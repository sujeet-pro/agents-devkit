"""pr_queue.py — `adk pr-queue` subcommands.

list                — print the queue as a compact table.
show <pr-url>       — dump a single entry as JSON.
add <url>           — single-shot upsert. URL may be a PR link (direct insert
                      after cheap meta-fetch) OR a Slack permalink (fetch that
                      message + replies, walk for PR links, upsert each).
update <pr-url>     — refresh head_oid + merged-state on one row (cheap meta
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
    STATUS_APPROVED, STATUS_COMMENTS, STATUS_MERGED, STATUS_PENDING,
    TAKEN_LOCK_MAX_AGE_SECONDS, _now_iso,
)


def _task_dir_for_link(pr_link: str) -> Path | None:
    try:
        p = parse_pr_url(pr_link)
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
    if not prs:
        print("(queue empty)" if not args.status else f"(no entries with status={args.status})")
        return 0

    rows = []
    for e in prs:
        rows.append((
            _short_status(e),
            (e.get("last_checked_at") or "-")[:19],
            e.get("pr_link") or "",
        ))
    w_status = max(len(r[0]) for r in rows + [("status", "", "")])
    w_lc = max(len(r[1]) for r in rows + [("", "last_checked_at", "")])
    print(f"{'status'.ljust(w_status)}  {'last_checked_at'.ljust(w_lc)}  pr_link")
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
    else:
        to_drop = [e for e in prs if (e.get("status") or "") == STATUS_MERGED]
        if not to_drop:
            print("(no merged entries to clean)")
            return 0
        action = f"drop {len(to_drop)} merged entr{'y' if len(to_drop) == 1 else 'ies'} + their task folders"

    if args.all and not args.yes:
        print(f"About to {action}. This is irreversible.")
        print("Re-run with --yes to confirm, or remove --all to drop only merged rows.")
        return 2

    dropped_links: list[str] = []
    removed_dirs: list[str] = []
    failed_dirs: list[str] = []
    for e in to_drop:
        link = e.get("pr_link") or ""
        dropped_links.append(link)
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
        "dropped_rows": len(dropped_links),
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
        print(f"  - {e.get('pr_link')}")
    print()
    print(f"Approved (open comments)      · {len(approved_with_comments)}")
    for e in approved_with_comments:
        print(f"  - {e.get('pr_link')}")
    print()
    print(f"Reviewed (open comments)      · {len(reviewed_with_comments)}")
    for e in reviewed_with_comments:
        print(f"  - {e.get('pr_link')}")


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


def cmd_add(args) -> int:
    """Add a single PR to the queue, by direct PR URL or by Slack permalink."""
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-add")
    url = args.url.strip()

    if _looks_like_pr_url(url):
        return _add_from_pr_url(url, queue_path, args, log)

    slack_info = _parse_slack_permalink(url)
    if slack_info is not None:
        return _add_from_slack_permalink(url, slack_info, queue_path, args, log)

    die(
        f"unrecognized URL: {url}\n"
        "Expected a PR URL (github.com/<owner>/<repo>/pull/<n> or "
        "bitbucket.org/<ws>/<repo>/pull-requests/<n>) or a Slack permalink "
        "(https://<workspace>.slack.com/archives/<channel>/p<ts>)."
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
        "pr_link": pr_url,
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
            "pr_link": pr_url,
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
                "pr_link": pr_url,
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

def cmd_update(args) -> int:
    queue_path = Path(args.queue).expanduser()
    log = get_logger("pr-queue-update")
    entry = find_row(queue_path, args.pr_url)
    if entry is None:
        die(f"no entry found for {args.pr_url} in {queue_path}")

    from pr_scan import cheap_pr_meta  # type: ignore[import-not-found]
    meta = cheap_pr_meta(args.pr_url, log)
    if "error" in meta:
        die(f"meta-fetch failed: {meta['error']}")

    updates = {"last_checked_at": _now_iso()}
    new_head = meta.get("head_oid")
    if new_head:
        updates["head_oid"] = new_head
    if meta.get("merged_at"):
        updates["status"] = STATUS_MERGED
    update_pr_entry(queue_path, args.pr_url, updates)
    out = {
        "pr_url": args.pr_url,
        "head_oid": new_head,
        "merged": bool(meta.get("merged_at")),
        "status": updates.get("status", entry.get("status")),
        "head_unchanged": (entry.get("head_oid") == new_head) if entry.get("head_oid") else None,
    }
    print(json.dumps(out, indent=2))
    return 0


# ----- release -------------------------------------------------------------

def cmd_release(args) -> int:
    queue_path = Path(args.queue).expanduser()
    ok = update_pr_entry(queue_path, args.pr_url, {"taken_at": None})
    if not ok:
        die(f"no entry found for {args.pr_url} in {queue_path}")
    print(f"released: {args.pr_url}")
    return 0


# ----- entrypoint ---------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-queue",
                                 description="Inspect / manage the PR review queue.")
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_list = sub.add_parser("list", help="list queue entries")
    sp_list.add_argument("--status", help="filter by status (pending|in_review|reviewed|comments|approved|merged|error|reminded)")
    sp_list.set_defaults(func=cmd_list)

    sp_show = sub.add_parser("show", help="show one entry as JSON")
    sp_show.add_argument("pr_url")
    sp_show.set_defaults(func=cmd_show)

    sp_add = sub.add_parser("add", help="add a PR by URL or by Slack permalink")
    sp_add.add_argument("url")
    sp_add.add_argument("-y", "--yes", action="store_true",
                        help="non-interactive; refresh in place if already present")
    sp_add.set_defaults(func=cmd_add)

    sp_upd = sub.add_parser("update", help="refresh head_oid + merged-state on one row")
    sp_upd.add_argument("pr_url")
    sp_upd.add_argument("-y", "--yes", action="store_true")
    sp_upd.set_defaults(func=cmd_update)

    sp_clean = sub.add_parser("clean", help="drop merged rows (or --all)")
    sp_clean.add_argument("--all", action="store_true",
                          help="drop EVERY entry + task folder (requires --yes to confirm)")
    sp_clean.add_argument("-y", "--yes", action="store_true",
                          help="confirm a --all clean (no-op without --all)")
    sp_clean.set_defaults(func=cmd_clean)

    sp_rtm = sub.add_parser("ready-to-merge", help="list approved PRs grouped by comment state")
    sp_rtm.set_defaults(func=cmd_ready_to_merge)

    sp_rel = sub.add_parser("release", help="clear `taken_at` on a row")
    sp_rel.add_argument("pr_url")
    sp_rel.set_defaults(func=cmd_release)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
