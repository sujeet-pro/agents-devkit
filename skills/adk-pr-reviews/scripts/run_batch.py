#!/usr/bin/env python3
"""run_batch.py — driver for /adk-pr-reviews (JSON5 queue + slack reactions + reminders).

Per-row flow:
  1. Acquire per-PR lock (fail fast if held).
  2. Cheap meta fetch — is it merged? what's head_oid?
  3. If merged → update queue entry status=merged, react with merged emoji
     (only if slack.n_pr_links_in_message == 1 and merged emoji configured), done.
  4. Decide:
       - new head_oid OR re_review_required → REVIEW
       - else → SKIP-STABLE
  5. SKIP-STABLE path:
       - bump last_checked_at
       - if reminder conditions met → post slack reply tagging author + thread_starter
  6. REVIEW path:
       - run_review.py (worktree + reindex + precis), forcing supporting_docs[] from the queue entry
       - claude -p (headless)
       - comment_resolver + post_comments (gated by per-invocation confirmation, which the
         user implicitly gave by invoking /adk-pr-reviews)
       - report.py
       - update queue entry: status, last_reviewed_head_oid, last_reviewed_at_utc,
         approved_no_comments, re_review_required
       - update slack reactions: remove last_reaction_status emoji, add new one per status_emoji

Modes:
  (default)  read queue, run reviews
  --scan     run scan_slack.py first, refresh queue from slack, THEN run reviews

Usage:
  python3 run_batch.py [queue-path] [--scan] [-p N | --parallelism N] [--dry-run] [--max-rows M]
                       [--slack-config <path>] [--since <days>]
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import os
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
SKILL_ROOT_PR_REVIEW = THIS_DIR.parent.parent / "adk-pr-review"
sys.path.insert(0, str(PR_REVIEW_SCRIPTS))
sys.path.insert(0, str(THIS_DIR))

from _common import (  # noqa: E402
    parse_pr_url, ensure_dirs, task_dir_for,
    pr_lock_for, try_file_lock, LockHeldError,
    read_state, write_state, read_json, write_json,
    get_logger, which, die,
)
from queue_io import (  # noqa: E402
    load_slack_config, read_queue, write_queue, update_pr_entry,
    STATUS_PENDING, STATUS_IN_REVIEW, STATUS_REVIEWED, STATUS_COMMENTS,
    STATUS_NEEDS_FIX,  # alias of STATUS_COMMENTS — kept importable for back-compat
    STATUS_APPROVED, STATUS_MERGED, STATUS_ERROR, STATUS_REMINDED,
    TERMINAL_OR_POSITIVE,
)

DEFAULT_QUEUE = Path.home() / ".agents-devkit" / "pr-reviews" / "queue.json5"
DEFAULT_SLACK_CONFIG = Path.home() / ".agents-devkit" / "config" / "connectors" / "slack.md"
PY = sys.executable


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(s: str | None):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


# ----------------------------- pre-flight ----------------------------------

def preflight(parallelism: int, queue_path: Path, log) -> None:
    if not which("claude"):
        die("claude CLI not on PATH. /adk-pr-reviews spawns `claude -p` per row.")
    if parallelism < 1 or parallelism > 16:
        die(f"--parallelism must be in [1, 16]; got {parallelism}")
    if not queue_path.exists():
        die(
            f"queue not found: {queue_path}. Either run with --scan to generate from slack, "
            f"or copy the template:\n"
            f"  cp {THIS_DIR.parent / 'templates' / 'queue.json5'} {queue_path}"
        )
    log.info("preflight: claude=%s, parallelism=%d, queue=%s", which("claude"), parallelism, queue_path)


# ----------------------------- cheap meta ----------------------------------

def cheap_pr_meta(pr_url: str, log) -> dict:
    """Same shape as scan_slack.cheap_pr_meta but local to avoid cross-import."""
    from scan_slack import cheap_pr_meta as _meta
    return _meta(pr_url, log)


# ----------------------------- review decision -----------------------------

def should_review(state: dict, current_head_oid: str) -> tuple[bool, str]:
    last = state.get("last_reviewed_head_oid")
    rer = bool(state.get("re_review_required", False))
    if last is None:
        return True, "no prior review"
    if last != current_head_oid:
        return True, f"new commit ({last[:8]} -> {current_head_oid[:8]})"
    if rer:
        return True, "re_review_required=true from last run"
    return False, "head_oid unchanged + no re-review pending"


# ----------------------------- slack reactions -----------------------------

def update_slack_reaction(slack_info: dict, new_status: str, slack_cfg: dict, log) -> dict:
    """Transition slack reaction.

    Normal transitions: remove `last_reaction_status` emoji, add the new one.
    Transitions to `approved` / `merged` (per `queue_io.TERMINAL_OR_POSITIVE`):
      sweep ALL other configured status emojis off the message — defensive
      cleanup in case a prior reaction wasn't tracked in `last_reaction_status`.
      The new status's emoji is the only one left.
    """
    status_emoji = slack_cfg.get("status_emoji") or {}
    new_emoji = status_emoji.get(new_status)
    last_status = slack_info.get("last_reaction_status")
    last_emoji = status_emoji.get(last_status) if last_status else None
    if not slack_info.get("channel_id") or not slack_info.get("message_ts"):
        return slack_info

    is_terminal_positive = new_status in TERMINAL_OR_POSITIVE

    # Idempotency shortcut: same emoji as last AND not a terminal sweep.
    if new_emoji == last_emoji and not is_terminal_positive:
        slack_info["last_reaction_status"] = new_status
        return slack_info

    from slack_helpers import SlackClient
    client = SlackClient()
    channel_id = slack_info["channel_id"]
    message_ts = slack_info["message_ts"]

    if is_terminal_positive:
        # Sweep every OTHER configured status emoji. Skip null entries + the new one.
        seen: set[str] = set()
        for st, em in status_emoji.items():
            if not em or em in seen or em == new_emoji:
                continue
            seen.add(em)
            client.remove_reaction(channel_id, message_ts, em)
        if log:
            log.info("slack: terminal transition to %s — swept other status emojis", new_status)
    else:
        if last_emoji and last_emoji != new_emoji:
            client.remove_reaction(channel_id, message_ts, last_emoji)

    if new_emoji:
        client.add_reaction(channel_id, message_ts, new_emoji)
    slack_info["last_reaction_status"] = new_status
    return slack_info


# ----------------------------- reminders -----------------------------------

def maybe_send_reminder(entry: dict, meta: dict, state: dict, slack_cfg: dict, log) -> bool:
    """Send a slack thread reply if conditions are met. Returns True if sent."""
    rem_cfg = slack_cfg.get("reminder") or {}
    if not rem_cfg.get("enabled"):
        return False
    slack_info = entry.get("slack") or {}
    if not (slack_info.get("channel_id") and slack_info.get("thread_ts")):
        return False
    if not state.get("re_review_required"):
        return False  # nothing to remind about
    after_hours = float(rem_cfg.get("after_hours", 24))
    min_between = float(rem_cfg.get("min_hours_between_reminders", 24))
    last_reviewed = _parse_iso(state.get("last_reviewed_at_utc"))
    if not last_reviewed:
        return False
    now = datetime.now(tz=timezone.utc)
    age_h = (now - last_reviewed).total_seconds() / 3600.0
    if age_h < after_hours:
        return False
    last_rem = _parse_iso(slack_info.get("last_reminder_at"))
    if last_rem and (now - last_rem).total_seconds() / 3600.0 < min_between:
        return False
    # Head must not have changed since last review (handled by caller — we're in skip-stable path).

    from slack_helpers import SlackClient
    client = SlackClient()

    # Build tag list.
    tag_tokens = rem_cfg.get("tag_users") or []
    mentions: list[str] = []
    for tok in tag_tokens:
        if tok == "author":
            author_id = client.resolve_user_token(meta.get("author") or "")
            if author_id:
                mentions.append(f"<@{author_id}>")
        elif tok == "thread_starter":
            ts_user = slack_info.get("thread_starter_user_id")
            if ts_user:
                mentions.append(f"<@{ts_user}>")
        else:
            uid = client.resolve_user_token(tok)
            if uid:
                mentions.append(f"<@{uid}>")

    template = rem_cfg.get(
        "message_template",
        "PR review pending — please address the {pending_findings} open comments above. cc {author} {thread_starter}",
    )
    pending_findings = state.get("last_n_findings", "open")
    author_tag = mentions[0] if "author" in tag_tokens and mentions else ""
    thread_starter_tag = ""
    if "thread_starter" in tag_tokens:
        ts_user = slack_info.get("thread_starter_user_id")
        if ts_user:
            thread_starter_tag = f"<@{ts_user}>"
    text = template.format(
        pending_findings=pending_findings,
        author=author_tag or "",
        thread_starter=thread_starter_tag or "",
        pr_link=entry.get("pr_link", ""),
    )
    # Append any extra mentions not already in the template-substituted result.
    extras = [m for m in mentions if m not in text]
    if extras:
        text = text.rstrip() + " " + " ".join(extras)

    posted = client.post_thread_reply(slack_info["channel_id"], slack_info["thread_ts"], text)
    if posted:
        slack_info["last_reminder_at"] = _now_iso()
        log.info("reminder posted (slack ts=%s) for %s", posted, entry["pr_link"])
        return True
    return False


# ----------------------------- per-row ------------------------------------

def run_step(cmd: list[str], log, env=None):
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    if cp.stdout:
        log.info("stdout:\n%s", cp.stdout.strip())
    if cp.stderr.strip():
        log.info("stderr:\n%s", cp.stderr.strip())
    if cp.returncode != 0:
        raise RuntimeError(f"step failed (rc={cp.returncode}): {' '.join(cmd)}")
    return cp


def run_claude_review(task_dir: Path, log) -> dict:
    skill_md = SKILL_ROOT_PR_REVIEW / "SKILL.md"
    schema = SKILL_ROOT_PR_REVIEW / "finding.template.json"
    precis = task_dir / "precis.md"
    if not precis.exists():
        raise RuntimeError(f"precis.md missing at {precis}")
    cmd = [
        "claude", "-p",
        "--bare",
        "--system-prompt", str(skill_md),
        "--add-dir", str(task_dir / "code"),
        "--allowedTools", "Read,Glob,Grep,Bash",
        "--permission-mode", "auto",
        "--json-schema", str(schema),
        "--output-format", "json",
    ]
    log.info("$ %s < precis.md", " ".join(cmd))
    started = time.time()
    cp = subprocess.run(cmd, input=precis.read_text(encoding="utf-8"),
                        capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - started
    if cp.returncode != 0:
        raise RuntimeError(f"claude -p failed (rc={cp.returncode}): {cp.stderr[:500]}")
    outer = json.loads(cp.stdout)
    findings = outer.get("structured_output") or outer.get("result")
    if not isinstance(findings, dict):
        raise RuntimeError(f"claude -p missing structured_output; head={cp.stdout[:400]}")
    write_json(task_dir / "findings.json", findings)
    log.info("claude -p ok (%.1fs, findings=%d)", elapsed, len(findings.get("findings", [])))
    return findings


def process_entry(entry: dict, queue_path: Path, slack_cfg: dict, dry_run: bool) -> dict[str, Any]:
    pr_link = entry.get("pr_link", "")
    summary: dict[str, Any] = {"pr_link": pr_link, "start_ts": _now_iso()}

    if "@" in pr_link.split("://", 1)[-1].split("/", 1)[0]:
        summary["status"] = "refused"
        summary["note"] = "URL embeds credentials"
        return summary

    try:
        parsed = parse_pr_url(pr_link)
    except ValueError as e:
        return _row_error(summary, queue_path, pr_link, "url", str(e), dry_run)

    host, owner, repo, n = parsed["host"], parsed["owner"], parsed["repo"], parsed["pr_number"]
    task_dir = task_dir_for(repo, n)
    summary.update({"host": host, "repo": repo, "pr_number": n})
    log = get_logger(f"batch.{repo}.{n}", task_dir)

    try:
        ctx = try_file_lock(pr_lock_for(repo, n), wait=False)
        ctx.__enter__()
    except LockHeldError as e:
        summary["status"] = "skipped-locked"
        summary["note"] = str(e).split("\n")[0]
        if not dry_run:
            update_pr_entry(queue_path, pr_link, {"last_checked_at": _now_iso()})
        return summary

    try:
        meta = cheap_pr_meta(pr_link, log)
        if "error" in meta:
            return _row_error(summary, queue_path, pr_link, log, dry_run, f"meta: {meta['error']}")
        summary["head_oid"] = meta.get("head_oid")
        summary["author"] = meta.get("author")

        # Merge short-circuit.
        if meta.get("merged_at"):
            updates = {"status": STATUS_MERGED, "last_checked_at": _now_iso()}
            slack_info = entry.get("slack") or {}
            if (slack_info.get("n_pr_links_in_message") == 1 and not dry_run):
                slack_info = update_slack_reaction(slack_info, STATUS_MERGED, slack_cfg, log)
                updates["slack"] = slack_info
            if not dry_run:
                update_pr_entry(queue_path, pr_link, updates)
                # Also update per-PR state.json so /adk-pr-review's own state agrees.
                st = read_state(task_dir)
                st["merged"] = True
                st["merged_at"] = meta["merged_at"]
                write_state(task_dir, st)
            summary["status"] = STATUS_MERGED
            summary["action"] = "skipped-merged"
            return summary

        st = read_state(task_dir)
        will_review, reason = should_review(st, meta.get("head_oid") or "")
        summary["decision"] = ("review" if will_review else "skip") + f": {reason}"

        if not will_review:
            # Skip-stable: bump last_checked + maybe send reminder.
            if not dry_run:
                slack_info = entry.get("slack") or {}
                sent = maybe_send_reminder(entry, meta, st, slack_cfg, log)
                updates = {"last_checked_at": _now_iso()}
                if sent:
                    updates["slack"] = slack_info  # last_reminder_at set by maybe_send_reminder
                    updates["status"] = STATUS_REMINDED
                else:
                    updates["status"] = entry.get("status", STATUS_PENDING) if entry.get("status") not in (None, STATUS_PENDING) else STATUS_REVIEWED
                update_pr_entry(queue_path, pr_link, updates)
                summary["reminder_sent"] = sent
            summary["status"] = "skipped-stable"
            summary["action"] = "skipped-stable" + (" + reminder" if summary.get("reminder_sent") else "")
            return summary

        if dry_run:
            summary["status"] = "would-review"
            return summary

        # --- Run the review ---
        env = os.environ.copy()
        env["ADK_PR_LOCK_HELD"] = "1"
        # Forced-input supporting docs: write them into a side-file the orchestrator
        # picks up before fetch_supporting_docs runs.
        if entry.get("supporting_docs"):
            task_dir.mkdir(parents=True, exist_ok=True)
            (task_dir / "forced-supporting-docs.json").write_text(
                json.dumps(entry["supporting_docs"], indent=2), encoding="utf-8")

        run_step([PY, str(PR_REVIEW_SCRIPTS / "run_review.py"), pr_link], log, env=env)

        # Set status=in_review BEFORE claude (so a parallel scan sees it).
        slack_info = entry.get("slack") or {}
        if slack_info.get("channel_id"):
            slack_info = update_slack_reaction(slack_info, STATUS_IN_REVIEW, slack_cfg, log)
        update_pr_entry(queue_path, pr_link, {"status": STATUS_IN_REVIEW, "slack": slack_info,
                                              "last_checked_at": _now_iso()})

        findings = run_claude_review(task_dir, log)

        run_step([PY, str(PR_REVIEW_SCRIPTS / "comment_resolver.py"),
                  "--task-dir", str(task_dir), "--json"], log)
        run_step([PY, str(PR_REVIEW_SCRIPTS / "post_comments.py"),
                  "--task-dir", str(task_dir), "--confirmed", "yes", "--json"], log)
        run_step([PY, str(PR_REVIEW_SCRIPTS / "report.py"),
                  "--task-dir", str(task_dir)], log)

        # Persist outcome. Status decision:
        #   findings > 0           → comments      (was needs_fix; renamed)
        #   findings == 0 + approved → approved    (recommendation:approve OR host APPROVED)
        #   findings == 0 + !approved → reviewed   (clean review, no host approval yet)
        n_findings = len(findings.get("findings", []))
        approved = (meta.get("reviewDecision") == "APPROVED" or
                    findings.get("recommendation") == "approve")
        re_review = (n_findings > 0)
        if re_review:
            new_status = STATUS_COMMENTS
        elif approved:
            new_status = STATUS_APPROVED
        else:
            new_status = STATUS_REVIEWED

        st = read_state(task_dir)
        st["last_reviewed_head_oid"] = meta.get("head_oid")
        st["last_reviewed_at_utc"] = _now_iso()
        st["approved_no_comments"] = bool(approved and n_findings == 0)
        st["re_review_required"] = re_review
        st["last_n_findings"] = n_findings
        write_state(task_dir, st)

        if slack_info.get("channel_id"):
            slack_info = update_slack_reaction(slack_info, new_status, slack_cfg, log)

        update_pr_entry(queue_path, pr_link, {
            "status": new_status,
            "last_checked_at": _now_iso(),
            "slack": slack_info,
        })

        summary["status"] = new_status
        summary["action"] = "reviewed"
        summary["n_findings"] = n_findings
        summary["re_review_required"] = re_review
        return summary

    except Exception as e:
        return _row_error(summary, queue_path, pr_link, log, dry_run, str(e), tb=traceback.format_exc())
    finally:
        try:
            ctx.__exit__(None, None, None)  # type: ignore[has-type]
        except Exception:
            pass


def _row_error(summary: dict, queue_path: Path, pr_link: str, log, dry_run: bool,
               message: str, tb: str | None = None) -> dict:
    log.error("row error: %s", message)
    if tb:
        log.error("traceback:\n%s", tb)
    short = message.replace("\n", " ")[:200]
    summary["status"] = STATUS_ERROR
    summary["note"] = short
    if not dry_run:
        try:
            update_pr_entry(queue_path, pr_link,
                            {"status": STATUS_ERROR, "last_checked_at": _now_iso(),
                             "notes": short})
        except Exception:
            pass
    return summary


# ----------------------------- main ----------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("queue_path", nargs="?", default=None,
                    help=f"path to queue.json5 (default: {DEFAULT_QUEUE})")
    ap.add_argument("-p", "--parallelism", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--scan", action="store_true",
                    help="run scan_slack.py first to refresh the queue from configured slack channels")
    ap.add_argument("--slack-config", default=str(DEFAULT_SLACK_CONFIG))
    ap.add_argument("--since", type=int, default=0,
                    help="(with --scan) days back to scan; 0 = use slack.json5 default")
    args = ap.parse_args()

    ensure_dirs()
    queue_path = Path(args.queue_path).expanduser() if args.queue_path else DEFAULT_QUEUE
    slack_cfg_path = Path(args.slack_config).expanduser()
    log = get_logger("batch")

    # --scan: refresh the queue before running.
    if args.scan:
        cmd = [PY, str(THIS_DIR / "scan_slack.py"),
               "--slack-config", str(slack_cfg_path),
               "--queue", str(queue_path)]
        if args.since:
            cmd += ["--since", str(args.since)]
        if args.dry_run:
            cmd += ["--dry-run"]
        log.info("running --scan: %s", " ".join(cmd))
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
        sys.stderr.write(cp.stderr)
        sys.stdout.write(cp.stdout)
        if cp.returncode != 0:
            die(f"scan_slack.py failed (rc={cp.returncode})")

    preflight(args.parallelism, queue_path, log)

    try:
        slack_cfg = load_slack_config(slack_cfg_path)
    except FileNotFoundError as e:
        log.warning("%s — slack reactions + reminders will be skipped", e)
        slack_cfg = {}

    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    log.info("loaded %d entries from %s", len(prs), queue_path)

    actionable: list[dict] = []
    skipped_merged = 0
    refused = 0
    for e in prs:
        if e.get("status") == STATUS_MERGED:
            skipped_merged += 1
            continue
        try:
            parse_pr_url(e.get("pr_link", ""))
        except ValueError:
            refused += 1
            continue
        actionable.append(e)

    if args.max_rows and len(actionable) > args.max_rows:
        log.info("--max-rows=%d: capping from %d to %d", args.max_rows, len(actionable), args.max_rows)
        actionable = actionable[:args.max_rows]

    print(f"\n=== /adk-pr-reviews — {queue_path} ===")
    print(f"  actionable: {len(actionable)} · merged-skip: {skipped_merged} · refused: {refused}")
    print(f"  parallelism: {args.parallelism} · scan: {args.scan} · dry-run: {args.dry_run}")
    print()

    if not actionable:
        print("nothing to do.")
        return 0

    results: list[dict[str, Any]] = []
    if args.parallelism == 1:
        for e in actionable:
            results.append(process_entry(e, queue_path, slack_cfg, args.dry_run))
    else:
        with cf.ThreadPoolExecutor(max_workers=args.parallelism) as ex:
            futs = {ex.submit(process_entry, e, queue_path, slack_cfg, args.dry_run): e
                    for e in actionable}
            for fut in cf.as_completed(futs):
                results.append(fut.result())

    print("\n=== per-row results ===")
    for s in results:
        line = f"  {s.get('pr_link')} → {s.get('status')}"
        if s.get("action"):
            line += f"  [{s['action']}]"
        if s.get("n_findings") is not None:
            line += f"  findings={s['n_findings']}"
        if s.get("reminder_sent"):
            line += "  +reminder"
        if s.get("note"):
            line += f"  ({s['note']})"
        print(line)

    n_err = sum(1 for s in results if s.get("status") == STATUS_ERROR)
    return 0 if n_err == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
