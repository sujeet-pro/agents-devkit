"""pr_scan.py — `adk pr-scan` subcommand.

Scans configured Slack channels for PR links, fetches cheap PR meta (merged?
head_sha?), and merges the results into ~/.agents-devkit/config/pr-queue.json5.

Each PR link gets its own queue row, even when multiple PRs live in the same
thread. Specifically:

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
from datetime import datetime, timezone
from difflib import SequenceMatcher
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

from _common import (  # noqa: E402
    RunEvent,
    die,
    emit_event,
    format_pr_ref,
    get_logger,
    is_orchestrated,
    parse_pr_url,
    summarize_items,
)
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH,
    load_slack_config, read_queue, write_queue, merge_scan_results,
    STATUS_PENDING, STATUS_MERGED,
)
from slack_helpers import (  # noqa: E402
    SlackClient, find_pr_urls, extract_message_actor_ids,
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
                   "--json", "number,title,headRefName,headRefOid,baseRefName,mergedAt,state,author,url"]
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
                "title": d.get("title"),
                "source_branch": d.get("headRefName"),
            }
        # bitbucket
        import requests  # local import
        tok = os.environ.get("BITBUCKET_TOKEN_CRED")
        user = os.environ.get("BITBUCKET_USERNAME")
        if not tok:
            return {"error": "BITBUCKET_TOKEN_CRED not set"}
        auth = (user, tok) if user else None
        headers = {"Accept": "application/json"} if auth else {"Authorization": f"Bearer {tok}", "Accept": "application/json"}
        base = f"https://api.bitbucket.org/2.0/repositories/{p['owner']}/{p['repo']}"
        url = f"{base}/pullrequests/{p['pr_number']}"
        r = requests.get(url, auth=auth, headers=headers, timeout=20)
        r.raise_for_status()
        d = r.json()
        state = d.get("state")
        merged_at = d.get("updated_on") if state == "MERGED" else None
        # Bitbucket Cloud's pullrequests endpoint returns source.commit.hash
        # as a 12-char abbreviation. `git fetch origin <short>` fails over
        # the wire ("couldn't find remote ref"); we need the full 40-char
        # SHA. Resolve via the /commit endpoint (one extra round-trip per
        # row — only fires when the value looks abbreviated).
        short_head = (d.get("source") or {}).get("commit", {}).get("hash")
        head_sha = short_head
        if short_head and len(short_head) < 40:
            try:
                cr = requests.get(f"{base}/commit/{short_head}",
                                  auth=auth, headers=headers, timeout=20)
                cr.raise_for_status()
                full = cr.json().get("hash")
                if full and len(full) >= 40 and full.startswith(short_head):
                    head_sha = full
                else:
                    log.warning("bb: commit-endpoint did not return a full SHA "
                                "for %s (got %r); keeping abbreviated value",
                                short_head, full)
            except Exception as e:
                log.warning("bb: failed to resolve abbreviated head_sha %s "
                            "via /commit endpoint (%s); keeping abbreviated",
                            short_head, e)
        return {
            "host": host, "owner": p["owner"], "repo": p["repo"], "pr_number": p["pr_number"],
            "head_sha": head_sha,
            "target_branch": (d.get("destination") or {}).get("branch", {}).get("name"),
            "merged_at": merged_at,
            "state": state,
            "author": (d.get("author") or {}).get("display_name") or (d.get("author") or {}).get("uuid"),
            "url": ((d.get("links") or {}).get("html") or {}).get("href"),
            "title": d.get("title"),
            "source_branch": (d.get("source") or {}).get("branch", {}).get("name"),
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
               n_pr_links_in_message: int, permalink: str,
               thread_pr_count: int | None = None) -> dict:
    """Build the `slack` dict for a candidate row.

    `n_pr_links_in_message` is the count of PR URLs in THIS message alone
    (main message OR a specific reply). `thread_pr_count` is the total
    across main + all replies in the thread — the value that decides
    reaction-vs-reply policy (set by the user 2026-05-22): we react to the
    main message only when the entire thread contains exactly one PR;
    otherwise each PR gets a thread reply with its own link so each post
    is self-identifying.
    """
    return {
        "permalink": permalink,
        "channel_id": channel_id,
        "message_ts": message_ts,
        "thread_ts": thread_ts,
        "thread_starter_user_id": thread_starter_user_id,
        "link_origin": link_origin,
        "n_pr_links_in_message": n_pr_links_in_message,
        "thread_pr_count": thread_pr_count if thread_pr_count is not None else n_pr_links_in_message,
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
        resolver = getattr(client, "resolve_user_token_ids", None)
        ids = set(resolver(token)) if callable(resolver) else set()
        if not ids:
            uid = client.resolve_user_token(token)
            ids = {uid} if uid else set()
        if ids:
            filter_user_ids.update(ids)
        else:
            log.warning("could not resolve filter user `%s`", token)
    apply_user_filter = bool(filter_user_ids)
    quiet = is_orchestrated()
    if apply_user_filter and not quiet:
        log.info("filter active — only threads mentioning any of: %s", sorted(filter_user_ids))

    channels = slack_cfg.get("channels", []) or []
    if not channels:
        die("slack config: `channels` is empty — nothing to scan.")

    if not quiet:
        log.info("scanning oldest_ts=%s across %d channels", oldest_ts, len(channels))

    candidates: list[dict] = []
    stats = {
        "channels_scanned": 0, "messages_seen": 0,
        "threads_with_main_pr": 0, "filtered_out_user": 0,
        "rows_from_main": 0, "rows_from_replies": 0,
    }

    total_channels = len(channels)
    for idx, ch in enumerate(channels, start=1):
        try:
            cid = client.resolve_channel(ch)
        except SystemExit:
            log.warning("skipping channel %s — couldn't resolve", ch)
            continue
        stats["channels_scanned"] += 1
        if not quiet:
            log.info("channel %s → %s", ch, cid)
        else:
            emit_event(RunEvent(
                kind="step_progress",
                name="pr-scan",
                status="run",
                detail=f"channel {idx}/{total_channels} {ch}: starting",
            ))

        channel_messages = 0
        channel_threads = 0
        for msg in client.iter_channel_messages(cid, oldest_ts):
            stats["messages_seen"] += 1
            channel_messages += 1
            if quiet and channel_messages % 25 == 0:
                emit_event(RunEvent(
                    kind="step_progress",
                    name="pr-scan",
                    status="run",
                    detail=(
                        f"channel {idx}/{total_channels} {ch}: "
                        f"{channel_messages} messages, {channel_threads} PR threads"
                    ),
                ))
            text = msg.get("text") or ""
            main_prs = find_pr_urls(text, url_patterns)
            if not main_prs:
                continue
            stats["threads_with_main_pr"] += 1
            channel_threads += 1
            if quiet:
                emit_event(RunEvent(
                    kind="step_progress",
                    name="pr-scan",
                    status="run",
                    detail=(
                        f"channel {idx}/{total_channels} {ch}: "
                        f"found PR thread {channel_threads} after {channel_messages} messages"
                    ),
                ))
            main_ts = msg.get("ts")
            thread_ts = msg.get("thread_ts", main_ts)
            thread_user = msg.get("user")

            # Walk replies once — used for filter + reply-PR-scan + supporting docs.
            participants: set[str] = set(extract_message_actor_ids(msg))
            if thread_user:
                participants.add(thread_user)
            reply_msgs: list[dict] = []
            if msg.get("reply_count", 0) > 0:
                for rep in client.iter_thread_replies(cid, thread_ts):
                    if rep.get("ts") == thread_ts:
                        continue  # already saw the root
                    reply_msgs.append(rep)
                    participants.update(extract_message_actor_ids(rep))

            if apply_user_filter and not (participants & filter_user_ids):
                stats["filtered_out_user"] += 1
                continue

            all_text = text + "\n" + "\n".join((r.get("text") or "") for r in reply_msgs)
            supporting = find_supporting_docs(all_text)
            main_permalink = client.get_message_permalink(cid, main_ts)

            # thread_pr_count = total PR links in main + all replies. This is
            # the value the slack reactor/poster uses to decide whether a
            # reaction on a single message can identify "which PR" — only
            # safe when the whole thread has exactly one PR. Compute it once
            # here so every row in this thread carries the same total.
            reply_pr_counts = [
                len(find_pr_urls(r.get("text") or "", url_patterns))
                for r in reply_msgs
            ]
            thread_pr_count = len(main_prs) + sum(reply_pr_counts)
            thread_pr_urls: list[str] = []
            for u in main_prs:
                if u not in thread_pr_urls:
                    thread_pr_urls.append(u)
            for rep in reply_msgs:
                for u in find_pr_urls(rep.get("text") or "", url_patterns):
                    if u not in thread_pr_urls:
                        thread_pr_urls.append(u)

            def related_pr_urls(pr_url: str) -> list[str]:
                return [u for u in thread_pr_urls if u != pr_url]

            for pr_url in main_prs:
                candidates.append({
                    "pr_url": pr_url,
                    "supporting_docs": supporting,
                    "related_pr_urls": related_pr_urls(pr_url),
                    "slack": _slack_for(
                        pr_url,
                        channel_id=cid, message_ts=main_ts, thread_ts=thread_ts,
                        thread_starter_user_id=thread_user, link_origin="main",
                        n_pr_links_in_message=len(main_prs), permalink=main_permalink,
                        thread_pr_count=thread_pr_count,
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
                        "related_pr_urls": related_pr_urls(pr_url),
                        "slack": _slack_for(
                            pr_url,
                            channel_id=cid, message_ts=rep_ts, thread_ts=thread_ts,
                            thread_starter_user_id=thread_user, link_origin="reply",
                            n_pr_links_in_message=len(rep_prs), permalink=rep_permalink,
                            thread_pr_count=thread_pr_count,
                        ),
                    })
                stats["rows_from_replies"] += len(rep_prs)

        if quiet:
            emit_event(RunEvent(
                kind="step_progress",
                name="pr-scan",
                status="run",
                detail=(
                    f"channel {idx}/{total_channels} {ch}: "
                    f"done, {channel_messages} messages, {channel_threads} PR threads"
                ),
            ))

    return candidates, stats


def post_process(candidates: list[dict], slack_cfg: dict, dry_run: bool, log) -> tuple[list[dict], dict]:
    """For each candidate: cheap meta. If merged + thread carries exactly
    one PR + emoji configured → react on its own message_ts. Return
    (non_merged, stats).

    Reaction policy (2026-05-22): a single emoji on a slack message can
    only identify a verdict for the PR it visually represents. When the
    whole thread contains exactly one PR, the reaction is unambiguous. When
    the thread carries multiple PRs (main + replies combined), a reaction
    on the main message would conflate verdicts — so we skip the reaction
    entirely and rely on reply-based reporting downstream, where each
    reply text includes the PR link.
    """
    stats = {"merged_reacted": 0, "merged_skipped": 0,
             "merged_skipped_multi_pr": 0, "merged_skipped_multi_pr_examples": [],
             "errors": 0, "kept": 0}
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
            # Thread-wide PR count is the gate for reaction safety.
            thread_pr_count = slack.get("thread_pr_count", 1)
            if thread_pr_count == 1 and merged_emoji and not dry_run:
                if client is None:
                    client = SlackClient()
                ok = client.add_reaction(slack["channel_id"], slack["message_ts"], merged_emoji)
                if ok:
                    stats["merged_reacted"] += 1
            elif thread_pr_count > 1:
                stats["merged_skipped_multi_pr"] += 1
                examples = stats.setdefault("merged_skipped_multi_pr_examples", [])
                ref = format_pr_ref(c["pr_url"])
                if ref not in examples and len(examples) < 5:
                    examples.append(ref)
                if not is_orchestrated():
                    log.info("merged PR in multi-PR thread (count=%d) — skipping reaction; "
                             "reply-mode verdict expected: %s", thread_pr_count, c["pr_url"])
            continue
        c["_meta"] = meta
        kept.append(c)
        stats["kept"] += 1
    return kept, stats


def _similar(a: str | None, b: str | None) -> float:
    a = (a or "").lower().strip()
    b = (b or "").lower().strip()
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def _looks_related(rows: list[dict]) -> bool:
    metas = [r.get("_meta") or {} for r in rows]
    for i, left in enumerate(metas):
        for right in metas[i + 1:]:
            if left.get("repo") != right.get("repo"):
                # Cross-repo split PRs are common; require title/branch overlap.
                pass
            if _similar(left.get("source_branch"), right.get("source_branch")) > 0.6:
                return True
            if _similar(left.get("title"), right.get("title")) > 0.5:
                return True
    return False


def maybe_emit_gentle_reminders(candidates: list[dict], existing_queue: dict,
                                slack_cfg: dict, dry_run: bool, log) -> dict:
    """Post one gentle reminder per unrelated multi-PR Slack thread.

    Duplicate guard: if any existing queue row for the thread already has
    `slack.gentle_reminder_at`, the thread is skipped.
    """
    stats = {"posted": 0, "skipped_existing": 0, "skipped_related": 0, "dry_run": 0}
    if slack_cfg.get("gentle_reminder_enabled", True) is False:
        return stats

    existing_threads: set[tuple[str, str]] = set()
    for row in existing_queue.get("prs", []) or []:
        slack = row.get("slack") or {}
        if slack.get("gentle_reminder_at"):
            existing_threads.add((slack.get("channel_id"), slack.get("thread_ts")))

    groups: dict[tuple[str, str], list[dict]] = {}
    for row in candidates:
        slack = row.get("slack") or {}
        key = (slack.get("channel_id"), slack.get("thread_ts"))
        if not key[0] or not key[1]:
            continue
        if int(slack.get("thread_pr_count") or 1) <= 1:
            continue
        groups.setdefault(key, []).append(row)

    client: SlackClient | None = None
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    for (channel_id, thread_ts), rows in groups.items():
        if (channel_id, thread_ts) in existing_threads:
            stats["skipped_existing"] += 1
            continue
        if _looks_related(rows):
            stats["skipped_related"] += 1
            continue
        text = (
            f"Heads-up: I see {len(rows)} PRs in this message — they don't look related. "
            "Posting each PR in its own message keeps review threading cleaner."
        )
        if dry_run:
            stats["dry_run"] += 1
        else:
            if client is None:
                client = SlackClient()
            client.post_thread_reply(channel_id, thread_ts, text)
            stats["posted"] += 1
        for row in rows:
            row.setdefault("slack", {})["gentle_reminder_at"] = now
    return stats


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
    ap.add_argument("--quiet", action="store_true", help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-scan", enabled=True, argv=argv)

    quiet = bool(args.quiet or is_orchestrated())
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
        if not quiet:
            log.info("scanning channels-only: %s (overrides configured channels)", only)
    elif extra:
        slack_cfg = dict(slack_cfg)
        slack_cfg["channels"] = list(slack_cfg.get("channels") or []) + [
            c for c in extra if c not in (slack_cfg.get("channels") or [])
        ]
        if not quiet:
            log.info("appended extra channels: %s", extra)

    oldest_ts, window = _resolve_oldest_ts(args, slack_cfg)
    if not quiet:
        log.info("scanning %s (oldest_ts=%s)", window, oldest_ts)
    else:
        emit_event(RunEvent(kind="step_start", name="pr-scan",
                            status="run", detail=f"window {window}"))

    candidates, scan_stats = scan(slack_cfg, oldest_ts, log)
    if not quiet:
        log.info("scan_stats: %s", scan_stats)

    kept, post_stats = post_process(candidates, slack_cfg, args.dry_run, log)
    if not quiet:
        log.info("post_process: %s", post_stats)

    existing = read_queue(queue_path)
    reminder_stats = maybe_emit_gentle_reminders(kept, existing, slack_cfg, args.dry_run, log)
    if not quiet:
        log.info("gentle_reminders: %s", reminder_stats)
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
        "gentle_reminders": reminder_stats,
        "merge": merge_summary,
        "dry_run": args.dry_run,
    }
    if quiet:
        detail = (
            f"{scan_stats.get('channels_scanned', 0)} channels, "
            f"{scan_stats.get('messages_seen', 0)} messages, "
            f"+{merge_summary.get('added', 0)} added, "
            f"{post_stats.get('merged_skipped_multi_pr', 0)} skipped merged multi-PR"
        )
        emit_event(RunEvent(kind="step_done", name="pr-scan",
                            status="done", detail=detail))
        skipped = post_stats.get("merged_skipped_multi_pr", 0)
        if skipped:
            examples = post_stats.get("merged_skipped_multi_pr_examples") or []
            emit_event(RunEvent(
                kind="attention",
                name="pr-scan",
                status="warn",
                detail=f"skipped reactions for {skipped} merged PRs in multi-PR threads",
                reason=f"examples: {summarize_items(examples)}",
            ))
    else:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
