"""pr_queue.py — `adk pr-queue` subcommands.

list                — print the queue as a compact table.
show <pr-url>       — dump a single entry as JSON.
add <url>           — single-shot upsert. URL may be a PR link (direct insert
                      after cheap meta-fetch), a Slack permalink (fetch that
                      message + replies, walk for PR links, upsert each), or
                      a bare PR number that resolves against
                      ~/.agents-devkit/config/core.yaml's defaults.repo (with
                      defaults.platform, default "github").
update <pr-url>     — refresh head_sha + merged-state on one row (cheap meta
                      only — does not trigger a review).
clean               — drop rows whose status == merged (and their task folders).
clean --all -y      — drop EVERY row + every task folder (requires --yes).
ready-to-merge      — list approved PRs grouped by open-comment state.
release <pr-url>    — clear `taken_at` on a row (manual lock release).

Every subcommand accepts `-y` / `--yes` for non-interactive use (no confirms;
smart defaults).

The queue lives at ~/.agents-devkit/config/pr-queue.json5 by default; override
with `--queue <path>`.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import parse_pr_url, task_dir_for, die, get_logger  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH,
    read_queue, write_queue, update_pr_entry, find_row, merge_scan_results,
    classify_pr_state, acquire_next_row,
    STATUS_APPROVED, STATUS_COMMENTS, STATUS_MERGED, STATUS_CLOSED,
    STATUS_PENDING, STATUS_IN_REVIEW,
    TERMINAL_STATUSES, TAKEN_LOCK_MAX_AGE_SECONDS, _now_iso,
)


def _load_defaults() -> dict:
    """Return the `defaults` block from ~/.agents-devkit/config/core.yaml,
    or {} if the file or block is absent. Only the `defaults` key is
    retained — every other top-level key is discarded so we never bring
    unrelated config (which may contain tokens, paths, or other state)
    into call sites. Per constitution §VII.

    Resolves $ADK_HOME / $HOME freshly on every call so tests that
    monkeypatch the env see the new path. Don't go through
    `config_io.load_core` here — its CORE_YAML constant is bound at
    import time and won't pick up a later HOME override.
    """
    import os
    try:
        home = Path(os.environ.get("ADK_HOME") or (Path.home() / ".agents-devkit"))
        if os.environ.get("ADK_HOME") is None and os.environ.get("HOME"):
            home = Path(os.environ["HOME"]) / ".agents-devkit"
        core = home / "config" / "core.yaml"
        if not core.exists():
            return {}
        import yaml  # noqa: WPS433 — lazy
        cfg = yaml.safe_load(core.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    defaults = cfg.get("defaults")
    if not isinstance(defaults, dict):
        return {}
    return defaults


def _task_dir_for_link(pr_url: str) -> Path | None:
    try:
        p = parse_pr_url(pr_url)
    except ValueError:
        return None
    return task_dir_for(p["repo"], p["pr_number"])


def _short_status(entry: dict) -> str:
    s = entry.get("status") or STATUS_PENDING
    if entry.get("taken_at"):
        return f"{s} (taken)"
    return s


# ----- list ----------------------------------------------------------------

def cmd_list(args) -> int:
    queue_path = Path(args.queue).expanduser()
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    if args.status:
        prs = [e for e in prs if (e.get("status") or STATUS_PENDING) == args.status]
    if args.urls_only:
        for e in prs:
            link = e.get("pr_url")
            if link:
                print(link)
        return 0
    if not prs:
        print("(queue empty)" if not args.status else f"(no entries with status={args.status})")
        return 0

    rows = []
    for e in prs:
        rows.append((
            _short_status(e),
            (e.get("last_checked_at") or "-")[:19],
            e.get("pr_url") or "",
        ))
    w_status = max(len(r[0]) for r in rows + [("status", "", "")])
    w_lc = max(len(r[1]) for r in rows + [("", "last_checked_at", "")])
    print(f"{'status'.ljust(w_status)}  {'last_checked_at'.ljust(w_lc)}  pr_url")
    print(f"{'-' * w_status}  {'-' * w_lc}  -")
    for r in rows:
        print(f"{r[0].ljust(w_status)}  {r[1].ljust(w_lc)}  {r[2]}")
    print(f"\n{len(rows)} entr{'y' if len(rows) == 1 else 'ies'}  ·  queue: {queue_path}")
    return 0


# ----- show ----------------------------------------------------------------

def cmd_show(args) -> int:
    queue_path = Path(args.queue).expanduser()
    entry = find_row(queue_path, args.pr_url)
    if entry is None:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return 0


# ----- clean ---------------------------------------------------------------

def _row_age_days(entry: dict) -> float | None:
    """Days since the row's last_checked_at. None if not parseable."""
    raw = entry.get("last_checked_at") or ""
    if not raw:
        return None
    try:
        from datetime import datetime, timezone
        s = raw[:-1] if raw.endswith("Z") else raw
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds() / 86400.0
    except Exception:
        return None


