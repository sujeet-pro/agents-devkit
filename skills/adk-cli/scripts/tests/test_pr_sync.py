"""Tests for `adk pr-sync` — the 5-step composer.

Each step shells into the sibling module's `main()`. We stub those out and
assert pr-sync invokes them in the right order with the right argv. The
real work of each step is covered by its own test file.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

import pr_sync


@pytest.fixture
def stubbed_steps(monkeypatch):
    """Replace each step's `main()` with a tracer; return the trace list."""
    trace: list[tuple[str, list]] = []

    def stub_scan(argv=None):
        trace.append(("pr-scan", list(argv or [])))
        return 0

    def stub_queue(argv=None):
        trace.append(("pr-queue", list(argv or [])))
        return 0

    def stub_task(argv=None):
        trace.append(("pr-task", list(argv or [])))
        return 0

    # The actual modules are imported lazily inside pr_sync.main; the import
    # statements there bind the name at call time, so we patch the modules'
    # `main` attribute directly via sys.modules.
    import pr_scan, pr_queue, pr_task, repo
    monkeypatch.setattr(pr_scan, "main", stub_scan)
    monkeypatch.setattr(pr_queue, "main", stub_queue)
    monkeypatch.setattr(pr_task, "main", stub_task)
    # Step 5.6 (auto-base cleanup) calls repo.cmd_auto_bases_clean directly;
    # stub it so unit tests don't hit the real disk / scan REPOS_ROOT.
    def stub_demote(ns):
        trace.append(("auto-base-clean", []))
        import json as _j
        print(_j.dumps({"action": "noop", "count": 0}))
        return 0
    monkeypatch.setattr(repo, "cmd_auto_bases_clean", stub_demote)
    return trace


def test_sync_runs_all_seven_steps_in_order(stubbed_steps):
    rc = pr_sync.main(["--queue", "/tmp/q.json5"])
    assert rc == 0
    names = [step for step, _ in stubbed_steps]
    assert names == [
        "pr-scan",            # 1
        "pr-queue",           # 2: update --all
        "pr-queue",           # 3: clean (merged + closed)
        "pr-task",            # 4: clean-orphans
        "pr-queue",           # 5: remind
        # 5.5 (base-index audit) is in-process, not a stubbed module call.
        "auto-base-clean",    # 5.6
        "pr-task",            # 6: prepare --all
    ]
    # Step-2 invokes `update --all`; step-3 invokes plain `clean`.
    assert "update" in stubbed_steps[1][1]
    assert "--all" in stubbed_steps[1][1]
    assert "clean" in stubbed_steps[2][1]
    assert "clean-orphans" in stubbed_steps[3][1]
    # Step 5: remind
    assert "remind" in stubbed_steps[4][1]
    # Step 6: prepare --all (post-cleanup)
    assert "prepare" in stubbed_steps[6][1]
    assert "--all" in stubbed_steps[6][1]


def test_sync_no_scan_skips_step_1(stubbed_steps):
    pr_sync.main(["--no-scan", "--queue", "/tmp/q.json5"])
    names = [step for step, _ in stubbed_steps]
    # pr-scan not called.
    assert "pr-scan" not in names
    # The remaining 5 steps still ran.
    assert names.count("pr-queue") == 3       # update + clean + remind
    assert names.count("pr-task") == 2        # clean-orphans + prepare


def test_sync_no_prepare_skips_step_6(stubbed_steps):
    pr_sync.main(["--no-prepare", "--queue", "/tmp/q.json5"])
    # pr-task is called only once (clean-orphans), not twice.
    task_calls = [argv for step, argv in stubbed_steps if step == "pr-task"]
    assert len(task_calls) == 1
    assert "clean-orphans" in task_calls[0]


