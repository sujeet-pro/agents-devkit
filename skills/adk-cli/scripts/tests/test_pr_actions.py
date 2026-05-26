from __future__ import annotations

import json
import sys
import types
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import pr


def _queue(path: Path, row: dict) -> Path:
    path.write_text(json.dumps({"prs": [row]}, indent=2), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Existing tests (unchanged)
# ---------------------------------------------------------------------------

def test_open_prints_slack_link_from_queue(tmp_path, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })

    rc = pr.main(["--queue", str(q), "open", "https://github.com/acme/foo/pull/1",
                  "--target", "slack", "--print-only"])

    assert rc == 0
    assert "https://example.slack.com/archives/C/p1" in capsys.readouterr().out


def test_merge_status_blocks_when_not_approved(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "pending",
    })
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _url, _log: {
        "state": "OPEN",
        "merged_at": None,
    })
    monkeypatch.setattr(pr, "_task_dir", lambda _url: tmp_path / "task")

    rc = pr.main(["--queue", str(q), "merge-status", "https://github.com/acme/foo/pull/1"])

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["bucket"] == "blocked"
    assert "not approved" in out["blockers"]


def test_merge_status_allows_resolvable_comments_when_approved(tmp_path, monkeypatch, capsys):
    """When all open comments are classified resolvable (approve_ready=True)
    and the PR is approved, comments must NOT be a hard blocker.

    approve_ready=True with open comments → caveat at most, never a blocker.
    approve_ready=False or None → caveat, again not a hard blocker."""
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "comments",
        "approved_host": True,
    })
    task = tmp_path / "task"
    (task / "pr-review").mkdir(parents=True)
    (task / "pr-review" / "comment-actions.json").write_text(
        json.dumps({"approve_ready": True}), encoding="utf-8"
    )
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _url, _log: {
        "state": "OPEN",
        "merged_at": None,
    })
    monkeypatch.setattr(pr, "_task_dir", lambda _url: task)

    rc = pr.main(["--queue", str(q), "merge-status", "https://github.com/acme/foo/pull/1"])

    out = json.loads(capsys.readouterr().out)
    for b in out["blockers"]:
        assert "comment" not in b.lower(), f"comments must not be hard blockers, got {b!r}"
    # checks/mergeability are unknown in this lightweight fixture so the
    # bucket ends up "unknown" (rc=1) rather than mergeable_now.
    assert rc == 1
    assert out["bucket"] in {"unknown", "mergeable_now"}


def test_context_refresh_runs_update_slack_and_prepare(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })
    calls = []

    def fake_run(args):
        calls.append(args)
        return {"cmd": args, "rc": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(pr, "_run_adk", fake_run)

    rc = pr.main(["--queue", str(q), "context-refresh", "https://github.com/acme/foo/pull/1"])

    assert rc == 0
    assert ["pr-queue", "--queue", str(q), "update", "https://github.com/acme/foo/pull/1"] in calls
    assert ["pr-queue", "--queue", str(q), "add", "https://example.slack.com/archives/C/p1", "-y"] in calls
    assert ["pr-task", "prepare", "https://github.com/acme/foo/pull/1", "--queue", str(q)] in calls


def test_context_refresh_no_prepare_skips_prepare_even_with_docs_default(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })
    calls = []

    def fake_run(args):
        calls.append(args)
        return {"cmd": args, "rc": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(pr, "_run_adk", fake_run)

    rc = pr.main([
        "--queue", str(q),
        "context-refresh", "https://github.com/acme/foo/pull/1",
        "--no-prepare",
    ])

    assert rc == 0
    assert ["pr-queue", "--queue", str(q), "update", "https://github.com/acme/foo/pull/1"] in calls
    assert not any(call[:2] == ["pr-task", "prepare"] for call in calls)


def test_merge_is_disabled_without_config(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "approved",
        "approved_host": True,
    })
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)

    rc = pr.main(["--queue", str(q), "merge", "https://github.com/acme/foo/pull/1", "--yes"])

    assert rc == 2
    assert "API merge disabled" in capsys.readouterr().out