def cmd_clean(args) -> int:
    queue_path = Path(args.queue).expanduser()
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    if not prs:
        print("(queue empty)")
        return 0

    if args.all:
        to_drop = list(prs)
        action = f"drop ALL {len(to_drop)} entries + their task folders"
    elif args.stale_days is not None:
        # Sweep rows older than N days, not currently locked, not in_review.
        # Improvement #10 (worktree disk pressure).
        if args.stale_days < 1:
            print(f"--stale-days must be >= 1 (got {args.stale_days})")
            return 2
        to_drop = []
        for e in prs:
            if (e.get("status") or "") == STATUS_IN_REVIEW:
                continue
            if e.get("taken_at"):
                continue  # actively locked
            age = _row_age_days(e)
            if age is not None and age >= args.stale_days:
                to_drop.append(e)
        if not to_drop:
            print(f"(no rows older than {args.stale_days} days to clean)")
            return 0
        action = (f"drop {len(to_drop)} stale entr"
                  f"{'y' if len(to_drop) == 1 else 'ies'} "
                  f"(last_checked_at >= {args.stale_days} days ago) + their task folders")
    else:
        # Default sweep: both terminal states (merged + closed). Together they
        # cover everything the origin API has confirmed will not move again.
        to_drop = [e for e in prs if (e.get("status") or "") in TERMINAL_STATUSES]
        if not to_drop:
            print("(no merged or closed entries to clean)")
            return 0
        kinds = sorted({e.get("status") for e in to_drop})
        action = (f"drop {len(to_drop)} {'/'.join(kinds)} entr"
                  f"{'y' if len(to_drop) == 1 else 'ies'} + their task folders")

    if args.all and not args.yes:
        print(f"About to {action}. This is irreversible.")
        print("Re-run with --yes to confirm, or remove --all to drop only merged rows.")
        return 2
    if args.stale_days is not None and not args.yes:
        print(f"About to {action}. This is irreversible.")
        print(f"Re-run with --yes to confirm.")
        return 2

    dropped_urls: list[str] = []
    removed_dirs: list[str] = []
    failed_dirs: list[str] = []
    for e in to_drop:
        link = e.get("pr_url") or ""
        dropped_urls.append(link)
        td = _task_dir_for_link(link)
        if td and td.exists():
            try:
                shutil.rmtree(td)
                removed_dirs.append(str(td))
            except OSError as exc:
                failed_dirs.append(f"{td}: {exc}")

    dropped_keys = {id(e) for e in to_drop}
    queue["prs"] = [e for e in prs if id(e) not in dropped_keys]
    write_queue(queue_path, queue)

    print(json.dumps({
        "dropped_rows": len(dropped_urls),
        "removed_task_dirs": len(removed_dirs),
        "failed_task_dirs": failed_dirs,
        "queue": str(queue_path),
    }, indent=2))
    return 0


# ----- ready-to-merge ------------------------------------------------------

def cmd_ready_to_merge(args) -> int:
    queue_path = Path(args.queue).expanduser()
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    print_summary(prs)
    return 0