def test_sync_no_remind_skips_step_5(stubbed_steps):
    pr_sync.main(["--no-remind", "--queue", "/tmp/q.json5"])
    queue_calls = [argv for step, argv in stubbed_steps if step == "pr-queue"]
    # Two pr-queue calls (update + clean), not three.
    assert len(queue_calls) == 2
    assert not any("remind" in argv for argv in queue_calls)


def test_sync_remind_actual_by_default(stubbed_steps):
    """Updated semantics: reminders post by default. `--no-remind` skips the
    step; `--dry-run` previews without posting."""
    pr_sync.main(["--queue", "/tmp/q.json5"])
    queue_calls = [argv for step, argv in stubbed_steps if step == "pr-queue"]
    remind_argv = next(argv for argv in queue_calls if "remind" in argv)
    assert "--dry-run" not in remind_argv


def test_sync_dry_run_previews_reminders(stubbed_steps):
    pr_sync.main(["--queue", "/tmp/q.json5", "--dry-run"])
    queue_calls = [argv for step, argv in stubbed_steps if step == "pr-queue"]
    remind_argv = next(argv for argv in queue_calls if "remind" in argv)
    assert "--dry-run" in remind_argv


def test_sync_remind_threshold_forwarded(stubbed_steps):
    pr_sync.main([
        "--queue", "/tmp/q.json5",
        "--remind-threshold-hours", "48",
    ])
    queue_calls = [argv for step, argv in stubbed_steps if step == "pr-queue"]
    remind_argv = next(argv for argv in queue_calls if "remind" in argv)
    assert "--threshold-hours" in remind_argv
    assert "48.0" in remind_argv


def test_sync_orphan_step_actual_by_default(stubbed_steps):
    """Updated semantics: orphan cleanup defaults to actually deleting.
    `--no-clean-orphans` skips the step; `--dry-run` previews without deleting."""
    pr_sync.main(["--queue", "/tmp/q.json5"])
    task_calls = [argv for step, argv in stubbed_steps if step == "pr-task"]
    orphan_argv = task_calls[0]
    assert "clean-orphans" in orphan_argv
    assert "-y" in orphan_argv
    assert "--dry-run" not in orphan_argv


def test_sync_dry_run_previews_orphans(stubbed_steps):
    pr_sync.main(["--queue", "/tmp/q.json5", "--dry-run"])
    task_calls = [argv for step, argv in stubbed_steps if step == "pr-task"]
    orphan_argv = task_calls[0]
    assert "--dry-run" in orphan_argv
    assert "-y" not in orphan_argv


def test_sync_no_clean_orphans_skips_step(stubbed_steps):
    pr_sync.main(["--queue", "/tmp/q.json5", "--no-clean-orphans"])
    task_calls = [argv for step, argv in stubbed_steps if step == "pr-task"]
    # pr-task only invoked for prepare; clean-orphans never ran.
    assert not any("clean-orphans" in argv for argv in task_calls)


def test_sync_propagates_scan_flags(stubbed_steps):
    pr_sync.main([
        "--queue", "/tmp/q.json5",
        "--since-hours", "24",
        "--channels", "#eng-prs,#sf-prs",
    ])
    scan_argv = stubbed_steps[0][1]
    assert scan_argv[0] == "--queue"
    assert "--since-hours" in scan_argv
    # --since-hours is parsed as a float; stringified with the trailing zero.
    assert "24.0" in scan_argv
    assert "--channels" in scan_argv
    assert "#eng-prs,#sf-prs" in scan_argv


def test_sync_forwards_prepare_flags(stubbed_steps):
    pr_sync.main([
        "--queue", "/tmp/q.json5",
        "--rebuild", "--detailed",
    ])
    task_calls = [argv for step, argv in stubbed_steps if step == "pr-task"]
    prep_argv = task_calls[-1]
    assert "prepare" in prep_argv
    assert "--all" in prep_argv
    assert "--rebuild" in prep_argv
    assert "--detailed" in prep_argv