def test_merge_tui_confirmed_bypasses_config_gate(tmp_path, monkeypatch, capsys):
    """--tui-confirmed lets a TUI-confirmed merge skip the allow_api_merge config check.

    The merge still re-checks merge-status; here merge-status returns 1 (not
    mergeable_now) because no task dir / approval data exists — that's fine,
    we only care that the "API merge disabled" gate is NOT triggered.
    """
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "approved",
        "approved_host": True,
    })
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)
    # merge-status subprocess is called inside cmd_merge; stub it to report
    # "not mergeable_now" so the function returns 2 at that point rather than
    # trying to call gh/bitbucket.
    import subprocess as _sp
    class _CP:
        returncode = 1
        stdout = '{"bucket":"blocked","blockers":["not approved"]}'
        stderr = ""
    monkeypatch.setattr(_sp, "run", lambda *_a, **_kw: _CP())

    rc = pr.main([
        "--queue", str(q), "merge",
        "https://github.com/acme/foo/pull/1",
        "--yes", "--tui-confirmed",
    ])

    out = capsys.readouterr().out
    # Must NOT hit the config-gate branch
    assert "API merge disabled" not in out
    # Must have proceeded to the merge-status check and been blocked there
    assert rc == 2


# ---------------------------------------------------------------------------
# New tests: cmd_sync
# ---------------------------------------------------------------------------

PR_URL = "https://github.com/acme/foo/pull/1"


def _make_fake_run_adk_updating_head(q: Path, pr_url: str, new_head: str):
    """Returns a _run_adk stub that simulates pr-queue update writing a new head_sha."""
    def fake_run(args):
        if "update" in args:
            data = json.loads(q.read_text())
            for row in data["prs"]:
                if row.get("pr_url") == pr_url:
                    row["head_sha"] = new_head
            q.write_text(json.dumps(data))
        return {"cmd": args, "rc": 0, "stdout": "", "stderr": ""}
    return fake_run


def test_sync_detects_head_sha_change(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL, "head_sha": "sha_old"})
    monkeypatch.setattr(pr, "_run_adk", _make_fake_run_adk_updating_head(q, PR_URL, "sha_new"))
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _u, _l: {"state": "OPEN", "merged_at": None})

    rc = pr.main(["--queue", str(q), "sync", PR_URL, "--no-comments"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["head_changed"] is True
    assert out["head_sha"] == "sha_new"


def test_sync_marks_queued_for_index_when_prep_stale(tmp_path, monkeypatch, capsys):
    """queued_for_index=True when head_sha moved but prep_head_sha still points to old sha."""
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "head_sha": "sha_new",
        "prep_head_sha": "sha_old",
        "prep_status": "ready",
    })
    monkeypatch.setattr(pr, "_run_adk", lambda _: {"cmd": [], "rc": 0, "stdout": "", "stderr": ""})
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _u, _l: {"state": "OPEN", "merged_at": None})

    rc = pr.main(["--queue", str(q), "sync", PR_URL, "--no-comments"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["queued_for_index"] is True
    assert out["prep_status"] == "ready"


def test_sync_no_row_in_queue_still_returns_gracefully(tmp_path, monkeypatch, capsys):
    """Syncing a PR that isn't in the queue should not crash."""
    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": []}), encoding="utf-8")
    monkeypatch.setattr(pr, "_run_adk", lambda _: {"cmd": [], "rc": 0, "stdout": "", "stderr": ""})
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _u, _l: {"state": "OPEN", "merged_at": None})

    rc = pr.main(["--queue", str(q), "sync", PR_URL, "--no-comments"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pr_url"] == PR_URL
    assert out["head_sha"] is None


def test_sync_comment_activity_updates_queue(tmp_path, monkeypatch, capsys):
    """comment activity refresh writes unresolved_comment_count into the queue row."""
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL, "head_sha": "sha1"})
    monkeypatch.setattr(pr, "_run_adk", lambda _: {"cmd": [], "rc": 0, "stdout": "", "stderr": ""})
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _u, _l: {"state": "OPEN", "merged_at": None})

    import comment_activity as _ca
    monkeypatch.setattr(_ca, "fetch_comment_activity", lambda _url, **_kw: {
        "comment_activity_hash": "abc123",
        "comment_count": 3,
        "unresolved_comment_count": 2,
        "comment_activity_updated_at": "2026-05-25T00:00:00Z",
        "comment_activity_error": None,
    })

    rc = pr.main(["--queue", str(q), "sync", PR_URL])

    assert rc == 0
    import queue_io
    updated = queue_io.find_row(q, PR_URL) or {}
    assert updated.get("unresolved_comment_count") == 2


# ---------------------------------------------------------------------------
# New tests: _post_slack_merge_notification
# ---------------------------------------------------------------------------

