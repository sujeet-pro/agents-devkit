"""pr_scan.py — `adk pr-scan` subcommand.

Scans configured Slack channels for PR links, fetches cheap PR meta (merged?
head_sha?), and merges the results into $ADK_CONFIG_HOME/pr-queue.json5.

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
  --slack-config <path>   default: $ADK_CONFIG_HOME/connectors/slack.md
  --queue <path>          default: $ADK_CONFIG_HOME/pr-queue.json5
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
from datetime import datetime, timedelta, timezone
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
_LIB_DIR = THIS_DIR.parent.parent.parent / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_config_home, adk_logs_home  # noqa: E402

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
    atomic_scan_merge, classify_pr_state,
    dedupe_key,
    STATUS_PENDING, STATUS_MERGED,
)
from slack_helpers import (  # noqa: E402
    SlackClient, find_pr_urls, extract_message_actor_ids,
    days_ago_ts, hours_ago_ts,
)
from repo import is_configured_repo  # noqa: E402

DEFAULT_SLACK_CONFIG = adk_config_home() / "connectors" / "slack.md"


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

            # thread_pr_count = number of UNIQUE PRs across main + all replies,
            # keyed by (host, owner, repo, pr#). The same PR mentioned in both
            # the main message and a reply collapses to one, as does a PR linked
            # via two URL shapes (`pull/42` vs `pull/42/files`). Used downstream
            # to decide "does this Slack thread carry exactly one PR?".
            thread_pr_urls: list[str] = []
            seen_keys: set[tuple[str, str, str, int]] = set()

            def _add_unique(url: str) -> None:
                try:
                    key = dedupe_key(url)
                except ValueError:
                    return
                if key in seen_keys:
                    return
                seen_keys.add(key)
                thread_pr_urls.append(url)

            for u in main_prs:
                _add_unique(u)
            for rep in reply_msgs:
                for u in find_pr_urls(rep.get("text") or "", url_patterns):
                    _add_unique(u)
            thread_pr_count = len(thread_pr_urls)

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
    """For each candidate: cheap meta. Drop merged PRs. Return (non_merged, stats)."""
    stats = {"merged_reacted": 0, "merged_skipped": 0,
             "merged_skipped_multi_pr": 0, "merged_skipped_multi_pr_examples": [],
             "errors": 0, "kept": 0}
    kept: list[dict] = []

    for c in candidates:
        meta = cheap_pr_meta(c["pr_url"], log)
        if "error" in meta:
            stats["errors"] += 1
            log.warning("meta-fetch %s → %s", c["pr_url"], meta["error"])
            continue
        if meta.get("merged_at"):
            stats["merged_skipped"] += 1
            slack = c.get("slack") or {}
            thread_pr_count = slack.get("thread_pr_count", 1)
            if thread_pr_count > 1:
                stats["merged_skipped_multi_pr"] += 1
                examples = stats.setdefault("merged_skipped_multi_pr_examples", [])
                ref = format_pr_ref(c["pr_url"])
                if ref not in examples and len(examples) < 5:
                    examples.append(ref)
                if not is_orchestrated():
                    log.info("merged PR in multi-PR thread (count=%d): %s",
                             thread_pr_count, c["pr_url"])
            continue
        c["_meta"] = meta
        kept.append(c)
        stats["kept"] += 1
    return kept, stats


def scan_user_mentions(slack_client: "SlackClient", user_id: str,
                       since_days: int, url_patterns: list[str],
                       log) -> list[dict]:
    """Search Slack for messages where `user_id` is mentioned, returning
    candidate rows (same shape as `scan` candidates) filtered to the
    `since_days` window.

    Uses Slack `search.messages` with `query="<@USER_ID> has:link"` to
    narrow to messages that contain at least one link (reduces noise).
    Each result runs through `find_pr_urls` and `find_supporting_docs` — the
    same extraction used by the channel-scan path.

    New rows get `discovery_source: "mention"`. The dedup against channel-
    scan results happens in `merge_scan_results` via `dedupe_key`.
    """
    if not user_id:
        log.warning("scan_user_mentions: user_id is empty — skipping mention scan")
        return []

    from datetime import timezone
    now_ts = datetime.now(timezone.utc).timestamp()
    cutoff_ts = now_ts - since_days * 86400

    query = f"<@{user_id}> has:link"
    candidates: list[dict] = []
    page = 1

    try:
        while True:
            # SlackClient._call maps method name string to the underlying
            # WebClient method. search_messages uses `count` + `page` paging.
            result = slack_client._call("search_messages",
                                        {"query": query, "count": 20, "page": page})
            if result is None:
                break
            messages = (result.get("messages") or {}).get("matches") or []
            if not messages:
                break
            for msg in messages:
                ts_raw = msg.get("ts") or "0"
                try:
                    ts_float = float(ts_raw)
                except (TypeError, ValueError):
                    ts_float = 0.0
                if ts_float < cutoff_ts:
                    continue
                text = msg.get("text") or ""
                pr_urls = find_pr_urls(text, url_patterns)
                if not pr_urls:
                    continue
                channel_info = msg.get("channel") or {}
                cid = channel_info.get("id") or ""
                supporting = find_supporting_docs(text)
                thread_ts = msg.get("thread_ts") or ts_raw
                permalink = msg.get("permalink") or ""
                n_prs = len(pr_urls)
                for pr_url in pr_urls:
                    related = [u for u in pr_urls if u != pr_url]
                    candidates.append({
                        "pr_url": pr_url,
                        "supporting_docs": supporting,
                        "related_pr_urls": related,
                        "discovery_source": "mention",
                        "slack": _slack_for(
                            pr_url,
                            channel_id=cid, message_ts=ts_raw, thread_ts=thread_ts,
                            thread_starter_user_id=msg.get("user"),
                            link_origin="mention",
                            n_pr_links_in_message=n_prs,
                            permalink=permalink,
                            thread_pr_count=n_prs,
                        ),
                    })
            paging = (result.get("messages") or {}).get("paging") or {}
            if page >= (paging.get("pages") or 1):
                break
            page += 1
    except Exception as e:
        log.warning("scan_user_mentions: search.messages failed (%s) — skipping mention scan", e)
        return []

    return candidates


def scan_direct_review_requests(log) -> list[dict]:
    """Return candidates from PRs where the user is a requested reviewer.

    For each configured repo in repos.md:
      - GitHub: calls `gh api search/issues` with `review-requested:@me`.
      - Bitbucket: logs a one-line warning and skips (REST helper not implemented).

    Returned candidates have the same shape as channel-scan candidates but with
    `link_origin="direct"` and no `slack` field. They merge through the normal
    dedupe path in merge_scan_results / atomic_scan_merge.
    """
    try:
        # config_io is in scripts/ which repo.py added to sys.path at import.
        from config_io import load_repos  # type: ignore  # noqa: WPS433
        fm, _ = load_repos()
    except Exception as exc:
        log.warning("direct-scan: could not load repos.md (%s) — skipping", exc)
        return []

    repo_entries = (fm.get("repos") if isinstance(fm, dict) else None) or []
    if not repo_entries:
        log.info("direct-scan: no repos configured in repos.md — skipping")
        return []

    candidates: list[dict] = []
    for entry in repo_entries:
        if not isinstance(entry, dict):
            continue
        host = (entry.get("host") or "github").lower()
        owner = entry.get("workspace") or entry.get("owner") or ""
        repo_name = entry.get("name") or ""
        if not owner or not repo_name:
            continue

        if host == "bitbucket":
            log.warning("direct-scan: bitbucket direct scan not implemented "
                        "for %s/%s; relying on Slack scan", owner, repo_name)
            continue

        if host != "github":
            log.warning("direct-scan: unsupported host %r for %s/%s; skipping",
                        host, owner, repo_name)
            continue

        query = f"is:open is:pr review-requested:@me repo:{owner}/{repo_name}"
        cmd = ["gh", "api", "search/issues",
               "-X", "GET", "-f", f"q={query}", "--paginate"]
        try:
            cp = subprocess.run(cmd, capture_output=True, text=True, check=True)
            items = json.loads(cp.stdout).get("items") or []
        except subprocess.CalledProcessError as exc:
            log.warning("direct-scan: gh api search failed for %s/%s (%s) — skipping",
                        owner, repo_name, (exc.stderr or "").strip()[:120])
            continue
        except Exception as exc:
            log.warning("direct-scan: error for %s/%s (%s) — skipping",
                        owner, repo_name, exc)
            continue

        for item in items:
            pr_url = item.get("pull_request", {}).get("html_url") or item.get("html_url") or ""
            if not pr_url or "/pull/" not in pr_url:
                continue
            candidates.append({
                "pr_url": pr_url,
                "supporting_docs": [],
                "related_pr_urls": [],
                "discovery_source": "direct",
                "link_origin": "direct",
            })

    return candidates


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


def _filter_by_configured_repos(candidates: list[dict], log) -> tuple[list[dict], int]:
    """Drop candidates whose repo is not in repos.md. Returns (kept, dropped_count).

    When repos.md is absent or has no entries, all candidates pass through
    (backward compat).
    """
    kept: list[dict] = []
    dropped = 0
    for c in candidates:
        try:
            p = parse_pr_url(c["pr_url"])
        except (ValueError, KeyError):
            kept.append(c)
            continue
        if is_configured_repo(p["host"], p["owner"], p["repo"]):
            kept.append(c)
        else:
            dropped += 1
            log.info("pr-scan: dropping %s/%s/%s#%s — not in configured repos",
                     p["host"], p["owner"], p["repo"], p["pr_number"])
    return kept, dropped


# ----- entrypoint ---------------------------------------------------------

_SINCE_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*(hr|h|d|w|m)$", re.I)

_UNIT_SECONDS = {
    "h": 3600,
    "hr": 3600,
    "d": 86400,
    "w": 7 * 86400,
    "m": 30 * 86400,
}


def _parse_since_seconds(since: str) -> float:
    """Parse `--since` value to seconds.

    Accepts:
      Nh / Nhr — hours (e.g. "12h", "30hr")
      Nd        — days (e.g. "30d", "7d")
      Nw        — weeks (e.g. "4w" → 28d)
      Nm        — months (e.g. "1m" → 30d, "3m" → 90d)

    Raises ValueError on unrecognised format.
    """
    m = _SINCE_RE.match(since.strip())
    if not m:
        raise ValueError(
            f"unrecognised --since format: {since!r}. "
            "Use Nh / Nhr (hours), Nd (days), Nw (weeks), or Nm (months). "
            "Example: 12h, 30d, 4w, 1m."
        )
    n = float(m.group(1))
    unit = m.group(2).lower()
    return n * _UNIT_SECONDS[unit]


def _resolve_since_days(args, slack_cfg: dict) -> int:
    """Return the scan window in whole days (for callers that need an int).

    Sub-day windows (e.g. --since 12h) are rounded up to 1 day — lossy by design.
    """
    if getattr(args, "since", None):
        try:
            seconds = _parse_since_seconds(args.since)
            return max(1, int(seconds // 86400))
        except ValueError:
            pass
    if getattr(args, "since_days", 0) and args.since_days > 0:
        return args.since_days
    if getattr(args, "since_hours", 0.0) and args.since_hours > 0:
        return max(1, int(args.since_hours / 24))
    return int(slack_cfg.get("scan_days_default", 30))


def _resolve_oldest_ts(args, slack_cfg: dict) -> tuple[str, str]:
    """Return (oldest_ts, human_description)."""
    if getattr(args, "since", None):
        try:
            seconds = _parse_since_seconds(args.since)
        except ValueError as e:
            die(str(e))
        ts_dt = datetime.now(tz=timezone.utc) - timedelta(seconds=seconds)
        ts = f"{ts_dt.timestamp():.6f}"
        return ts, f"last {args.since} (--since {args.since})"
    if args.since_hours and args.since_hours > 0:
        return hours_ago_ts(args.since_hours), f"last {args.since_hours}h"
    if args.since_days and args.since_days > 0:
        return days_ago_ts(args.since_days), f"last {args.since_days}d"
    default_days = int(slack_cfg.get("scan_days_default", 30))
    return days_ago_ts(default_days), f"last {default_days}d (config default)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-scan",
                                 description="Scan Slack channels for PR links → upsert into pr-queue.json5")
    ap.add_argument("--slack-config", default=str(DEFAULT_SLACK_CONFIG))
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    ap.add_argument("--since", default="",
                    help="scan window: Nh / Nhr (hours), Nd (days), Nw (weeks), Nm (months). "
                         "Example: 12h, 30d, 4w, 1m. Overrides --since-hours / --since-days.")
    ap.add_argument("--since-hours", type=float, default=0.0)
    ap.add_argument("--since-days", type=int, default=0)
    ap.add_argument("--channels", default="",
                    help="comma-separated channels to scan in addition to slack config")
    ap.add_argument("--channels-only", default="",
                    help="comma-separated channels to scan INSTEAD of slack config")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--include-unmapped-repos", action="store_true",
                    help="bypass the configured-repos filter; include PRs from any repo")
    ap.add_argument("--no-direct", action="store_true",
                    help="skip the direct review-requested scan (GitHub/Bitbucket API)")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="non-interactive; smart defaults")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to $ADK_DATA_HOME/logs/")
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
            f"$ADK_CONFIG_HOME/connectors/slack.md frontmatter with at least "
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
    # Tag channel-scan candidates with discovery_source (N2 traceability).
    for c in candidates:
        c.setdefault("discovery_source", "channel")
    if not quiet:
        log.info("scan_stats: %s", scan_stats)

    # N2 — user-mention scan. Runs after channel scan; dedup happens in merge.
    url_patterns = slack_cfg.get("url_patterns") or []
    user_id = slack_cfg.get("user_id") or ""
    mention_candidates: list[dict] = []
    if user_id and url_patterns:
        since_days_val = _resolve_since_days(args, slack_cfg)
        try:
            mention_client = SlackClient()
            mention_candidates = scan_user_mentions(
                mention_client, user_id, since_days_val, url_patterns, log
            )
            if not quiet:
                log.info("mention_scan: found %d candidates for user_id=%s",
                         len(mention_candidates), user_id)
        except Exception as e:
            log.warning("mention_scan: failed (%s) — skipping", e)
    elif not user_id:
        if not quiet:
            log.info("mention_scan: skipped — user_id not set in slack.md pr_reviews")

    # Direct review-requested scan (GitHub API; Bitbucket not yet implemented).
    direct_candidates: list[dict] = []
    if not getattr(args, "no_direct", False):
        direct_candidates = scan_direct_review_requests(log)
        if not quiet:
            log.info("direct_scan: found %d candidates", len(direct_candidates))

    # Merge direct candidates into the main list before the repo filter.
    if direct_candidates:
        existing_urls = {c["pr_url"] for c in candidates}
        for dc in direct_candidates:
            if dc["pr_url"] not in existing_urls:
                candidates.append(dc)
                existing_urls.add(dc["pr_url"])

    # Configured-repo filter — drop candidates not in repos.md (unless bypassed).
    if not getattr(args, "include_unmapped_repos", False):
        candidates, dropped_ch = _filter_by_configured_repos(candidates, log)
        mention_candidates, dropped_mn = _filter_by_configured_repos(mention_candidates, log)
        if not quiet and (dropped_ch or dropped_mn):
            log.info("repo-filter: dropped %d channel + %d mention candidates "
                     "(not in configured repos)", dropped_ch, dropped_mn)

    mention_kept, mention_post_stats = post_process(
        mention_candidates, slack_cfg, args.dry_run, log
    ) if mention_candidates else ([], {})

    kept, post_stats = post_process(candidates, slack_cfg, args.dry_run, log)
    if not quiet:
        log.info("post_process: %s", post_stats)

    # N4 — populate author on each kept candidate from its _meta (set by post_process).
    for c in kept + mention_kept:
        meta = c.pop("_meta", None) or {}
        author_str = meta.get("author")
        host = meta.get("host", "")
        if author_str and not c.get("author"):
            if host == "github":
                c["author"] = {
                    "display_name": author_str,
                    "host_user_id": author_str,
                    "email": None,
                }
            else:
                # Bitbucket: display_name from meta; uuid used as host_user_id
                # when the meta author is the uuid (fallback from cheap_pr_meta).
                c["author"] = {
                    "display_name": author_str,
                    "host_user_id": meta.get("author_uuid") or author_str,
                    "email": None,
                }

    all_kept = kept + [m for m in mention_kept
                       if not any(m.get("pr_url") == k.get("pr_url") for k in kept)]

    existing = read_queue(queue_path)
    reminder_stats = maybe_emit_gentle_reminders(all_kept, existing, slack_cfg, args.dry_run, log)
    if not quiet:
        log.info("gentle_reminders: %s", reminder_stats)

    # Build a fetch_state callable for N3 PR retention (re-checks open PRs not
    # seen in this scan). Wraps cheap_pr_meta + classify_pr_state.
    def _fetch_state(pr_url: str) -> str:
        try:
            meta = cheap_pr_meta(pr_url, log)
            return classify_pr_state(meta)
        except Exception:
            return "unknown"

    if not args.dry_run:
        # P0.3: atomic read → merge → write under the queue lock.
        merged = atomic_scan_merge(queue_path, all_kept, fetch_state=_fetch_state)
    else:
        merged = merge_scan_results(existing, all_kept, fetch_state=_fetch_state)
    merge_summary = merged.pop("_merge_summary", {})

    summary = {
        "queue": str(queue_path),
        "slack_config": str(slack_cfg_path),
        "window": window,
        "scan": scan_stats,
        "post_process": post_stats,
        "mention_post_process": mention_post_stats,
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