def test_quiet_mode_emits_events_and_forwards_quiet(stubbed_steps, capsys):
    rc = pr_sync.main(["--queue", "/tmp/q.json5", "--quiet"])

    out = capsys.readouterr().out
    assert rc == 0
    assert "ADK_EVENT" in out
    assert "--quiet" in stubbed_steps[0][1]
    assert "--quiet" in stubbed_steps[-1][1]
    assert "adk pr-sync complete" not in out


def test_sync_continues_past_step_failures(stubbed_steps, monkeypatch, capsys):
    """If one step exits with rc=1, the rest still run and pr-sync exits 1."""
    import pr_queue
    call_count = [0]

    def flaky_queue(argv=None):
        call_count[0] += 1
        # First pr-queue call (update --all) fails; second (clean) succeeds.
        return 1 if call_count[0] == 1 else 0

    monkeypatch.setattr(pr_queue, "main", flaky_queue)
    rc = pr_sync.main(["--no-scan", "--queue", "/tmp/q.json5"])
    out = capsys.readouterr().out
    assert "warn" in out
    # rc=1 because there was a non-zero step rc (status=warn, not failed).
    # pr_sync only returns 1 when a step crashes (status=failed).
    assert rc == 0  # warn ≠ failed
    # All 4 non-scan steps still ran.
    assert "pr-task prepare --all" in out


# ---------------------------------------------------------------
# Phase D — base-index audit step
# ---------------------------------------------------------------

import json as _json
from pathlib import Path as _Path


def _write_queue(tmp_path, rows):
    qpath = tmp_path / "queue.json5"
    qpath.write_text(_json.dumps({"filters": None, "prs": rows}), encoding="utf-8")
    return str(qpath)


def test_audit_empty_queue_reports_no_gaps(tmp_path, capsys):
    """No rows → zero groups, zero gaps. Audit runs but emits no warnings."""
    qpath = _write_queue(tmp_path, [])
    log = pr_sync.get_logger("t-audit-empty")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["audited"] is True
    assert res["groups"] == 0
    assert res["gaps"] == []
    assert res["skipped_no_target_branch"] == 0
    assert res["mode"] == "preview"
    # New fields exposed for tooling: promote_threshold + refresh_min_age_hours
    assert res["promote_threshold"] == 2
    assert res["refresh_min_age_hours"] == 1.0


def test_audit_skips_rows_without_target_branch(tmp_path):
    """Rows missing target_branch (e.g., never refreshed) are counted as
    skipped but don't trigger a warning."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending"},  # no target_branch
    ])
    log = pr_sync.get_logger("t-audit-skip")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["groups"] == 0
    assert res["skipped_no_target_branch"] == 1


def test_audit_skips_terminal_rows(tmp_path):
    """Merged / closed rows are out of scope — base index doesn't matter
    for a PR that's already done."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "merged", "target_branch": "main"},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "status": "closed", "target_branch": "main"},
    ])
    log = pr_sync.get_logger("t-audit-terminal")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["groups"] == 0


def test_audit_warns_missing_index(tmp_path, monkeypatch, caplog):
    """When pick_base_index reports no exact match AND queued_prs >= threshold,
    the audit emits a warning naming (repo, target_branch) and the
    `adk repo branch add … --auto` command."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "develop"},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "status": "pending", "target_branch": "develop"},
    ])
    # Stub base_index — exact missing, no fallback.
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)

    log = pr_sync.get_logger("t-audit-missing")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["groups"] == 1
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "missing"
    assert gap["target_branch"] == "develop"
    assert gap["repo"] == "foo"
    assert gap["queued_prs"] == 2
    # --auto is now appended so the demote pass can identify the base later.
    assert gap["command"] == "adk repo branch add foo --branch develop --auto"


def test_audit_below_threshold_is_informational_only(tmp_path, monkeypatch):
    """A target branch with only one queued PR sits below the default
    promote_threshold=2 — gap is recorded as 'below_threshold' but no
    command is emitted. The PR's prepare path falls back to the default
    branch index."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "feature/x"},
    ])
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: SimpleNamespace(branch="master"),
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    log = pr_sync.get_logger("t-audit-below")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "below_threshold"
    assert gap["command"] is None
    assert gap["promote_threshold"] == 2
    assert gap["queued_prs"] == 1
    assert gap["fallback_to"] == "master"