def print_summary(prs: list[dict]) -> None:
    """Print the ready-to-merge summary. Three buckets — distinguishing
    host-approved-with-comments from reviewed-but-not-approved.

      - Approved (no open comments)     status=APPROVED                  → merge-ready
      - Approved (open comments)        status=COMMENTS + approved_host  → merge-pending-resolution
      - Reviewed (open comments)        status=COMMENTS + !approved_host → not merge-ready yet

    The third bucket was previously rolled into "Approved (open comments)",
    which mislabeled review-only rows as approved. The fix needs the row to
    carry `approved_host` (persisted by `release_after_review`).
    """
    approved_clean = [e for e in prs if (e.get("status") or "") == STATUS_APPROVED]
    comments = [e for e in prs if (e.get("status") or "") == STATUS_COMMENTS]
    approved_with_comments = [e for e in comments if e.get("approved_host")]
    reviewed_with_comments = [e for e in comments if not e.get("approved_host")]

    if not approved_clean and not approved_with_comments and not reviewed_with_comments:
        print("Ready to merge: none.")
        return

    print("Ready to merge")
    print("==============")
    print(f"Approved (no open comments)   · {len(approved_clean)}")
    for e in approved_clean:
        print(f"  - {e.get('pr_url')}")
    print()
    print(f"Approved (open comments)      · {len(approved_with_comments)}")
    for e in approved_with_comments:
        print(f"  - {e.get('pr_url')}")
    print()
    print(f"Reviewed (open comments)      · {len(reviewed_with_comments)}")
    for e in reviewed_with_comments:
        print(f"  - {e.get('pr_url')}")


# ----- add (single-shot upsert from PR URL or Slack permalink) -------------

_SLACK_PERMALINK_RE = re.compile(
    r"https?://(?P<workspace>[a-zA-Z0-9_\-]+)\.slack\.com/archives/(?P<channel>[CG][A-Z0-9]+)/p(?P<ts>\d+)",
    re.I,
)


def _parse_slack_permalink(url: str) -> dict | None:
    """Return {workspace, channel_id, message_ts, thread_ts?} or None.

    Slack permalinks use `p<unix-ts><micros>` where the last 6 digits are the
    microsecond portion; we split at position-6-from-right to recover the
    decimal ts the API expects.
    """
    m = _SLACK_PERMALINK_RE.search(url)
    if not m:
        return None
    raw_ts = m.group("ts")
    if len(raw_ts) < 7:
        return None
    message_ts = raw_ts[:-6] + "." + raw_ts[-6:]
    parsed = {
        "workspace": m.group("workspace"),
        "channel_id": m.group("channel"),
        "message_ts": message_ts,
    }
    # Optional ?thread_ts=… in the query string.
    thread_match = re.search(r"[?&]thread_ts=(\d+\.\d+)", url)
    if thread_match:
        parsed["thread_ts"] = thread_match.group(1)
    return parsed


def _looks_like_pr_url(url: str) -> bool:
    try:
        parse_pr_url(url)
        return True
    except ValueError:
        return False


_BARE_PR_NUMBER_RE = re.compile(r"^#?(\d+)$")


def _resolve_bare_pr_number(token: str) -> str | None:
    """If `token` is a bare PR number (e.g. `1234` or `#1234`), expand it to
    a full PR URL using `defaults.platform` + `defaults.repo` from
    ~/.agents-devkit/config/core.yaml. Returns None if `token` is not a
    bare-number form. Raises SystemExit (via `die`) on configuration errors
    so the caller surfaces a clear actionable message.
    """
    m = _BARE_PR_NUMBER_RE.match(token)
    if not m:
        return None
    n = int(m.group(1))
    if n <= 0:
        die(f"bare PR number must be positive (got {n}).")
    defaults = _load_defaults()
    repo = defaults.get("repo")
    if not repo:
        die(
            "bare PR number requires defaults.repo in "
            "~/.agents-devkit/config/core.yaml. Example: "
            "defaults: { platform: github, repo: acme/storefront-bff }. "
            "Or pass a full URL."
        )
    platform = (defaults.get("platform") or "github").lower()
    if platform == "github":
        return f"https://github.com/{repo}/pull/{n}"
    if platform == "bitbucket":
        return f"https://bitbucket.org/{repo}/pull-requests/{n}"
    die(
        f"defaults.platform={platform!r} not supported. "
        "Allowed: github, bitbucket."
    )
    return None  # unreachable


