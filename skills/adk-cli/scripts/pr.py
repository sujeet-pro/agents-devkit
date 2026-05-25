"""Higher-level per-PR actions shared by CLI and TUI."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
sys.path.insert(0, str(THIS_DIR.parent.parent / "adk-pr-review" / "scripts"))
sys.path.insert(0, str(THIS_DIR.parent.parent.parent / "scripts"))

from _common import parse_pr_url, task_dir_for  # type: ignore  # noqa: E402
from pr_scan import cheap_pr_meta  # type: ignore  # noqa: E402
from queue_io import (  # type: ignore  # noqa: E402
    DEFAULT_QUEUE_PATH, TERMINAL_STATUSES,
    find_row, read_queue, update_pr_entry, _now_iso,
    code_review_needed, comment_review_needed, classify_pr_state,
    slack_threads_for,
    STATUS_APPROVED, STATUS_MERGED,
    PREP_READY,
)
from run_state import file_link  # type: ignore  # noqa: E402


def cmd_open(args) -> int:
    target = args.target
    links = _links_for(args.pr_url, Path(args.queue).expanduser())
    url = links.get(target)
    if not url:
        print(json.dumps({"status": "missing", "target": target, "links": links}, indent=2))
        return 1
    if args.print_only:
        print(url)
        return 0
    return _open_url(url)


def cmd_context_refresh(args) -> int:
    queue = Path(args.queue).expanduser()
    steps: list[dict] = []
    steps.append(_run_adk(["pr-queue", "--queue", str(queue), "update", args.pr_url]))
    row = find_row(queue, args.pr_url) or {}
    if args.slack:
        for slack in _slack_targets(row):
            permalink = slack.get("permalink")
            if permalink:
                steps.append(_run_adk(["pr-queue", "--queue", str(queue), "add", permalink, "-y"]))
    if args.prepare:
        prep = ["pr-task", "prepare", args.pr_url, "--queue", str(queue)]
        if args.rebuild:
            prep.append("--rebuild")
        steps.append(_run_adk(prep))
    status = "ok" if all(s["rc"] == 0 for s in steps) else "failed"
    print(json.dumps({"status": status, "pr_url": args.pr_url, "steps": steps}, indent=2))
    return 0 if status == "ok" else 1


def cmd_merge_status(args) -> int:
    queue_path = Path(args.queue).expanduser()
    row = find_row(queue_path, args.pr_url) or {}
    meta = cheap_pr_meta(args.pr_url, _NullLog())
    task_dir = _task_dir(args.pr_url)
    pr_json = _read_json(task_dir / "pr.json")
    comment_actions = _read_json(task_dir / "comment-actions.json")
    approved_host = bool(row.get("approved_host")) or (
        pr_json.get("reviewDecision") in {"APPROVED"}
        or pr_json.get("review_decision") in {"APPROVED"}
    )
    recommendation = row.get("recommendation") or pr_json.get("recommendation")
    approve_ready = comment_actions.get("approve_ready")
    unresolved_known = None if approve_ready is None else not bool(approve_ready)
    status = row.get("status") or ""
    open_comments = status == "comments"
    checks = pr_json.get("checks") or pr_json.get("status_checks") or {}
    checks_state = _checks_state(checks)
    mergeability = _mergeability(pr_json)
    origin_state = "unknown"
    if meta.get("merged_at"):
        origin_state = "merged"
    elif (meta.get("state") or "").upper() in {"CLOSED", "DECLINED", "SUPERSEDED"}:
        origin_state = "closed"
    elif meta and not meta.get("error"):
        origin_state = "open"
    blockers = []
    if origin_state != "open":
        blockers.append(f"origin state is {origin_state}")
    if not approved_host and recommendation != "approve":
        blockers.append("not approved")
    comments_blocking = unresolved_known is True or (open_comments and approve_ready is not True)
    if comments_blocking:
        blockers.append("unresolved or unclassified comments")
    if checks_state == "failed":
        blockers.append("checks failing")
    if mergeability == "blocked":
        blockers.append("not mergeable")
    bucket = "mergeable_now" if not blockers else "blocked"
    if checks_state == "unknown" or mergeability == "unknown":
        bucket = "unknown" if not blockers else "blocked"
    out = {
        "pr_url": args.pr_url,
        "bucket": bucket,
        "blockers": blockers,
        "origin_state": origin_state,
        "approved_host": approved_host,
        "recommendation": recommendation,
        "open_comments": open_comments,
        "approve_ready": approve_ready,
        "checks": checks_state,
        "mergeability": mergeability,
        "links": _links_for(args.pr_url, queue_path),
    }
    print(json.dumps(out, indent=2))
    return 0 if bucket == "mergeable_now" else 1


def cmd_merge(args) -> int:
    tui_confirmed = getattr(args, "tui_confirmed", False)
    if not _allow_api_merge() and not tui_confirmed:
        print("API merge disabled. Set pr_actions.allow_api_merge=true in adk-cli.json5 to enable.")
        return 2
    if not args.yes:
        print("Refusing to merge without --yes. Re-run after checking `adk pr merge-status`.")
        return 2
    status_cp = subprocess.run(
        [sys.executable, __file__, "--queue", args.queue, "merge-status", args.pr_url],
        text=True, capture_output=True, check=False,
    )
    if status_cp.returncode != 0:
        print(status_cp.stdout or status_cp.stderr)
        print("Refusing to merge because merge-status is not mergeable_now.")
        return 2
    if args.dry_run:
        print(json.dumps({"status": "dry-run", "would_merge": args.pr_url}, indent=2))
        return 0
    parsed = parse_pr_url(args.pr_url)
    queue_path = Path(args.queue).expanduser()
    if parsed["host"] == "github":
        cmd = ["gh", "pr", "merge", str(parsed["pr_number"]),
               "--repo", f"{parsed['owner']}/{parsed['repo']}", f"--{args.method}"]
        if args.confirm_head:
            cmd += ["--match-head-commit", args.confirm_head]
        merge_rc = subprocess.run(cmd, check=False).returncode
    elif parsed["host"] == "bitbucket":
        merge_rc = _merge_bitbucket(parsed, args)
    else:
        print("Unsupported PR host for API merge.")
        return 2
    if merge_rc == 0:
        slack_result = _post_slack_merge_notification(queue_path, args.pr_url)
        if slack_result.get("status") not in {"ok", "skipped"}:
            print(
                f"[warn] Slack notification after merge failed: "
                f"{slack_result.get('reason') or slack_result.get('channels_failed')}"
            )
    return merge_rc


def cmd_sync(args) -> int:
    """Per-PR sync: refresh origin metadata + comment activity, report state.

    Detects head_sha changes and outputs queued_for_index / needs_re_review
    signals so callers (TUI, CI scripts) know whether to re-prepare or re-review.
    Never mutates prep_status — that is owned by `pr-task prepare`.
    """
    queue_path = Path(args.queue).expanduser()
    old_row = find_row(queue_path, args.pr_url) or {}
    old_head = old_row.get("head_sha")

    steps: list[dict] = []
    steps.append(_run_adk(["pr-queue", "--queue", str(queue_path), "update", args.pr_url]))

    if not args.no_comments:
        try:
            from comment_activity import fetch_comment_activity  # type: ignore
            activity = fetch_comment_activity(args.pr_url)
            if "error" not in activity:
                field_updates = {
                    k: v for k, v in activity.items()
                    if k in ("comment_activity_hash", "comment_count",
                             "unresolved_comment_count", "comment_activity_updated_at",
                             "comment_activity_error")
                }
                if field_updates and find_row(queue_path, args.pr_url) is not None:
                    update_pr_entry(queue_path, args.pr_url, field_updates)
                steps.append({
                    "step": "comment_activity", "rc": 0, "status": "ok",
                    "unresolved": activity.get("unresolved_comment_count", 0),
                })
            else:
                steps.append({
                    "step": "comment_activity", "rc": 1, "status": "warn",
                    "error": activity.get("error"),
                })
        except Exception as e:
            steps.append({"step": "comment_activity", "rc": 1, "status": "warn", "error": str(e)})

    updated_row = find_row(queue_path, args.pr_url) or {}
    new_head = updated_row.get("head_sha")
    prep_head = updated_row.get("prep_head_sha")
    prep_status = updated_row.get("prep_status") or "pending"
    head_changed = bool(old_head and new_head and old_head != new_head)
    queued_for_index = bool(new_head) and (
        prep_status != PREP_READY
        or (prep_head is not None and prep_head != new_head)
    )

    meta = cheap_pr_meta(args.pr_url, _NullLog())
    origin_state = classify_pr_state(meta) if meta and not meta.get("error") else "unknown"

    overall = "ok" if all(s.get("rc", 0) == 0 for s in steps) else "warn"
    out = {
        "pr_url": args.pr_url,
        "status": overall,
        "head_sha": new_head,
        "head_changed": head_changed,
        "queued_for_index": queued_for_index,
        "needs_re_review": code_review_needed(updated_row) or comment_review_needed(updated_row),
        "code_review_needed": code_review_needed(updated_row),
        "comment_review_needed": comment_review_needed(updated_row),
        "prep_status": prep_status,
        "unresolved_comment_count": updated_row.get("unresolved_comment_count"),
        "origin_state": origin_state,
        "steps": steps,
    }
    print(json.dumps(out, indent=2))
    return 0 if overall == "ok" else 1


def cmd_approve(args) -> int:
    """Approve a PR on its host platform. Shared-state action — requires --yes."""
    if not args.yes:
        print("Refusing to approve without --yes. Review the PR first, then re-run with --yes.")
        return 2
    parsed = parse_pr_url(args.pr_url)
    queue_path = Path(args.queue).expanduser()
    if parsed["host"] == "github":
        cmd = ["gh", "pr", "review", str(parsed["pr_number"]),
               "--repo", f"{parsed['owner']}/{parsed['repo']}", "--approve"]
        if args.body:
            cmd += ["--body", args.body]
        rc = subprocess.run(cmd, check=False).returncode
    elif parsed["host"] == "bitbucket":
        rc = _approve_bitbucket(parsed)
    else:
        print(f"Unsupported host for API approval: {parsed['host']}")
        return 2
    if rc == 0:
        update_pr_entry(queue_path, args.pr_url, {
            "approved_host": True,
            "status": STATUS_APPROVED,
            "last_checked_at": _now_iso(),
        })
        print(json.dumps({"status": "approved", "pr_url": args.pr_url}, indent=2))
    return rc


def cmd_list_comments(args) -> int:
    """List open/unresolved comments for a PR (read-only)."""
    from comment_activity import fetch_unresolved_comments  # type: ignore
    result = fetch_unresolved_comments(args.pr_url)
    if args.json or "error" in result:
        print(json.dumps(result, indent=2))
        return 0 if "error" not in result else 1
    items = result.get("items") or []
    count = result.get("count", 0)
    host = result.get("host", "unknown")
    print(f"\nOpen comments for {args.pr_url}")
    print(f"Host: {host}  |  Count: {count}")
    if result.get("resolve_note"):
        print(f"Note: {result['resolve_note']}")
    print()
    for item in items:
        loc = f" [{item['path']}:{item.get('line') or '?'}]" if item.get("path") else ""
        parent = f" (reply to {item['parent_id']})" if item.get("parent_id") else ""
        body_preview = (item.get("body") or "")[:200].replace("\n", " ")
        print(f"  [{item.get('id')}]{loc}{parent}")
        print(f"  @{item.get('author', 'unknown')} · {(item.get('updated') or '')[:19]}")
        print(f"  {body_preview}")
        print()
    return 0


def cmd_post_comment(args) -> int:
    """Post a generic comment on a PR. Shared-state action — requires --yes."""
    if not args.yes:
        print("Refusing to post without --yes. Check the comment body, then re-run with --yes.")
        return 2
    parsed = parse_pr_url(args.pr_url)
    if parsed["host"] == "github":
        cmd = [
            "gh", "api",
            f"repos/{parsed['owner']}/{parsed['repo']}/issues/{parsed['pr_number']}/comments",
            "-f", f"body={args.body}",
        ]
        rc = subprocess.run(cmd, capture_output=True, check=False).returncode
        if rc != 0:
            print(f"Failed to post comment (rc={rc}).")
        else:
            print(json.dumps({"status": "posted", "pr_url": args.pr_url}, indent=2))
        return rc
    if parsed["host"] == "bitbucket":
        return _post_comment_bitbucket(parsed, args.body)
    print(f"Unsupported host for posting comments: {parsed['host']}")
    return 2


def cmd_action_availability(args) -> int:
    """Print per-action availability + gates for a PR as JSON."""
    queue_path = Path(args.queue).expanduser()
    result = action_availability(args.pr_url, queue_path)
    print(json.dumps(result, indent=2))
    return 0


def action_availability(pr_url: str, queue_path: Path) -> dict:
    """Return per-action availability and gates for a PR.

    TUI integration: pass the returned `actions` dict to PrActionScreen to
    filter the shown actions based on `available` + `gate`.

    Gates:
      read_only    — no side effects; always callable.
      shared_state — mutates queue or remote state; requires --yes / TUI confirm.
      merge_gate   — requires allow_api_merge config + --yes + tui_confirmed.
    """
    from queue_io import review_work_needed, WORK_NONE  # type: ignore
    row = find_row(queue_path, pr_url) or {}
    status = row.get("status") or "pending"
    is_terminal = status in TERMINAL_STATUSES
    is_locked = bool(row.get("taken_at"))
    prep_status = row.get("prep_status") or "pending"
    prep_ready = prep_status == PREP_READY
    approved_host = bool(row.get("approved_host"))
    has_slack = bool(_slack_targets(row))
    allow_merge = _allow_api_merge()
    work = review_work_needed(row)

    def _act(avail: bool, reason: str, gate: str) -> dict:
        return {"available": avail, "reason": reason, "gate": gate}

    return {
        "pr_url": pr_url,
        "actions": {
            "open_pr": _act(True, "always available", "read_only"),
            "open_slack": _act(
                has_slack,
                "no slack context" if not has_slack else "available",
                "read_only",
            ),
            "view_log": _act(True, "always available", "read_only"),
            "list_comments": _act(
                not is_terminal,
                "terminal PR" if is_terminal else "available",
                "read_only",
            ),
            "sync": _act(
                not is_terminal,
                "terminal PR" if is_terminal else "available",
                "read_only",
            ),
            "global_refresh": _act(True, "always available", "read_only"),
            "post_comment": _act(
                not is_terminal,
                "terminal PR" if is_terminal else "available",
                "shared_state",
            ),
            "status_update": _act(
                not is_terminal,
                "terminal PR" if is_terminal else "available",
                "shared_state",
            ),
            "full_review": _act(
                not is_terminal and not is_locked and work != WORK_NONE,
                ("terminal PR" if is_terminal
                 else "locked by active review" if is_locked
                 else "no review work pending" if work == WORK_NONE
                 else "available"),
                "shared_state",
            ),
            "re_review": _act(
                not is_terminal and not is_locked and prep_ready,
                ("terminal PR" if is_terminal
                 else "locked by active review" if is_locked
                 else "prep not ready" if not prep_ready
                 else "available"),
                "shared_state",
            ),
            "approve": _act(
                not is_terminal and not approved_host,
                ("terminal PR" if is_terminal
                 else "already approved on host" if approved_host
                 else "available"),
                "shared_state",
            ),
            "merge": _act(
                not is_terminal and allow_merge,
                ("terminal PR" if is_terminal
                 else "allow_api_merge not configured (set pr_actions.allow_api_merge=true)"
                 if not allow_merge else "available"),
                "merge_gate",
            ),
        },
        "context": {
            "status": status,
            "is_terminal": is_terminal,
            "is_locked": is_locked,
            "prep_status": prep_status,
            "approved_host": approved_host,
            "has_slack": has_slack,
            "allow_api_merge": allow_merge,
            "review_work": work,
        },
    }


def _post_slack_merge_notification(queue_path: Path, pr_url: str) -> dict:
    """Post a Slack reply + reaction when a PR is merged.

    Returns {status, channels_posted, channels_failed} or {status, reason} when
    skipped. Never raises — failures produce recoverable warn status so the merge
    result is not rolled back.
    """
    row = find_row(queue_path, pr_url) or {}
    threads = _slack_targets(row)
    if not threads:
        return {"status": "skipped", "reason": "no_slack_context"}

    try:
        from slack_helpers import SlackClient  # type: ignore
        client = SlackClient()
    except Exception as e:
        return {
            "status": "warn",
            "reason": f"slack_client_unavailable: {e}",
            "channels_posted": [],
            "channels_failed": [],
        }

    text = f":merged: PR merged: {pr_url}"
    posted: list[dict] = []
    failed: list[dict] = []
    for slack in threads:
        channel_id = slack.get("channel_id")
        thread_ts = slack.get("thread_ts") or slack.get("message_ts")
        if not channel_id or not thread_ts:
            continue
        try:
            reply_ts = client.post_thread_reply(channel_id, thread_ts, text)
            posted.append({"channel_id": channel_id, "reply_ts": reply_ts})
        except Exception as e:
            failed.append({"channel_id": channel_id, "error": str(e)})
            continue
        try:
            client.add_reaction(channel_id, thread_ts, "white_check_mark")
        except Exception:
            pass  # reaction is best-effort

    if posted:
        try:
            update_pr_entry(queue_path, pr_url, {"slack_merge_notified_at": _now_iso()})
        except Exception:
            pass

    status = "ok" if posted and not failed else ("warn" if failed else "skipped")
    return {"status": status, "channels_posted": posted, "channels_failed": failed}


def _links_for(pr_url: str, queue_path: Path) -> dict[str, str]:
    row = find_row(queue_path, pr_url) or {}
    links = {"pr": pr_url}
    slack = row.get("slack") if isinstance(row.get("slack"), dict) else {}
    if slack.get("permalink"):
        links["slack"] = slack["permalink"]
    try:
        td = _task_dir(pr_url)
        links["task-dir"] = file_link(td) or ""
        for key, name in (("report", "report.md"), ("findings", "findings.md")):
            path = td / name
            if path.exists():
                links[key] = file_link(path) or ""
    except Exception:
        pass
    return {k: v for k, v in links.items() if v}


def _task_dir(pr_url: str) -> Path:
    parsed = parse_pr_url(pr_url)
    return task_dir_for(parsed["repo"], parsed["pr_number"])


def _run_adk(args: list[str]) -> dict:
    adk = Path(__file__).resolve().parents[3] / "bin" / "adk"
    cmd = [str(adk), *args]
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return {
        "cmd": cmd,
        "rc": cp.returncode,
        "stdout": cp.stdout[-2000:],
        "stderr": cp.stderr[-2000:],
    }


def _slack_targets(row: dict) -> list[dict]:
    out = []
    if isinstance(row.get("slack"), dict):
        out.append(row["slack"])
    if isinstance(row.get("slack_threads"), list):
        out.extend([s for s in row["slack_threads"] if isinstance(s, dict)])
    seen = set()
    deduped = []
    for item in out:
        key = item.get("permalink") or (item.get("channel_id"), item.get("thread_ts"))
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)
    return deduped


def _open_url(url: str) -> int:
    if sys.platform == "darwin":
        return subprocess.run(["open", url], check=False).returncode
    if sys.platform.startswith("linux"):
        return subprocess.run(["xdg-open", url], check=False).returncode
    print(url)
    return 0


def _read_json(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _checks_state(checks) -> str:
    if not checks:
        return "unknown"
    text = json.dumps(checks).lower()
    if any(word in text for word in ("failure", "failed", "error", "cancelled")):
        return "failed"
    if any(word in text for word in ("pending", "queued", "in_progress")):
        return "pending"
    if any(word in text for word in ("success", "passed", "pass")):
        return "passing"
    return "unknown"


def _mergeability(pr_json: dict) -> str:
    if not pr_json:
        return "unknown"
    raw = pr_json.get("raw") if isinstance(pr_json.get("raw"), dict) else {}
    mergeable = pr_json.get("mergeable", raw.get("mergeable"))
    status = str(pr_json.get("merge_status") or raw.get("mergeStateStatus") or "").lower()
    if mergeable is False or status in {"conflicting", "cannot_be_merged", "not_mergeable", "dirty"}:
        return "blocked"
    if mergeable is True or status in {"clean", "unstable", "has_hooks"}:
        return "mergeable"
    return "unknown"


def _allow_api_merge() -> bool:
    try:
        from config_io import get_adk_cli  # type: ignore
        return bool(get_adk_cli("pr_actions", "allow_api_merge", default=False))
    except Exception:
        return False


def _merge_bitbucket(parsed: dict, args) -> int:
    try:
        import requests
    except ImportError:
        print("Bitbucket merge requires the `requests` package.")
        return 2
    tok = os.environ.get("BITBUCKET_TOKEN_CRED") or os.environ.get("BITBUCKET_TOKEN")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        print("BITBUCKET_TOKEN_CRED not set; cannot merge via Bitbucket API.")
        return 2
    auth = (user, tok) if user else None
    headers = {"Accept": "application/json"}
    if not auth:
        headers["Authorization"] = f"Bearer {tok}"
    url = (
        f"https://api.bitbucket.org/2.0/repositories/"
        f"{parsed['owner']}/{parsed['repo']}/pullrequests/{parsed['pr_number']}/merge"
    )
    strategy = {"merge": "merge_commit", "squash": "squash", "rebase": "fast_forward"}.get(args.method)
    payload = {"merge_strategy": strategy} if strategy else {}
    response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=30)
    if response.status_code not in {200, 201, 202}:
        print(f"Bitbucket merge failed: HTTP {response.status_code} {response.text[:300]}")
        return 1
    print(json.dumps({"status": "merged", "pr_url": response.json().get("links", {}).get("html", {}).get("href")}, indent=2))
    return 0


def _approve_bitbucket(parsed: dict) -> int:
    try:
        import requests
    except ImportError:
        print("Bitbucket approve requires the `requests` package.")
        return 2
    tok = os.environ.get("BITBUCKET_TOKEN_CRED") or os.environ.get("BITBUCKET_TOKEN")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        print("BITBUCKET_TOKEN_CRED not set; cannot approve via Bitbucket API.")
        return 2
    auth = (user, tok) if user else None
    headers = {"Accept": "application/json"}
    if not auth:
        headers["Authorization"] = f"Bearer {tok}"
    url = (
        f"https://api.bitbucket.org/2.0/repositories/"
        f"{parsed['owner']}/{parsed['repo']}/pullrequests/{parsed['pr_number']}/approve"
    )
    response = requests.post(url, auth=auth, headers=headers, timeout=30)
    if response.status_code not in {200, 201}:
        print(f"Bitbucket approve failed: HTTP {response.status_code} {response.text[:300]}")
        return 1
    return 0


def _post_comment_bitbucket(parsed: dict, body: str) -> int:
    try:
        import requests
    except ImportError:
        print("Bitbucket comment posting requires the `requests` package.")
        return 2
    tok = os.environ.get("BITBUCKET_TOKEN_CRED") or os.environ.get("BITBUCKET_TOKEN")
    user = os.environ.get("BITBUCKET_USERNAME")
    if not tok:
        print("BITBUCKET_TOKEN_CRED not set; cannot post via Bitbucket API.")
        return 2
    auth = (user, tok) if user else None
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if not auth:
        headers["Authorization"] = f"Bearer {tok}"
    url = (
        f"https://api.bitbucket.org/2.0/repositories/"
        f"{parsed['owner']}/{parsed['repo']}/pullrequests/{parsed['pr_number']}/comments"
    )
    payload = {"content": {"raw": body}}
    response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=30)
    if response.status_code not in {200, 201}:
        print(f"Bitbucket post comment failed: HTTP {response.status_code} {response.text[:300]}")
        return 1
    pr_ref = f"{parsed['owner']}/{parsed['repo']}/pull-requests/{parsed['pr_number']}"
    print(json.dumps({"status": "posted", "pr_url": pr_ref}, indent=2))
    return 0


class _NullLog:
    def warning(self, *_args, **_kwargs):
        return None

    def info(self, *_args, **_kwargs):
        return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr")
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_open = sub.add_parser("open", help="open a PR-related link")
    sp_open.add_argument("pr_url")
    sp_open.add_argument("--target", choices=("pr", "slack", "log", "report", "findings", "task-dir"),
                         default="pr")
    sp_open.add_argument("--print-only", action="store_true")
    sp_open.set_defaults(func=cmd_open)

    sp_ctx = sub.add_parser("context-refresh", help="refresh origin + Slack/docs context")
    sp_ctx.add_argument("pr_url")
    sp_ctx.add_argument("--slack", action="store_true", default=True)
    sp_ctx.add_argument("--no-slack", dest="slack", action="store_false")
    sp_ctx.add_argument("--docs", action="store_true", default=True)
    sp_ctx.add_argument("--no-docs", dest="docs", action="store_false")
    sp_ctx.add_argument("--prepare", action="store_true", default=True)
    sp_ctx.add_argument("--no-prepare", dest="prepare", action="store_false")
    sp_ctx.add_argument("--rebuild", action="store_true")
    sp_ctx.set_defaults(func=cmd_context_refresh)

    sp_ms = sub.add_parser("merge-status", help="show whether a PR can merge now")
    sp_ms.add_argument("pr_url")
    sp_ms.set_defaults(func=cmd_merge_status)

    sp_merge = sub.add_parser("merge", help="merge a PR via provider API when explicitly enabled")
    sp_merge.add_argument("pr_url")
    sp_merge.add_argument("--method", choices=("merge", "squash", "rebase"), default="merge")
    sp_merge.add_argument("--confirm-head", default=None)
    sp_merge.add_argument("--dry-run", action="store_true")
    sp_merge.add_argument("-y", "--yes", action="store_true")
    sp_merge.add_argument(
        "--tui-confirmed", dest="tui_confirmed", action="store_true",
        help="bypass allow_api_merge config check when the TUI has already obtained interactive confirmation",
    )
    sp_merge.set_defaults(func=cmd_merge)

    sp_sync = sub.add_parser("sync", help="per-PR metadata + comment refresh; detect head_sha change")
    sp_sync.add_argument("pr_url")
    sp_sync.add_argument("--no-comments", dest="no_comments", action="store_true",
                         help="skip comment activity refresh (faster, metadata only)")
    sp_sync.set_defaults(func=cmd_sync)

    sp_app = sub.add_parser("approve", help="approve a PR on its host platform (shared state; --yes required)")
    sp_app.add_argument("pr_url")
    sp_app.add_argument("--body", default=None, help="optional approval message body")
    sp_app.add_argument("-y", "--yes", action="store_true")
    sp_app.set_defaults(func=cmd_approve)

    sp_lc = sub.add_parser("list-comments", help="list open/unresolved comments for a PR (read-only)")
    sp_lc.add_argument("pr_url")
    sp_lc.add_argument("--json", dest="json", action="store_true", help="emit raw JSON output")
    sp_lc.set_defaults(func=cmd_list_comments)

    sp_pc = sub.add_parser("post-comment", help="post a generic comment on a PR (shared state; --yes required)")
    sp_pc.add_argument("pr_url")
    sp_pc.add_argument("--body", required=True, help="comment text to post")
    sp_pc.add_argument("-y", "--yes", action="store_true")
    sp_pc.set_defaults(func=cmd_post_comment)

    sp_aa = sub.add_parser("action-availability", help="show which actions are available for a PR")
    sp_aa.add_argument("pr_url")
    sp_aa.set_defaults(func=cmd_action_availability)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
