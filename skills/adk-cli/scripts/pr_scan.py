"""pr_scan.py — `adk pr-scan` subcommand.

Scans configured Slack channels for PR links, fetches cheap PR meta (merged?
head_sha?), and merges the results into ~/.agents-devkit/config/pr-queue.json5.

Difference vs the legacy scan_slack.py this replaces: each PR link gets ITS OWN
queue row, even when multiple PRs live in the same thread. Specifically:

  - A main message with N PR links → N rows, all with link_origin="main"
    and message_ts=main.ts; n_pr_links_in_message=N (reactions are only safe
    when N==1, since otherwise an emoji on the message would be ambiguous).
  - A thread reply with M PR links → M rows, link_origin="reply",
    message_ts=reply.ts (reactions/replies will land on the reply, not the
    parent), thread_ts=main.ts.

Both rows carry the same thread-derived `supporting_docs` (Atlassian / Drive /
Figma URLs found anywhere in the thread).

Flow:
  1. Load slack config + existing queue.
  2. For each configured channel, walk messages and (when they contain PR links)
     their thread replies.
  3. Apply filter_mentioned_users at the thread level — any participant (main
     author, reply authors, mentions in main or replies) must intersect the
     configured filter user set.
  4. For each candidate PR: cheap meta fetch.
     - If merged AND n_pr_links_in_message == 1 AND a merged emoji is configured
       → react with the merged emoji + drop from the actionable set.
  5. Merge non-merged candidates into the queue (additive; dedupe by host/repo/pr#).

Args:
  --slack-config <path>   default: ~/.agents-devkit/config/connectors/slack.md
  --queue <path>          default: ~/.agents-devkit/config/pr-queue.json5
  --since-hours <h>       override scan window in hours (else: slack config
                          `scan_days_default` × 24)
  --since-days <d>        override scan window in days
  --channels <c1,c2,…>    additive override — scan these IN ADDITION TO the
                          configured channels. Comma-separated.
  --channels-only <c1,…>  replace the configured channel list entirely for
                          this run (useful for ad-hoc scans of unrelated rooms).
  --dry-run               walk + classify; do not write the queue, do not react
  -y, --yes               non-interactive; smart defaults. No prompts.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import die, get_logger, parse_pr_url  # noqa: E402
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH,
    load_slack_config, read_queue, write_queue, merge_scan_results,
    STATUS_PENDING, STATUS_MERGED,
)
from slack_helpers import (  # noqa: E402
    SlackClient, find_pr_urls, extract_mentioned_user_ids,
    days_ago_ts, hours_ago_ts,
)

DEFAULT_SLACK_CONFIG = Path.home() / ".agents-devkit" / "config" / "connectors" / "slack.md"


# ----- PR meta (cheap, no clone) -------------------------------------------

def cheap_pr_meta(pr_url: str, log) -> dict:
    """Return {host, owner, repo, pr_number, head_sha, merged_at|None, state,
    author, url, target_branch}. Errors → {error: str}.
    """
    try:
        p = parse_pr_url(pr_url)
    except ValueError as e:
        return {"error": str(e)}
    host = p["host"]
    try:
        if host == "github":
            cmd = ["gh", "pr", "view", str(p["pr_number"]),
                   "--repo", f"{p['owner']}/{p['repo']}",
                   "--json", "number,headRefOid,baseRefName,mergedAt,state,author,url"]
            cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
            d = json.loads(cp.stdout)
            return {
                "host": host, "owner": p["owner"], "repo": p["repo"], "pr_number": p["pr_number"],
                "head_sha": d.get("headRefOid"),
                "target_branch": d.get("baseRefName"),
                "merged_at": d.get("mergedAt"),
                "state": d.get("state"),
                "author": (d.get("author") or {}).get("login"),
                "url": d.get("url"),
            }
        # bitbucket
        import requests  # local import
        tok = os.environ.get("BITBUCKET_TOKEN_CRED")
        user = os.environ.get("BITBUCKET_USERNAME")
        if not tok:
            return {"error": "BITBUCKET_TOKEN_CRED not set"}
        auth = (user, tok) if user else None
        headers = {"Accept": "application/json"} if auth else {"Authorization": f"Bearer {tok}", "Accept": "application/json"}
        url = f"https://api.bitbucket.org/2.0/repositories/{p['owner']}/{p['repo']}/pullrequests/{p['pr_number']}"
        r = requests.get(url, auth=auth, headers=headers, timeout=20)
        r.raise_for_status()
        d = r.json()
        state = d.get("state")
        merged_at = d.get("updated_on") if state == "MERGED" else None
        return {
            "host": host, "owner": p["owner"], "repo": p["repo"], "pr_number": p["pr_number"],
            "head_sha": (d.get("source") or {}).get("commit", {}).get("hash"),
            "target_branch": (d.get("destination") or {}).get("branch", {}).get("name"),
            "merged_at": merged_at,
            "state": state,
            "author": (d.get("author") or {}).get("display_name") or (d.get("author") or {}).get("uuid"),
            "url": ((d.get("links") or {}).get("html") or {}).get("href"),
        }
    except subprocess.CalledProcessError as e:
        return {"error": f"gh pr view failed: {(e.stderr or '').strip()[:200]}"}
    except Exception as e:
        return {"error": f"meta-fetch: {e}"}


# ----- supporting-docs extraction ------------------------------------------

def find_supporting_docs(text: str) -> list[str]:
    """Extract Atlassian / Google / Figma URLs from a blob of Slack text. PR URLs
    are explicitly excluded.
    """
    if not text:
        return []
    out: list[str] = []
    pr_re_gh = re.compile(r"github\.com/[^/]+/[^/]+/pull/\d+", re.I)
    pr_re_bb = re.compile(r"bitbucket\.org/[^/]+/[^/]+/pull-requests/\d+", re.I)
    candidate_urls = []
    for m in re.finditer(r"<(https?://[^>|]+)(?:\|[^>]*)?>", text):
        candidate_urls.append(m.group(1))
    for m in re.finditer(r"https?://[^\s<>\]\)]+", text):
        candidate_urls.append(m.group(0).rstrip(".,);:"))
    seen: set[str] = set()
    for url in candidate_urls:
        if url in seen:
            continue
        if pr_re_gh.search(url) or pr_re_bb.search(url):
            continue
        ulow = url.lower()
        if any(p in ulow for p in (".atlassian.net/", "docs.google.com/", "drive.google.com/", "figma.com/")):
            seen.add(url)
            out.append(url)
    return out


# ----- main scan -----------------------------------------------------------

def _slack_for(pr_url: str, *, channel_id: str, message_ts: str, thread_ts: str,
               thread_starter_user_id: str | None, link_origin: str,
               n_pr_links_in_message: int, permalink: str) -> dict:
    """Build the `slack` dict for a candidate row."""
    return {
        "permalink": permalink,
        "channel_id": channel_id,
        "message_ts": message_ts,
        "thread_ts": thread_ts,
        "thread_starter_user_id": thread_starter_user_id,
        "link_origin": link_origin,
        "n_pr_links_in_message": n_pr_links_in_message,
        "last_reaction_status": None,
        "last_reminder_at": None,
    }


def scan(slack_cfg: dict, oldest_ts: str, log) -> tuple[list[dict], dict]:
    """Walk configured channels and return (candidate rows, stats)."""
    client = SlackClient()
    url_patterns = slack_cfg.get("url_patterns", [])
    if not url_patterns:
        die("slack config: `url_patterns` is empty — nothing to scan for.")

    filter_users_cfg = slack_cfg.get("filter_mentioned_users") or []
    filter_user_ids: set[str] = set()
    for token in filter_users_cfg:
        uid = client.resolve_user_token(token)
        if uid:
            filter_user_ids.add(uid)
        else:
            log.warning("could not resolve filter user `%s`", token)
    apply_user_filter = bool(filter_user_ids)
    if apply_user_filter:
        log.info("filter active — only threads mentioning any of: %s", sorted(filter_user_ids))

    channels = slack_cfg.get("channels", []) or []
    if not channels:
        die("slack config: `channels` is empty — nothing to scan.")

    log.info("scanning oldest_ts=%s across %d channels", oldest_ts, len(channels))

    candidates: list[dict] = []
    stats = {
        "channels_scanned": 0, "messages_seen": 0,
        "threads_with_main_pr": 0, "filtered_out_user": 0,
        "rows_from_main": 0, "rows_from_replies": 0,
    }

    for ch in channels:
        try:
            cid = client.resolve_channel(ch)
        except SystemExit:
            log.warning("skipping channel %s — couldn't resolve", ch)
            continue
        stats["channels_scanned"] += 1
        log.info("channel %s → %s", ch, cid)

        for msg in client.iter_channel_messages(cid, oldest_ts):
            stats["messages_seen"] += 1
            text = msg.get("text") or ""
            main_prs = find_pr_urls(text, url_patterns)
            if not main_prs:
                continue
            stats["threads_with_main_pr"] += 1
            main_ts = msg.get("ts")
            thread_ts = msg.get("thread_ts", main_ts)
            thread_user = msg.get("user")

            # Walk replies once — used for filter + reply-PR-scan + supporting docs.
            participants: set[str] = set(extract_mentioned_user_ids(text))
            if thread_user:
                participants.add(thread_user)
            reply_msgs: list[dict] = []
            if msg.get("reply_count", 0) > 0:
                for rep in client.iter_thread_replies(cid, thread_ts):
                    if rep.get("ts") == thread_ts:
                        continue  # already saw the root
                    reply_msgs.append(rep)
                    if rep.get("user"):
                        participants.add(rep["user"])
                    for uid in extract_mentioned_user_ids(rep.get("text") or ""):
                        participants.add(uid)

            if apply_user_filter and not (participants & filter_user_ids):
                stats["filtered_out_user"] += 1
                continue

            all_text = text + "\n" + "\n".join((r.get("text") or "") for r in reply_msgs)
            supporting = find_supporting_docs(all_text)
            main_permalink = client.get_message_permalink(cid, main_ts)

            for pr_url in main_prs:
                candidates.append({
                    "pr_url": pr_url,
                    "supporting_docs": supporting,
                    "slack": _slack_for(
                        pr_url,
                        channel_id=cid, message_ts=main_ts, thread_ts=thread_ts,
                        thread_starter_user_id=thread_user, link_origin="main",
                        n_pr_links_in_message=len(main_prs), permalink=main_permalink,
                    ),
                })
            stats["rows_from_main"] += len(main_prs)

            for rep in reply_msgs:
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
                            pr_url,
                            channel_id=cid, message_ts=rep_ts, thread_ts=thread_ts,
                            thread_starter_user_id=thread_user, link_origin="reply",
                            n_pr_links_in_message=len(rep_prs), permalink=rep_permalink,
                        ),
                    })
                stats["rows_from_replies"] += len(rep_prs)

    return candidates, stats


def post_process(candidates: list[dict], slack_cfg: dict, dry_run: bool, log) -> tuple[list[dict], dict]:
    """For each candidate: cheap meta. If merged + n_pr_links_in_message==1 + emoji
    configured → react on its own message_ts. Return (non_merged, stats).
    """
    stats = {"merged_reacted": 0, "merged_skipped": 0, "errors": 0, "kept": 0}
    status_emoji = slack_cfg.get("status_emoji") or {}
    merged_emoji = status_emoji.get("merged")
    kept: list[dict] = []
    client: SlackClient | None = None

    for c in candidates:
        meta = cheap_pr_meta(c["pr_url"], log)
        if "error" in meta:
            stats["errors"] += 1
            log.warning("meta-fetch %s → %s", c["pr_url"], meta["error"])
            continue
        if meta.get("merged_at"):
            stats["merged_skipped"] += 1
            slack = c.get("slack") or {}
            if slack.get("n_pr_links_in_message") == 1 and merged_emoji and not dry_run:
                if client is None:
                    client = SlackClient()
                ok = client.add_reaction(slack["channel_id"], slack["message_ts"], merged_emoji)
                if ok:
                    stats["merged_reacted"] += 1
            continue
        c["_meta"] = meta
        kept.append(c)
        stats["kept"] += 1
    return kept, stats


# ----- entrypoint ---------------------------------------------------------

def _resolve_oldest_ts(args, slack_cfg: dict) -> tuple[str, str]:
    """Return (oldest_ts, human_description)."""
    if args.since_hours and args.since_hours > 0:
        return hours_ago_ts(args.since_hours), f"last {args.since_hours}h"
    if args.since_days and args.since_days > 0:
        return days_ago_ts(args.since_days), f"last {args.since_days}d"
    default_days = int(slack_cfg.get("scan_days_default", 14))
    return days_ago_ts(default_days), f"last {default_days}d (config default)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-scan",
                                 description="Scan Slack channels for PR links → upsert into pr-queue.json5")
    ap.add_argument("--slack-config", default=str(DEFAULT_SLACK_CONFIG))
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    ap.add_argument("--since-hours", type=float, default=0.0)
    ap.add_argument("--since-days", type=int, default=0)
    ap.add_argument("--channels", default="",
                    help="comma-separated channels to scan in addition to slack config")
    ap.add_argument("--channels-only", default="",
                    help="comma-separated channels to scan INSTEAD of slack config")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="non-interactive; smart defaults")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to ~/.agents-devkit/logs/")
    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-scan", enabled=True, argv=argv)

    log = get_logger("pr-scan")
    slack_cfg_path = Path(args.slack_config).expanduser()
    queue_path = Path(args.queue).expanduser()

    try:
        slack_cfg = load_slack_config(slack_cfg_path)
    except FileNotFoundError as e:
        die(
            f"{e}\n\nAdd a `pr_reviews:` section to "
            f"~/.agents-devkit/config/connectors/slack.md frontmatter with at least "
            "channels, url_patterns, status_emoji, and (optionally) filter_mentioned_users."
        )

    # Channel overrides — --channels-only replaces wholesale; --channels appends.
    extra = [c.strip() for c in args.channels.split(",") if c.strip()]
    only = [c.strip() for c in args.channels_only.split(",") if c.strip()]
    if only:
        slack_cfg = dict(slack_cfg)
        slack_cfg["channels"] = only
        log.info("scanning channels-only: %s (overrides configured channels)", only)
    elif extra:
        slack_cfg = dict(slack_cfg)
        slack_cfg["channels"] = list(slack_cfg.get("channels") or []) + [
            c for c in extra if c not in (slack_cfg.get("channels") or [])
        ]
        log.info("appended extra channels: %s", extra)

    oldest_ts, window = _resolve_oldest_ts(args, slack_cfg)
    log.info("scanning %s (oldest_ts=%s)", window, oldest_ts)

    candidates, scan_stats = scan(slack_cfg, oldest_ts, log)
    log.info("scan_stats: %s", scan_stats)

    kept, post_stats = post_process(candidates, slack_cfg, args.dry_run, log)
    log.info("post_process: %s", post_stats)

    existing = read_queue(queue_path)
    merged = merge_scan_results(existing, kept)
    merge_summary = merged.pop("_merge_summary", {})

    if not args.dry_run:
        write_queue(queue_path, merged)

    summary = {
        "queue": str(queue_path),
        "slack_config": str(slack_cfg_path),
        "window": window,
        "scan": scan_stats,
        "post_process": post_stats,
        "merge": merge_summary,
        "dry_run": args.dry_run,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