def _make_slack_module(posted_to: list[dict], *, reply_fail: bool = False):
    """Return a fake slack_helpers module."""
    class _FakeClient:
        def post_thread_reply(self, channel_id, thread_ts, text):
            if reply_fail:
                raise RuntimeError("simulated slack error")
            posted_to.append({"channel_id": channel_id, "thread_ts": thread_ts, "text": text})
            return "ts_reply"
        def add_reaction(self, channel_id, thread_ts, name):
            pass

    m = types.ModuleType("slack_helpers")
    m.SlackClient = _FakeClient
    return m


def test_merge_posts_slack_on_success(tmp_path, monkeypatch):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "slack": {"channel_id": "C123", "thread_ts": "1234.5678",
                  "permalink": "https://acme.slack.com/archives/C123/p12345678"},
    })
    posted: list[dict] = []
    monkeypatch.setitem(sys.modules, "slack_helpers", _make_slack_module(posted))

    result = pr._post_slack_merge_notification(q, PR_URL)

    assert result["status"] == "ok"
    assert len(result["channels_posted"]) == 1
    assert result["channels_failed"] == []
    assert any("merged" in p["text"].lower() for p in posted)


def test_merge_slack_failure_is_recoverable_warning(tmp_path, monkeypatch):
    """Slack API error after merge → warn status, not exception."""
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "slack": {"channel_id": "C123", "thread_ts": "1234.5678"},
    })
    posted: list[dict] = []
    monkeypatch.setitem(sys.modules, "slack_helpers", _make_slack_module(posted, reply_fail=True))

    result = pr._post_slack_merge_notification(q, PR_URL)

    assert result["status"] == "warn"
    assert len(result["channels_failed"]) == 1
    assert result["channels_failed"][0]["error"] == "simulated slack error"


def test_merge_no_slack_context_skips_silently(tmp_path):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})

    result = pr._post_slack_merge_notification(q, PR_URL)

    assert result["status"] == "skipped"
    assert result["reason"] == "no_slack_context"


def test_merge_slack_unavailable_returns_warn(tmp_path, monkeypatch):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "slack": {"channel_id": "C123", "thread_ts": "1234.5678"},
    })
    # Make slack_helpers unimportable by removing it from sys.modules
    monkeypatch.setitem(sys.modules, "slack_helpers", None)

    result = pr._post_slack_merge_notification(q, PR_URL)

    assert result["status"] == "warn"
    assert "slack_client_unavailable" in result["reason"]


# ---------------------------------------------------------------------------
# New tests: action_availability
# ---------------------------------------------------------------------------

def test_action_availability_terminal_pr_blocks_most_actions(tmp_path):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL, "status": "merged"})

    result = pr.action_availability(PR_URL, q)

    actions = result["actions"]
    # Read-only always available
    assert actions["open_pr"]["available"] is True
    assert actions["view_log"]["available"] is True
    assert actions["global_refresh"]["available"] is True
    # Mutating + terminal = unavailable
    assert actions["merge"]["available"] is False
    assert actions["approve"]["available"] is False
    assert actions["post_comment"]["available"] is False
    assert actions["full_review"]["available"] is False
    assert actions["list_comments"]["available"] is False


def test_action_availability_open_prep_ready_pr(tmp_path, monkeypatch):
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: True)
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "status": "pending",
        "prep_status": "ready",
        "head_sha": "sha1",
        "prep_head_sha": "sha1",   # in sync — code_review_needed=True (no last_reviewed_head_sha)
    })

    result = pr.action_availability(PR_URL, q)

    actions = result["actions"]
    assert actions["full_review"]["available"] is True
    assert actions["re_review"]["available"] is True
    assert actions["approve"]["available"] is True
    assert actions["merge"]["available"] is True
    assert actions["list_comments"]["available"] is True
    assert actions["sync"]["available"] is True
    assert result["context"]["prep_status"] == "ready"


def test_action_availability_no_merge_config_blocks_merge(tmp_path, monkeypatch):
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL, "status": "approved", "approved_host": True,
    })

    result = pr.action_availability(PR_URL, q)

    assert result["actions"]["merge"]["available"] is False
    assert "allow_api_merge" in result["actions"]["merge"]["reason"]


def test_action_availability_already_approved_blocks_approve(tmp_path):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL, "status": "approved", "approved_host": True,
    })

    result = pr.action_availability(PR_URL, q)

    assert result["actions"]["approve"]["available"] is False
    assert "already approved" in result["actions"]["approve"]["reason"]