def cmd_add(args) -> int:
    """Add a single PR to the queue, by direct PR URL, by Slack permalink,
    or by bare PR number (resolves against core.yaml defaults.repo)."""
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-add")
    url = args.url.strip()

    # Bare PR number form (`adk pr-queue add 1234` or `... add #1234`):
    # resolve against `defaults.platform` + `defaults.repo` from core.yaml.
    bare_resolved = _resolve_bare_pr_number(url)
    if bare_resolved is not None:
        log.info("resolved bare PR number %s → %s", url, bare_resolved)
        return _add_from_pr_url(bare_resolved, queue_path, args, log)

    if _looks_like_pr_url(url):
        return _add_from_pr_url(url, queue_path, args, log)

    slack_info = _parse_slack_permalink(url)
    if slack_info is not None:
        return _add_from_slack_permalink(url, slack_info, queue_path, args, log)

    die(
        f"unrecognized URL: {url}\n"
        "Expected a PR URL (github.com/<owner>/<repo>/pull/<n> or "
        "bitbucket.org/<ws>/<repo>/pull-requests/<n>), a Slack permalink "
        "(https://<workspace>.slack.com/archives/<channel>/p<ts>), or a "
        "bare PR number (uses core.yaml defaults.repo)."
    )
    return 1  # unreachable


def _add_from_pr_url(pr_url: str, queue_path: Path, args, log) -> int:
    """Direct insert. Cheap meta-fetch via `gh pr view` / bb REST, then upsert."""
    # Lazy import — pr_scan owns cheap_pr_meta.
    from pr_scan import cheap_pr_meta  # type: ignore[import-not-found]
    meta = cheap_pr_meta(pr_url, log)
    if "error" in meta:
        die(f"meta-fetch for {pr_url} failed: {meta['error']}")
    if meta.get("merged_at"):
        log.info("%s is already merged; status=merged on insert", pr_url)
    candidate = {
        "pr_url": pr_url,
        "status": STATUS_MERGED if meta.get("merged_at") else STATUS_PENDING,
        "supporting_docs": [],
    }
    existing = read_queue(queue_path)
    if find_row(queue_path, pr_url) is not None and not args.yes:
        print(f"{pr_url} already in queue. Re-run with -y to refresh in place.")
        return 2
    merged = merge_scan_results(existing, [candidate])
    merged.pop("_merge_summary", None)
    write_queue(queue_path, merged)
    print(json.dumps({"added": pr_url, "status": candidate["status"],
                      "queue": str(queue_path)}, indent=2))
    return 0


def _add_from_slack_permalink(url: str, slack_info: dict, queue_path: Path, args, log) -> int:
    """Fetch the slack message + its replies, walk for PR links, upsert each."""
    from slack_helpers import SlackClient, find_pr_urls  # type: ignore[import-not-found]
    from pr_scan import (  # type: ignore[import-not-found]
        post_process, find_supporting_docs, _slack_for,
    )
    from queue_io import load_slack_config  # type: ignore[import-not-found]

    slack_cfg = load_slack_config(None)
    url_patterns = slack_cfg.get("url_patterns") or []
    if not url_patterns:
        die("slack config has no url_patterns — cannot identify PR links.")

    client = SlackClient()
    cid = slack_info["channel_id"]
    msg_ts = slack_info["message_ts"]

    # Fetch the message via conversations.history(latest=ts, oldest=ts-epsilon, inclusive=True).
    # Easier: iter_thread_replies with thread_ts == this msg_ts often returns the parent.
    thread_ts = slack_info.get("thread_ts") or msg_ts
    main: dict | None = None
    replies: list[dict] = []
    for m in client.iter_thread_replies(cid, thread_ts):
        if m.get("ts") == thread_ts:
            main = m
        else:
            replies.append(m)
    # If the permalink pointed at a REPLY (not the thread root), build candidates around it.
    if main is None or thread_ts == msg_ts:
        pass  # main is the root
    elif msg_ts != thread_ts:
        log.info("permalink targets a reply (ts=%s) within thread ts=%s", msg_ts, thread_ts)

    if main is None:
        die(f"could not fetch slack message at {url}. Wrong channel id / message no longer exists?")

    main_text = main.get("text") or ""
    main_prs = find_pr_urls(main_text, url_patterns)
    all_text = main_text + "\n" + "\n".join((r.get("text") or "") for r in replies)
    supporting = find_supporting_docs(all_text)

    candidates: list[dict] = []
    main_permalink = client.get_message_permalink(cid, thread_ts)
    for pr_url in main_prs:
        candidates.append({
            "pr_url": pr_url,
            "supporting_docs": supporting,
            "slack": _slack_for(
                pr_url, channel_id=cid, message_ts=thread_ts, thread_ts=thread_ts,
                thread_starter_user_id=main.get("user"), link_origin="main",
                n_pr_links_in_message=len(main_prs), permalink=main_permalink,
            ),
        })
    for rep in replies:
        rep_text = rep.get("text") or ""
        rep_prs = find_pr_urls(rep_text, url_patterns)
        if not rep_prs:
            continue
        rep_ts = rep.get("ts")
        rep_permalink = client.get_message_permalink(cid, rep_ts)
        for pr_url in rep_prs:
            candidates.append({
                "pr_url": pr_url,
                "supporting_docs": supporting,
                "slack": _slack_for(
                    pr_url, channel_id=cid, message_ts=rep_ts, thread_ts=thread_ts,
                    thread_starter_user_id=main.get("user"), link_origin="reply",
                    n_pr_links_in_message=len(rep_prs), permalink=rep_permalink,
                ),
            })

    if not candidates:
        die(f"no PR links found in slack thread at {url}.")

    # Post-process: cheap meta, react-on-merged, drop merged.
    kept, post_stats = post_process(candidates, slack_cfg, dry_run=False, log=log)
    existing = read_queue(queue_path)
    merged = merge_scan_results(existing, kept)
    summary = merged.pop("_merge_summary", {})
    write_queue(queue_path, merged)
    print(json.dumps({
        "permalink": url,
        "candidates_found": len(candidates),
        "post_process": post_stats,
        "merge": summary,
        "queue": str(queue_path),
    }, indent=2))
    return 0


