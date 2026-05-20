#!/usr/bin/env python3
"""scan_slack.py — scan configured slack channels for PR links, merge into queue.json5.

Flow (per `references/workflow.md`):
  1. Load slack.json5 + existing queue.json5
  2. For each configured channel:
       - list messages last N days
       - list replies for each thread
       - find PR URLs matching url_patterns
       - apply filter_mentioned_users (any of these in main message OR replies)
  3. For each candidate PR:
       - cheap meta fetch (gh / bb)
       - if merged AND n_pr_links_in_message == 1 AND status_emoji.merged != null → react with merged emoji
       - drop merged PRs from the actionable set
       - non-merged PRs → emit as a "scanned entry"
  4. Merge scanned entries into queue.json5 (additive, dedupe by repo+pr-number)
  5. Print summary

Args:
  --slack-config <path>    default: ~/.agents-devkit/config/pr-reviews-slack.json5
  --queue <path>           default: ~/.agents-devkit/pr-reviews/queue.json5
  --since <days>           override scan_days_default
  --dry-run                walk + classify, don't write the queue, don't react
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import die, get_logger, parse_pr_url  # noqa: E402
from queue_io import (  # noqa: E402
    load_slack_config, read_queue, write_queue, merge_scan_results,
    STATUS_PENDING, STATUS_MERGED,
)
from slack_helpers import (  # noqa: E402
    SlackClient, find_pr_urls, count_pr_urls, extract_mentioned_user_ids, days_ago_ts,
)

DEFAULT_SLACK_CONFIG = Path.home() / ".agents-devkit" / "config" / "connectors" / "slack.md"
DEFAULT_QUEUE = Path.home() / ".agents-devkit" / "pr-reviews" / "queue.json5"


# ----- PR meta (cheap, no clone) -------------------------------------------

def cheap_pr_meta(pr_url: str, log) -> dict:
    """Return {head_oid, merged_at|None, state}. Errors → {error: str}."""
    try:
        p = parse_pr_url(pr_url)
    except ValueError as e:
        return {"error": str(e)}
    host = p["host"]
    try:
        if host == "github":
            cmd = ["gh", "pr", "view", str(p["pr_number"]),
                   "--repo", f"{p['owner']}/{p['repo']}",
                   "--json", "number,headRefOid,mergedAt,state,author,url"]
            cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
            d = json.loads(cp.stdout)
            return {
                "host": host, "owner": p["owner"], "repo": p["repo"], "pr_number": p["pr_number"],
                "head_oid": d.get("headRefOid"),
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
            "head_oid": (d.get("source") or {}).get("commit", {}).get("hash"),
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

_SUPPORTING_PATTERNS = [
    "https://docs.google.com/",
    "https://drive.google.com/",
    "https://atlassian.net/",     # confluence + jira live on subdomains
    ".atlassian.net/",            # match *.atlassian.net/...
    "https://www.figma.com/",
    "https://github.com/",        # only if NOT a PR; the scanner re-checks
]


def find_supporting_docs(text: str, pr_url_patterns: list[str]) -> list[str]:
    """Find supporting-doc URLs in `text` (atlassian / google / figma / bare gh that isn't a PR).
    Excludes URLs that already match pr_url_patterns AND look like a PR.
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
        # Skip PR URLs.
        if pr_re_gh.search(url) or pr_re_bb.search(url):
            continue
        ulow = url.lower()
        if any(p in ulow for p in [".atlassian.net/", "docs.google.com/", "drive.google.com/", "figma.com/"]):
            seen.add(url)
            out.append(url)
    return out


# ----- main scan -----------------------------------------------------------

def scan(slack_cfg: dict, since_days: int, log) -> tuple[list[dict], dict]:
    """Return (scanned_entries, stats)."""
    client = SlackClient()
    url_patterns = slack_cfg.get("url_patterns", [])
    if not url_patterns:
        die("slack.json5: `url_patterns` is empty — nothing to scan for.")

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
        log.info("filter active — only PRs mentioning any of: %s", sorted(filter_user_ids))

    channels = slack_cfg.get("channels", []) or []
    if not channels:
        die("slack.json5: `channels` is empty — nothing to scan.")

    oldest = days_ago_ts(since_days)
    log.info("scanning last %d days (oldest=%s) across %d channels", since_days, oldest, len(channels))

    candidates: list[dict] = []
    stats = {"channels_scanned": 0, "messages_seen": 0, "with_pr_link": 0,
             "filtered_out_user": 0, "candidates": 0}

    for ch in channels:
        try:
            cid = client.resolve_channel(ch)
        except SystemExit:
            log.warning("skipping channel %s — couldn't resolve", ch)
            continue
        stats["channels_scanned"] += 1
        log.info("channel %s → %s", ch, cid)

        for msg in client.iter_channel_messages(cid, oldest):
            stats["messages_seen"] += 1
            text = msg.get("text") or ""
            pr_urls = find_pr_urls(text, url_patterns)
            if not pr_urls:
                continue
            stats["with_pr_link"] += 1
            n_pr_links = len(pr_urls)

            # Thread participants — for user filter + thread_starter capture.
            thread_ts = msg.get("thread_ts", msg.get("ts"))
            thread_user = msg.get("user")  # the user who posted the top-level message
            participants: set[str] = set(extract_mentioned_user_ids(text))
            if thread_user:
                participants.add(thread_user)

            # Walk replies (cheap: only if message has replies AND we need to filter).
            replies_text = ""
            if msg.get("reply_count", 0) > 0:
                for rep in client.iter_thread_replies(cid, thread_ts):
                    if rep.get("ts") == thread_ts:
                        continue  # already saw the root
                    rep_text = rep.get("text") or ""
                    replies_text += "\n" + rep_text
                    if rep.get("user"):
                        participants.add(rep["user"])
                    for uid in extract_mentioned_user_ids(rep_text):
                        participants.add(uid)

            if apply_user_filter and not (participants & filter_user_ids):
                stats["filtered_out_user"] += 1
                continue

            # Supporting docs — from BOTH the main message and its replies.
            supporting = find_supporting_docs(text + "\n" + replies_text, url_patterns)

            permalink = client.get_message_permalink(cid, msg.get("ts", ""))

            for pr_url in pr_urls:
                candidates.append({
                    "pr_link": pr_url,
                    "supporting_docs": supporting,
                    "slack": {
                        "permalink": permalink,
                        "channel_id": cid,
                        "message_ts": msg.get("ts"),
                        "thread_ts": thread_ts,
                        "thread_starter_user_id": thread_user,
                        "n_pr_links_in_message": n_pr_links,
                        "last_reaction_status": None,
                        "last_reminder_at": None,
                    },
                })
            stats["candidates"] += len(pr_urls)

    return candidates, stats


# ----- post-scan: meta-fetch + react-on-merged + drop merged ---------------

def post_process(candidates: list[dict], slack_cfg: dict, dry_run: bool, log) -> tuple[list[dict], dict]:
    """For each candidate: cheap meta. If merged + single-PR-in-msg + emoji configured → react.
    Return (non_merged_candidates, stats)."""
    stats = {"merged_reacted": 0, "merged_skipped": 0, "errors": 0, "kept": 0}
    status_emoji = slack_cfg.get("status_emoji") or {}
    merged_emoji = status_emoji.get("merged")  # may be None
    kept: list[dict] = []
    client: SlackClient | None = None

    for c in candidates:
        meta = cheap_pr_meta(c["pr_link"], log)
        if "error" in meta:
            stats["errors"] += 1
            log.warning("meta-fetch %s → %s", c["pr_link"], meta["error"])
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
        c["_meta"] = meta  # passthrough for downstream
        kept.append(c)
        stats["kept"] += 1

    return kept, stats


# ----- main ----------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slack-config", default=str(DEFAULT_SLACK_CONFIG))
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE))
    ap.add_argument("--since", type=int, default=0, help="days back to scan (0 = use slack.json5 default)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    log = get_logger("scan_slack")
    slack_cfg_path = Path(args.slack_config).expanduser()
    queue_path = Path(args.queue).expanduser()

    try:
        slack_cfg = load_slack_config(slack_cfg_path)
    except FileNotFoundError as e:
        die(
            f"{e}\n\nTo bootstrap: copy "
            f"{Path(__file__).parent.parent / 'templates' / 'pr-reviews-slack.json5'} "
            f"into ~/.agents-devkit/config/connectors/slack.md frontmatter under `pr_reviews:`."
        )
    since_days = args.since or int(slack_cfg.get("scan_days_default", 14))

    candidates, scan_stats = scan(slack_cfg, since_days, log)
    log.info("scan_stats: %s", scan_stats)

    kept, post_stats = post_process(candidates, slack_cfg, args.dry_run, log)
    log.info("post_process: %s", post_stats)

    existing = read_queue(queue_path) if queue_path.exists() else {"filters": None, "prs": []}
    merged = merge_scan_results(existing, kept)
    merge_summary = merged.pop("_merge_summary", {})

    if not args.dry_run:
        write_queue(queue_path, merged)

    summary = {
        "queue": str(queue_path),
        "slack_config": str(slack_cfg_path),
        "since_days": since_days,
        "scan": scan_stats,
        "post_process": post_stats,
        "merge": merge_summary,
        "dry_run": args.dry_run,
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