def test_action_availability_locked_pr_blocks_review(tmp_path):
    from queue_io import _now_iso
    q = _queue(tmp_path / "q.json5", {
        "pr_url": PR_URL,
        "status": "in_review",
        "taken_at": _now_iso(),
        "prep_status": "ready",
        "head_sha": "sha1",
    })

    result = pr.action_availability(PR_URL, q)

    assert result["actions"]["full_review"]["available"] is False
    assert "locked" in result["actions"]["full_review"]["reason"]


def test_action_availability_not_in_queue_returns_safe_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)
    q = tmp_path / "q.json5"
    q.write_text(json.dumps({"prs": []}), encoding="utf-8")

    result = pr.action_availability(PR_URL, q)

    assert result["pr_url"] == PR_URL
    assert result["actions"]["open_pr"]["available"] is True
    # Without a row, status defaults to "pending" (non-terminal)
    assert result["context"]["is_terminal"] is False


# ---------------------------------------------------------------------------
# New tests: cmd_approve (gate check only — no real gh call)
# ---------------------------------------------------------------------------

def test_approve_blocked_without_yes(tmp_path, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})

    rc = pr.main(["--queue", str(q), "approve", PR_URL])

    assert rc == 2
    assert "Refusing" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# New tests: cmd_list_comments
# ---------------------------------------------------------------------------

def test_list_comments_json_returns_unresolved(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})
    import comment_activity as _ca
    monkeypatch.setattr(_ca, "fetch_unresolved_comments", lambda _url, **_kw: {
        "pr_url": PR_URL,
        "host": "github",
        "count": 1,
        "items": [{"id": "1", "author": "bob", "body": "Fix this!", "path": "a.py",
                   "line": 10, "updated": "2026-05-25T00:00:00Z", "parent_id": None}],
        "resolve_support": "github_graphql_only",
        "resolve_note": "Use web UI",
    })

    rc = pr.main(["--queue", str(q), "list-comments", PR_URL, "--json"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 1
    assert out["items"][0]["body"] == "Fix this!"


def test_list_comments_returns_error_on_failure(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})
    import comment_activity as _ca
    monkeypatch.setattr(_ca, "fetch_unresolved_comments", lambda _url, **_kw: {
        "error": "network error", "host": "github", "pr_url": PR_URL,
    })

    rc = pr.main(["--queue", str(q), "list-comments", PR_URL, "--json"])

    assert rc == 1


# ---------------------------------------------------------------------------
# New tests: cmd_post_comment
# ---------------------------------------------------------------------------

def test_post_comment_blocked_without_yes(tmp_path, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})

    rc = pr.main(["--queue", str(q), "post-comment", PR_URL, "--body", "LGTM"])

    assert rc == 2
    assert "Refusing" in capsys.readouterr().out


def test_post_comment_github_success(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL})
    import subprocess as _sp
    class _CP:
        returncode = 0
    monkeypatch.setattr(_sp, "run", lambda *_a, **_kw: _CP())

    rc = pr.main(["--queue", str(q), "post-comment", PR_URL, "--body", "LGTM", "--yes"])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["status"] == "posted"


# ---------------------------------------------------------------------------
# New tests: cmd_action_availability CLI surface
# ---------------------------------------------------------------------------

def test_action_availability_cli_returns_json(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)
    q = _queue(tmp_path / "q.json5", {"pr_url": PR_URL, "status": "pending"})

    rc = pr.main(["--queue", str(q), "action-availability", PR_URL])

    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pr_url"] == PR_URL
    assert "actions" in out
    assert "context" in out
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })

    rc = pr.main(["--queue", str(q), "open", "https://github.com/acme/foo/pull/1",
                  "--target", "slack", "--print-only"])

    assert rc == 0
    assert "https://example.slack.com/archives/C/p1" in capsys.readouterr().out


def test_merge_status_blocks_when_not_approved(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "pending",
    })
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _url, _log: {
        "state": "OPEN",
        "merged_at": None,
    })
    monkeypatch.setattr(pr, "_task_dir", lambda _url: tmp_path / "task")

    rc = pr.main(["--queue", str(q), "merge-status", "https://github.com/acme/foo/pull/1"])

    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["bucket"] == "blocked"
    assert "not approved" in out["blockers"]