# ----- update (cheap meta refresh on one row) ------------------------------

def _refresh_one(pr_url: str, entry: dict, *, queue_path: Path, log) -> dict:
    """Refresh one PR's metadata only (head_sha + merged/closed state).

    Strict single-purpose: this verb does NOT touch the worktree or the
    index. If you also want to pre-warm the task folder, run
    `adk pr-task prepare <url>` afterwards (or just `adk pr-sync`, which
    chains both).

    Never raises — failures are folded into the returned dict so the `--all`
    caller can keep going.
    """
    from pr_scan import cheap_pr_meta  # type: ignore[import-not-found]
    try:
        meta = cheap_pr_meta(pr_url, log)
    except Exception as e:
        return {"pr_url": pr_url, "status": "failed", "stage": "meta", "reason": str(e)}
    if "error" in meta:
        return {"pr_url": pr_url, "status": "failed", "stage": "meta", "reason": meta["error"]}

    updates = {"last_checked_at": _now_iso()}
    new_head = meta.get("head_sha")
    if new_head:
        updates["head_sha"] = new_head
    # Capture target_branch (baseRefName / destination.branch.name). Skills
    # downstream — pr-sync's base-index audit, /adk-pr-review's seed-picker —
    # rely on this to map a PR to its base index.
    target_branch = meta.get("target_branch")
    if target_branch:
        updates["target_branch"] = target_branch
    # Origin-API is the source of truth for terminal state. classify_pr_state
    # interprets the host-specific quirks (GitHub CLOSED-without-merge ↔
    # Bitbucket DECLINED / SUPERSEDED) uniformly.
    verdict = classify_pr_state(meta)
    if verdict == "merged":
        updates["status"] = STATUS_MERGED
    elif verdict == "closed":
        updates["status"] = STATUS_CLOSED
    update_pr_entry(queue_path, pr_url, updates)
    prev_head = entry.get("head_sha")
    head_unchanged = (prev_head == new_head) if prev_head else None
    return {
        "pr_url": pr_url,
        "head_sha": new_head,
        "verdict": verdict,
        "merged": verdict == "merged",
        "closed": verdict == "closed",
        "status": updates.get("status", entry.get("status")),
        "head_unchanged": head_unchanged,
        "refreshed": "meta",
    }


