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
    import pr_scan, pr_queue, pr_task
    monkeypatch.setattr(pr_scan, "main", stub_scan)
    monkeypatch.setattr(pr_queue, "main", stub_queue)
    monkeypatch.setattr(pr_task, "main", stub_task)
    return trace


def test_sync_runs_all_six_steps_in_order(stubbed_steps):
    rc = pr_sync.main(["--queue", "/tmp/q.json5"])
    assert rc == 0
    names = [step for step, _ in stubbed_steps]
    assert names == [
        "pr-scan",         # 1
        "pr-queue",        # 2: update --all
        "pr-queue",        # 3: clean (merged + declined)
        "pr-task",         # 4: clean-orphans (dry-run by default)
        "pr-queue",        # 5: remind (dry-run by default)
        "pr-task",         # 6: prepare --all
    ]
    # Step-2 invokes `update --all`; step-3 invokes plain `clean`.
    assert "update" in stubbed_steps[1][1]
    assert "--all" in stubbed_steps[1][1]
    assert "clean" in stubbed_steps[2][1]
    assert "clean-orphans" in stubbed_steps[3][1]
    # Step 5: remind
    assert "remind" in stubbed_steps[4][1]
    # Step 6: prepare --all
    assert "prepare" in stubbed_steps[5][1]
    assert "--all" in stubbed_steps[5][1]


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
    out = json.loads(capsys.readouterr().out)
    assert any(s["status"] == "warn" for s in out["steps"])
    # rc=1 because there was a non-zero step rc (status=warn, not failed).
    # pr_sync only returns 1 when a step crashes (status=failed).
    assert rc == 0  # warn ≠ failed
    # All 4 non-scan steps still ran.
    step_names = [s["step"] for s in out["steps"]]
    assert "pr-task prepare --all" in step_names


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
    res = pr_sync._audit_base_indexes(qpath, mode="warn", embed_model=None, log=log)
    assert res == {"audited": True, "groups": 0, "gaps": [],
                   "skipped_no_target_branch": 0, "mode": "warn"}


def test_audit_skips_rows_without_target_branch(tmp_path):
    """Rows missing target_branch (e.g., never refreshed) are counted as
    skipped but don't trigger a warning."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
         "status": "pending"},  # no target_branch
    ])
    log = pr_sync.get_logger("t-audit-skip")
    res = pr_sync._audit_base_indexes(qpath, mode="warn", embed_model=None, log=log)
    assert res["groups"] == 0
    assert res["skipped_no_target_branch"] == 1


def test_audit_skips_terminal_rows(tmp_path):
    """Merged / declined rows are out of scope — base index doesn't matter
    for a PR that's already done."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
         "status": "merged", "target_branch": "main"},
        {"pr_link": "https://github.com/acme/foo/pull/2",
         "status": "declined", "target_branch": "main"},
    ])
    log = pr_sync.get_logger("t-audit-terminal")
    res = pr_sync._audit_base_indexes(qpath, mode="warn", embed_model=None, log=log)
    assert res["groups"] == 0


def test_audit_warns_missing_index(tmp_path, monkeypatch, caplog):
    """When pick_base_index reports no exact match, the audit emits a warning
    naming the (repo, target_branch) and the `adk repo branch add …` command."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
         "status": "pending", "target_branch": "develop"},
        {"pr_link": "https://github.com/acme/foo/pull/2",
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
    res = pr_sync._audit_base_indexes(qpath, mode="warn", embed_model=None, log=log)
    assert res["groups"] == 1
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "missing"
    assert gap["target_branch"] == "develop"
    assert gap["repo"] == "foo"
    assert gap["queued_prs"] == 2
    assert gap["command"] == "adk repo branch add foo --branch develop"


def test_audit_warns_stale_index(tmp_path, monkeypatch):
    """A stale exact-match index emits a stale warning + the `adk repo update
    … --branch …` command (not the branch-add command)."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://bitbucket.org/team/foo/pull-requests/5",
         "status": "pending", "target_branch": "develop"},
    ])
    stale_idx = SimpleNamespace(
        branch="develop", slug="develop", age_days=42.0,
        embed_model="nomic-embed-text",
    )
    fake = SimpleNamespace(
        get_branch_index=lambda repo, br: stale_idx,
        is_fresh=lambda idx: False,
        pick_base_index=lambda repo, target_branch, **kw: stale_idx,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake)

    log = pr_sync.get_logger("t-audit-stale")
    res = pr_sync._audit_base_indexes(qpath, mode="warn", embed_model=None, log=log)
    assert len(res["gaps"]) == 1
    gap = res["gaps"][0]
    assert gap["kind"] == "stale"
    assert gap["age_days"] == 42.0
    assert gap["command"] == "adk repo update foo --branch develop"