def test_merge_status_allows_resolvable_comments_when_approved(tmp_path, monkeypatch, capsys):
    """When all open comments are classified resolvable (approve_ready=True)
    and the PR is approved, comments must NOT be a hard blocker.

    approve_ready=True with open comments → caveat at most, never a blocker.
    approve_ready=False or None → caveat, again not a hard blocker."""
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "comments",
        "approved_host": True,
    })
    task = tmp_path / "task"
    (task / "pr-review").mkdir(parents=True)
    (task / "pr-review" / "comment-actions.json").write_text(
        json.dumps({"approve_ready": True}), encoding="utf-8"
    )
    monkeypatch.setattr(pr, "cheap_pr_meta", lambda _url, _log: {
        "state": "OPEN",
        "merged_at": None,
    })
    monkeypatch.setattr(pr, "_task_dir", lambda _url: task)

    rc = pr.main(["--queue", str(q), "merge-status", "https://github.com/acme/foo/pull/1"])

    out = json.loads(capsys.readouterr().out)
    for b in out["blockers"]:
        assert "comment" not in b.lower(), f"comments must not be hard blockers, got {b!r}"
    # checks/mergeability are unknown in this lightweight fixture so the
    # bucket ends up "unknown" (rc=1) rather than mergeable_now.
    assert rc == 1
    assert out["bucket"] in {"unknown", "mergeable_now"}


def test_context_refresh_runs_update_slack_and_prepare(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })
    calls = []

    def fake_run(args):
        calls.append(args)
        return {"cmd": args, "rc": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(pr, "_run_adk", fake_run)

    rc = pr.main(["--queue", str(q), "context-refresh", "https://github.com/acme/foo/pull/1"])

    assert rc == 0
    assert ["pr-queue", "--queue", str(q), "update", "https://github.com/acme/foo/pull/1"] in calls
    assert ["pr-queue", "--queue", str(q), "add", "https://example.slack.com/archives/C/p1", "-y"] in calls
    assert ["pr-task", "prepare", "https://github.com/acme/foo/pull/1", "--queue", str(q)] in calls


def test_context_refresh_no_prepare_skips_prepare_even_with_docs_default(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "slack": {"permalink": "https://example.slack.com/archives/C/p1"},
    })
    calls = []

    def fake_run(args):
        calls.append(args)
        return {"cmd": args, "rc": 0, "stdout": "", "stderr": ""}

    monkeypatch.setattr(pr, "_run_adk", fake_run)

    rc = pr.main([
        "--queue", str(q),
        "context-refresh", "https://github.com/acme/foo/pull/1",
        "--no-prepare",
    ])

    assert rc == 0
    assert ["pr-queue", "--queue", str(q), "update", "https://github.com/acme/foo/pull/1"] in calls
    assert not any(call[:2] == ["pr-task", "prepare"] for call in calls)


def test_merge_is_disabled_without_config(tmp_path, monkeypatch, capsys):
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "approved",
        "approved_host": True,
    })
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)

    rc = pr.main(["--queue", str(q), "merge", "https://github.com/acme/foo/pull/1", "--yes"])

    assert rc == 2
    assert "API merge disabled" in capsys.readouterr().out


def test_merge_tui_confirmed_bypasses_config_gate(tmp_path, monkeypatch, capsys):
    """--tui-confirmed lets a TUI-confirmed merge skip the allow_api_merge config check.

    The merge still re-checks merge-status; here merge-status returns 1 (not
    mergeable_now) because no task dir / approval data exists — that's fine,
    we only care that the "API merge disabled" gate is NOT triggered.
    """
    q = _queue(tmp_path / "q.json5", {
        "pr_url": "https://github.com/acme/foo/pull/1",
        "status": "approved",
        "approved_host": True,
    })
    monkeypatch.setattr(pr, "_allow_api_merge", lambda: False)
    # merge-status subprocess is called inside cmd_merge; stub it to report
    # "not mergeable_now" so the function returns 2 at that point rather than
    # trying to call gh/bitbucket.
    import subprocess as _sp
    class _CP:
        returncode = 1
        stdout = '{"bucket":"blocked","blockers":["not approved"]}'
        stderr = ""
    monkeypatch.setattr(_sp, "run", lambda *_a, **_kw: _CP())

    rc = pr.main([
        "--queue", str(q), "merge",
        "https://github.com/acme/foo/pull/1",
        "--yes", "--tui-confirmed",
    ])

    out = capsys.readouterr().out
    # Must NOT hit the config-gate branch
    assert "API merge disabled" not in out
    # Must have proceeded to the merge-status check and been blocked there
    assert rc == 2