def cmd_update(args) -> int:
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-update")

    if args.all:
        if args.pr_url:
            die("pass either <pr-url> or --all, not both")
        queue = read_queue(queue_path)
        prs = queue.get("prs", []) or []
        candidates = [e for e in prs
                      if (e.get("status") or STATUS_PENDING) not in TERMINAL_STATUSES]
        if not candidates:
            print(json.dumps({"updated": [],
                              "reason": "no rows to refresh (all merged or closed)"},
                             indent=2))
            return 0
        log.info("refreshing %d row(s) (metadata only)", len(candidates))
        results: list[dict] = []
        had_failure = False
        for e in candidates:
            url = e.get("pr_url")
            if not url:
                continue
            r = _refresh_one(url, e, queue_path=queue_path, log=log)
            if r.get("status") == "failed":
                had_failure = True
            results.append(r)
        print(json.dumps({"updated": results, "count": len(results)},
                         indent=2, default=str))
        return 1 if had_failure else 0

    if not args.pr_url:
        die("missing <pr-url>. Pass a URL or `--all`. "
            "List rows with `adk pr-queue list`.")
    entry = find_row(queue_path, args.pr_url)
    if entry is None:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    result = _refresh_one(args.pr_url, entry, queue_path=queue_path, log=log)
    print(json.dumps(result, indent=2))
    return 1 if result.get("status") == "failed" else 0


# ----- get-next ------------------------------------------------------------

def _drop_terminal_row(queue_path: Path, pr_url: str, status: str, log) -> None:
    """Remove a row whose origin-API check says it's merged or closed.

    Idempotent: re-running on an already-removed row is a no-op. Also cleans
    the row's on-disk task folder so `pr-task list` stays in sync.
    """
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    kept = [e for e in prs if e.get("pr_url") != pr_url]
    if len(kept) == len(prs):
        return
    queue["prs"] = kept
    write_queue(queue_path, queue)

    td = _task_dir_for_link(pr_url)
    if td and td.exists():
        try:
            shutil.rmtree(td)
        except OSError as e:
            log.warning("failed to remove task folder %s: %s", td, e)
    log.info("auto-dropped %s row %s + task folder", status, pr_url)


def get_next_eligible(queue_path: Path, *, validate: bool = True,
                      max_attempts: int = 10, log=None) -> dict | None:
    """Atomically claim the next eligible row, validating against the origin
    API. Rows that turn out to be merged or closed since the last sync are
    dropped from the queue (along with their on-disk task folder) and the
    picker tries the next candidate. Returns the claimed row, or None.

    `validate=False` skips the origin-API check — used by tests and by
    callers who already validated separately. The CLI front-end
    (`adk pr-queue get-next`) and `prepare_task.py` queue mode use
    `validate=True`.
    """
    if log is None:
        log = get_logger("pr-queue-get-next")
    from pr_scan import cheap_pr_meta  # type: ignore[import-not-found]

    attempts = 0
    while attempts < max_attempts:
        attempts += 1
        candidate = acquire_next_row(queue_path)
        if candidate is None:
            return None
        if not validate:
            return candidate

        pr_url = candidate.get("pr_url")
        if not pr_url:
            return candidate
        meta = cheap_pr_meta(pr_url, log)
        verdict = classify_pr_state(meta)
        if verdict in {"merged", "closed"}:
            # Release the claim we just took, then drop the row entirely.
            update_pr_entry(queue_path, pr_url, {"taken_at": None})
            _drop_terminal_row(queue_path, pr_url, verdict, log)
            continue
        # Refresh head_sha so the row reflects the API's current view, then
        # return the (still-claimed) candidate.
        new_head = meta.get("head_sha") if not meta.get("error") else None
        if new_head and new_head != candidate.get("head_sha"):
            update_pr_entry(queue_path, pr_url,
                            {"head_sha": new_head, "last_checked_at": _now_iso()})
            candidate["head_sha"] = new_head
        return candidate
    log.warning("get_next_eligible: exhausted %d attempts; queue may be all-terminal",
                max_attempts)
    return None


def _cmd_remind(args) -> int:
    """Thin wrapper so the standalone `pr_reminders.main` and the
    `pr-queue remind` subcommand share one implementation."""
    from pr_reminders import send_reminders  # type: ignore[import-not-found]
    out = send_reminders(
        Path(args.queue).expanduser(),
        threshold_hours=args.threshold_hours,
        dry_run=args.dry_run,
    )
    print(json.dumps(out, indent=2, default=str))
    return 1 if out.get("failed") else 0