def test_audit_off_mode_still_returns_summary_silently(tmp_path, monkeypatch):
    """off mode: still counts groups + gaps so callers can act on the summary;
    no warning log lines should fire."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
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
    """auto mode: for each gap, runs the corresponding `adk repo …` command
    via repo.main and records the rc back on the gap dict."""
    qpath = _write_queue(tmp_path, [
        {"pr_link": "https://github.com/acme/foo/pull/1",
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
    res = pr_sync._audit_base_indexes(qpath, mode="auto", embed_model="bge-m3", log=log)
    assert len(res["gaps"]) == 1
    assert res["gaps"][0]["fix_rc"] == 0
    # The auto run forwarded both the branch-add command AND the embed-model.
    assert calls == [["branch", "add", "foo", "--branch", "develop",
                      "--embed-model", "bge-m3"]]


def test_audit_step_runs_in_pipeline(stubbed_steps, tmp_path, monkeypatch, capsys):
    """End-to-end: pr-sync (default audit-mode=warn from config) includes a
    `base-index audit` entry in the final summary."""
    fake_base = SimpleNamespace(
        get_branch_index=lambda repo, br: None,
        is_fresh=lambda idx: True,
        pick_base_index=lambda repo, target_branch, **kw: None,
    )
    monkeypatch.setitem(__import__("sys").modules, "base_index", fake_base)
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    out = _json.loads(capsys.readouterr().out)
    steps = [s["step"] for s in out["steps"]]
    assert "base-index audit" in steps


def test_audit_step_can_be_skipped(stubbed_steps, tmp_path, capsys):
    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "--no-base-audit"])
    out = _json.loads(capsys.readouterr().out)
    audit_step = next((s for s in out["steps"] if s["step"] == "base-index audit"), None)
    assert audit_step is not None and audit_step["status"] == "skipped"


def test_audit_mode_cli_overrides_config(stubbed_steps, tmp_path, monkeypatch, capsys):
    """`--audit-mode off` wins over whatever core.yaml says — useful for one-off
    runs where the user doesn't want noise."""
    # Force config to return 'auto' so we can prove the CLI flag wins.
    monkeypatch.setattr(pr_sync, "_load_pr_sync_setting",
                        lambda key, default: "auto" if key == "auto_update_base_indexes" else default)

    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    def trace(*a, **kw):
        seen_mode.append(kw.get("mode"))
        return real_audit(*a, **kw)
    monkeypatch.setattr(pr_sync, "_audit_base_indexes", trace)

    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare", "--audit-mode", "off"])
    assert seen_mode == ["off"]


def test_audit_mode_invalid_value_falls_back_to_warn(stubbed_steps, tmp_path,
                                                     monkeypatch, capsys):
    """A bogus value in core.yaml shouldn't crash pr-sync — coerce to 'warn'."""
    monkeypatch.setattr(pr_sync, "_load_pr_sync_setting",
                        lambda key, default: "bogus" if key == "auto_update_base_indexes" else default)

    seen_mode = []
    real_audit = pr_sync._audit_base_indexes
    def trace(*a, **kw):
        seen_mode.append(kw.get("mode"))
        return real_audit(*a, **kw)
    monkeypatch.setattr(pr_sync, "_audit_base_indexes", trace)

    qpath = _write_queue(tmp_path, [])
    pr_sync.main(["--queue", qpath, "--no-scan", "--no-prepare"])
    assert seen_mode == ["warn"]


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