def test_audit_below_threshold_skipped_in_auto_mode(tmp_path, monkeypatch):
    """Auto mode must NOT invoke `branch add` for groups below the threshold —
    even though there's a non-actionable gap, no repo.main call fires."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "feature/x"},
    ])
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    calls: list[list[str]] = []
    fake_repo = SimpleNamespace(main=lambda argv: calls.append(list(argv)) or 0)
    monkeypatch.setitem(__import__("sys").modules, "repo", fake_repo)

    log = pr_sync.get_logger("t-audit-below-auto")
    res = pr_sync._audit_base_indexes(qpath, mode="act", embed_model=None, log=log)
    assert len(res["gaps"]) == 1
    assert res["gaps"][0]["kind"] == "below_threshold"
    assert calls == []  # auto mode skipped the non-actionable gap


def test_audit_warns_stale_index(tmp_path, monkeypatch):
    """A stale exact-match index emits a stale warning + the `adk repo update
    … --branch …` command (not the branch-add command). Even one queued PR
    is enough to trigger a refresh — refreshing an existing index is cheap."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://bitbucket.org/team/foo/pull-requests/5",
         "status": "pending", "target_branch": "develop"},
    ])
    stale_idx = SimpleNamespace(
        branch="develop", slug="develop", age_days=42.0,
        indexed_sha="deadbeef" * 5,
        embed_model="nomic-embed-text",
    )
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: stale_idx,
        is_fresh=lambda idx: False,
        pick_base_index=lambda repo, target_branch, **kw: stale_idx,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    # The drift-check side branch will call _remote_tip; force None so the
    # test doesn't depend on a real bare clone on disk.
    monkeypatch.setattr(pr_sync, "_remote_tip", lambda repo, branch: None)

    log = pr_sync.get_logger("t-audit-stale")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "stale"
    assert gap["age_days"] == 42.0
    assert gap["command"] == "adk repo update foo --branch develop"


def test_audit_detects_drift_against_remote(tmp_path, monkeypatch):
    """An age-fresh exact-match index whose indexed_sha differs from the
    current remote tip is flagged as drifted → `adk repo update`."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://bitbucket.org/team/foo/pull-requests/5",
         "status": "pending", "target_branch": "develop"},
    ])
    fresh_idx = SimpleNamespace(
        branch="develop", slug="develop", age_days=2.0,  # >1h floor, <7d cap
        indexed_sha="aaaa1111" + "0" * 32,
        embed_model="nomic-embed-text",
    )
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: fresh_idx,
        is_fresh=lambda idx: True,  # age says fresh, but drift says otherwise
        pick_base_index=lambda repo, target_branch, **kw: fresh_idx,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    # Remote has moved.
    monkeypatch.setattr(pr_sync, "_remote_tip",
                        lambda repo, branch: "bbbb2222" + "0" * 32)

    log = pr_sync.get_logger("t-audit-drift")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "drifted"
    assert gap["indexed_sha"].startswith("aaaa1111")
    assert gap["remote_tip"].startswith("bbbb2222")
    assert gap["command"] == "adk repo update foo --branch develop"


def test_audit_no_drift_emits_no_gap(tmp_path, monkeypatch):
    """Fresh-by-age AND remote tip matches indexed_sha → no gap."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://bitbucket.org/team/foo/pull-requests/5",
         "status": "pending", "target_branch": "develop"},
    ])
    fresh_idx = SimpleNamespace(
        branch="develop", slug="develop", age_days=2.0,
        indexed_sha="aaaa1111" + "0" * 32,
        embed_model="nomic-embed-text",
    )
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: fresh_idx,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: fresh_idx,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    monkeypatch.setattr(pr_sync, "_remote_tip",
                        lambda repo, branch: "aaaa1111" + "0" * 32)
    log = pr_sync.get_logger("t-audit-no-drift")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["gaps"] == []