def cmd_get_next(args) -> int:
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-get-next")
    row = get_next_eligible(queue_path, validate=not args.no_validate, log=log)
    if row is None:
        print(json.dumps({"action": "queue_empty",
                          "queue": str(queue_path),
                          "message": "no eligible rows. Run `adk pr-sync` to refresh."},
                         indent=2))
        return 0
    out = {
        "action": "claimed",
        "pr_url": row.get("pr_url"),
        "head_sha": row.get("head_sha"),
        "status": row.get("status"),
        "slack": row.get("slack"),
        "supporting_docs": row.get("supporting_docs") or [],
        "taken_at": row.get("taken_at"),
    }
    print(json.dumps(out, indent=2, default=str))
    return 0


# ----- claim / heartbeat / release / set-status (v4 §6.v lock handling) ----

def cmd_claim(args) -> int:
    """v4 §6.v: atomically set taken_at + status=in_review for one PR.

    Fails (rc=2) if the row is already locked AND --force is not set.
    Returns the claimed row as JSON on success.
    """
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-claim")
    entry = find_row(queue_path, args.pr_url)
    if entry is None:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    from datetime import datetime, timezone
    now = datetime.now(tz=timezone.utc)
    # Check lock — only --force bypasses an ACTIVE lock (§6.u rule 2 still
    # protects from breaking an active reviewer).
    from queue_io import _is_locked, _now_iso, STATUS_IN_REVIEW
    if _is_locked(entry, now) and not args.force:
        die(f"row is locked (taken_at={entry.get('taken_at')!r}); "
            f"another reviewer holds it. Re-run with --force only if you're sure.")
    # Even with --force, never break a TRULY fresh lock (within the last minute).
    if _is_locked(entry, now) and args.force:
        log.warning("--force overriding active lock on %s", args.pr_url)
    updates = {"taken_at": _now_iso()}
    # Don't downgrade status if it's already in_review / past it.
    cur = entry.get("status") or ""
    if cur in {"pending", "reviewed", "comments", "reminded", "error", ""}:
        updates["status"] = STATUS_IN_REVIEW
    update_pr_entry(queue_path, args.pr_url, updates)
    refreshed = find_row(queue_path, args.pr_url)
    print(json.dumps({"action": "claimed", "pr_url": args.pr_url,
                      "taken_at": refreshed.get("taken_at"),
                      "status": refreshed.get("status")}, indent=2))
    return 0


def cmd_heartbeat(args) -> int:
    """v4 §6.v: bump taken_at to now. Called by the agent every ~5 min during
    a long review so the lock doesn't expire mid-work.
    """
    queue_path = Path(args.queue).expanduser()
    from queue_io import _now_iso
    entry = find_row(queue_path, args.pr_url)
    if entry is None:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    if entry.get("taken_at") is None:
        die(f"row {args.pr_url} is not locked; cannot heartbeat. "
            f"Run `adk pr-queue claim` first.")
    update_pr_entry(queue_path, args.pr_url, {"taken_at": _now_iso()})
    print(json.dumps({"action": "heartbeat", "pr_url": args.pr_url,
                      "taken_at": _now_iso()}, indent=2))
    return 0


def cmd_set_status(args) -> int:
    """v4 §6.v: change the row's status without releasing the lock.

    Useful for mid-review transitions (e.g. → 'reviewed' after Phase 5 posts
    comments but before Phase 6 finalises). Doesn't touch taken_at.
    """
    queue_path = Path(args.queue).expanduser()
    ok = update_pr_entry(queue_path, args.pr_url, {"status": args.status})
    if not ok:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    print(json.dumps({"action": "set_status", "pr_url": args.pr_url,
                      "status": args.status}, indent=2))
    return 0


# ----- release -------------------------------------------------------------

def cmd_release(args) -> int:
    """v4 §6.v: clear taken_at. Optionally set a terminal status with --status."""
    queue_path = Path(args.queue).expanduser()
    updates = {"taken_at": None}
    status = getattr(args, "status", None)
    if status:
        updates["status"] = status
    ok = update_pr_entry(queue_path, args.pr_url, updates)
    if not ok:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    msg = f"released: {args.pr_url}"
    if status:
        msg += f" (status={status})"
    print(msg)
    return 0


# ----- entrypoint ---------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-queue",
                                 description="Inspect / manage the PR review queue.")
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to ~/.agents-devkit/logs/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_list = sub.add_parser("list", help="list queue entries")
    sp_list.add_argument("--status", help="filter by status (pending|in_review|reviewed|comments|approved|merged|closed|error|reminded)")
    sp_list.add_argument("--urls-only", action="store_true",
                          help="emit one PR URL per line (for shell completion)")
    sp_list.set_defaults(func=cmd_list)

    sp_show = sub.add_parser("show", help="show one entry as JSON")
    sp_show.add_argument("pr_url")
    sp_show.set_defaults(func=cmd_show)

    sp_add = sub.add_parser("add", help="add a PR by URL, Slack permalink, or bare PR number (uses core.yaml defaults.repo)")
    sp_add.add_argument("url")
    sp_add.add_argument("-y", "--yes", action="store_true",
                        help="non-interactive; refresh in place if already present")
    sp_add.set_defaults(func=cmd_add)

    sp_upd = sub.add_parser("update",
                            help="refresh row metadata (head_sha + merged/closed "
                                 "state via origin API). Single-purpose: does NOT "
                                 "touch the worktree or index — for that, run "
                                 "`adk pr-task prepare` or `adk pr-sync`.")
    sp_upd.add_argument("pr_url", nargs="?", default=None,
                        help="PR URL to refresh (omit when using --all)")
    sp_upd.add_argument("--all", action="store_true",
                        help="refresh every non-terminal row in the queue; "
                             "continues past per-row failures and exits 1 if any failed")
    sp_upd.add_argument("-y", "--yes", action="store_true")
    sp_upd.set_defaults(func=cmd_update)

    sp_clean = sub.add_parser("clean", help="drop merged rows (or --all, or --stale-days N)")
    sp_clean.add_argument("--all", action="store_true",
                          help="drop EVERY entry + task folder (requires --yes to confirm)")
    sp_clean.add_argument("--stale-days", type=int, default=None,
                          help="drop rows with last_checked_at >= N days ago "
                               "(skips in_review and currently-locked rows). Requires --yes.")
    sp_clean.add_argument("-y", "--yes", action="store_true",
                          help="confirm --all or --stale-days clean")
    sp_clean.set_defaults(func=cmd_clean)

    sp_rtm = sub.add_parser("ready-to-merge", help="list approved PRs grouped by comment state")
    sp_rtm.set_defaults(func=cmd_ready_to_merge)

    sp_get = sub.add_parser("get-next",
                            help="claim the next eligible PR for review "
                                 "(skips merged/declined/locked/already-reviewed; "
                                 "auto-drops rows the origin API says are terminal)")
    sp_get.add_argument("--no-validate", action="store_true",
                        help="skip origin-API validation; in-memory pick only")
    sp_get.set_defaults(func=cmd_get_next)

    sp_rel = sub.add_parser("release",
                            help="clear `taken_at` (optionally set a terminal status)")
    sp_rel.add_argument("pr_url")
    sp_rel.add_argument("--status", default=None,
                        help="optionally set the row's status while releasing "
                             "(e.g. 'reviewed', 'approved', 'comments')")
    sp_rel.set_defaults(func=cmd_release)

    sp_claim = sub.add_parser("claim",
                              help="v4 §6.v: atomically set taken_at + status=in_review")
    sp_claim.add_argument("pr_url")
    sp_claim.add_argument("--force", action="store_true",
                          help="override an active lock (use only if you're sure)")
    sp_claim.set_defaults(func=cmd_claim)

    sp_hb = sub.add_parser("heartbeat",
                           help="v4 §6.v: bump taken_at to now (call every ~5 min during a long review)")
    sp_hb.add_argument("pr_url")
    sp_hb.set_defaults(func=cmd_heartbeat)

    sp_ss = sub.add_parser("set-status",
                           help="v4 §6.v: change the row's status without releasing the lock")
    sp_ss.add_argument("pr_url")
    sp_ss.add_argument("status",
                       help="new status (pending|in_review|reviewed|comments|approved|merged|closed|error|reminded)")
    sp_ss.set_defaults(func=cmd_set_status)

    sp_rem = sub.add_parser("remind",
                            help="Slack-reply reminder for any PR reviewed "
                                 ">=24h ago with no new commits since")
    sp_rem.add_argument("--threshold-hours", type=float, default=24.0)
    sp_rem.add_argument("--dry-run", action="store_true")
    sp_rem.add_argument("-y", "--yes", action="store_true")
    sp_rem.set_defaults(func=lambda args: _cmd_remind(args))

    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-queue", enabled=True, argv=argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