def test_audit_skips_drift_check_when_under_min_age(tmp_path, monkeypatch):
    """A base younger than refresh_min_age_hours short-circuits the drift
    check — we don't spam `git ls-remote` on every pr-sync run."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://bitbucket.org/team/foo/pull-requests/5",
         "status": "pending", "target_branch": "develop"},
    ])
    # age_days = 0.01 → ~14 minutes; refresh_min_age_hours default = 1.0
    fresh_idx = SimpleNamespace(
        branch="develop", slug="develop", age_days=0.01,
        indexed_sha="aaaa1111" + "0" * 32,
        embed_model="nomic-embed-text",
    )
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: fresh_idx,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: fresh_idx,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    call_counter = [0]
    def fail_if_called(repo, branch):
        call_counter[0] += 1
        return "bbbb2222" + "0" * 32  # would mark drift if called
    monkeypatch.setattr(pr_sync, "_remote_tip", fail_if_called)
    log = pr_sync.get_logger("t-audit-min-age")
    res = pr_sync._audit_base_indexes(qpath, mode="preview", embed_model=None, log=log)
    assert res["gaps"] == []
    assert call_counter[0] == 0  # drift check was skipped entirely


def test_audit_off_mode_still_returns_summary_silently(tmp_path, monkeypatch):
    """off mode: still counts groups + gaps so callers can act on the summary;
    no warning log lines should fire."""
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "develop"},
    ])
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)
    log = pr_sync.get_logger("t-audit-off")
    res = pr_sync._audit_base_indexes(qpath, mode="off", embed_model=None, log=log)
    assert res["mode"] == "off"
    assert len(res["gaps"]) == 1
    # We do not assert on log content directly — the gap is still in the
    # summary regardless of mode.


def test_audit_auto_mode_invokes_repo_main(tmp_path, monkeypatch):
    """auto mode: for each actionable gap, runs the corresponding `adk repo …`
    command via repo.main and records the rc back on the gap dict.

    Two PRs share the target branch → meets the default promote_threshold=2 →
    audit emits a `missing` gap → auto mode fires `branch add --auto`.
    """
    qpath = _write_queue(tmp_path, [
        {"pr_url": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "develop"},
        {"pr_url": "https://github.com/acme/foo/pull/2",
         "status": "pending", "target_branch": "develop"},
    ])
    fake_base = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake_base)

    calls: list[list[str]] = []
    def fake_repo_main(argv):
        calls.append(list(argv))
        return 0
    fake_repo = SimpleNamespace(main=fake_repo_main)
    monkeypatch.setitem(__import__("sys").modules, "repo", fake_repo)

    log = pr_sync.get_logger("t-audit-auto")
    res = pr_sync._audit_base_indexes(qpath, mode="act", embed_model="bge-m3", log=log)
    assert len(res["gaps"]) == 1
    assert res["gaps"][0]["fix_rc"] == 0
    # Auto run forwards branch + --auto + --auto-reason + embed-model.
    assert calls == [[
        "branch", "add", "foo", "--branch", "develop",
        "--auto", "--auto-reason", "queued_prs=2 (>= promote_threshold=2)",
        "--embed-model", "bge-m3",
    ]]


def test_audit_step_runs_in_pipeline(stubbed_steps, tmp_path, monkeypatch, capsys):
    """End-to-end: pr-sync includes a `base-index audit` entry in the final summary."""
    fake_base = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake_base)
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    out = capsys.readouterr().out
    assert "base-index audit" in out


def test_audit_step_can_be_skipped(stubbed_steps, tmp_path, capsys):
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "--no-base-audit"])
    out = capsys.readouterr().out
    assert "base-index audit" in out
    assert "skipped" in out


def test_auto_demote_step_runs_in_pipeline(stubbed_steps, tmp_path, capsys, monkeypatch):
    """Step 5.6 (auto-base cleanup) is on by default and emits a step record."""
    fake_base = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake_base)
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    out = capsys.readouterr().out
    assert "auto-base cleanup" in out
    assert "ok" in out


def test_auto_demote_can_be_skipped(stubbed_steps, tmp_path, capsys, monkeypatch):
    fake_base = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake_base)
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "--no-auto-demote"])
    out = capsys.readouterr().out
    assert "auto-base cleanup" in out
    assert "skipped" in out


def test_audit_default_mode_is_act(stubbed_steps, tmp_path, monkeypatch, capsys):
    """Model 1: with no flags, the audit defaults to 'act' (run fix commands).
    The visible surface has only direct flags for ask/preview/off."""
    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    def trace(*a, **kw):
        seen_mode.append(kw.get("mode"))
        return real_audit(*a, **kw)
    monkeypatch.setattr(pr_sync, "_audit_base_indexes", trace)

    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    assert seen_mode == ["act"]


def test_audit_interactive_flag_sets_ask_mode(stubbed_steps, tmp_path,
                                              monkeypatch, capsys):
    """`-i` flips the audit into ask mode (prompt before each fix)."""
    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    monkeypatch.setattr(pr_sync, "_audit_base_indexes",
                        lambda *a, **kw: (seen_mode.append(kw.get("mode")) or
                                          real_audit(*a, **kw)))
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "-i"])
    assert seen_mode == ["ask"]


def test_audit_dry_run_sets_preview_mode(stubbed_steps, tmp_path,
                                         monkeypatch, capsys):
    """`--dry-run` flips the audit into preview mode (log intended commands,
    execute none)."""
    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    monkeypatch.setattr(pr_sync, "_audit_base_indexes",
                        lambda *a, **kw: (seen_mode.append(kw.get("mode")) or
                                          real_audit(*a, **kw)))
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "--dry-run"])
    assert seen_mode == ["preview"]


def test_audit_mode_flag_is_not_supported(stubbed_steps, tmp_path):
    qpath = _write_queue(tmp_path, [])
    removed_flag = "--" + "audit-mode"
    with pytest.raises(SystemExit) as exc:
        pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare",
                      removed_flag, "warn"])

    assert exc.value.code == 2


def test_audit_mode_config_override(stubbed_steps, tmp_path,
                                     monkeypatch, capsys):
    """A value under pr_sync.audit_mode in adk-cli.json5 wins over the
    in-code default when no CLI flag forces a mode. Power-users who want
    preview-by-default set audit_mode='preview' in their config."""
    monkeypatch.setattr(pr_sync, "_load_pr_sync_setting",
                        lambda key, default: "preview" if key == "audit_mode" else default)
    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    monkeypatch.setattr(pr_sync, "_audit_base_indexes",
                        lambda *a, **kw: (seen_mode.append(kw.get("mode")) or
                                          real_audit(*a, **kw)))
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    assert seen_mode == ["preview"]


def test_audit_mode_invalid_config_falls_back_to_act(
        stubbed_steps, tmp_path, monkeypatch, capsys):
    """A bogus value in adk-cli.json5 shouldn't crash pr-sync — coerce to 'act'."""
    monkeypatch.setattr(pr_sync, "_load_pr_sync_setting",
                        lambda key, default: "bogus" if key == "audit_mode" else default)
    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    monkeypatch.setattr(pr_sync, "_audit_base_indexes",
                        lambda *a, **kw: (seen_mode.append(kw.get("mode")) or
                                          real_audit(*a, **kw)))
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    assert seen_mode == ["act"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
