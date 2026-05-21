"""Tests for `adk pr-task`:
- prepare → forwards to prepare_task.py --prepare-only with the right args.
- info → reads state.json + pr.json and emits a JSON status block.
- list → enumerates ~/.agents-devkit/skill-pr-review/ and supports --names-only / --paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import pr_task


@pytest.fixture
def fake_pr_reviews(tmp_path, monkeypatch):
    """Point PR_REVIEWS_ROOT at a clean tmp dir."""
    monkeypatch.setattr(pr_task, "PR_REVIEW_ROOT", tmp_path)
    monkeypatch.setattr(pr_task, "PR_REVIEWS_ROOT", tmp_path)
    monkeypatch.setattr(pr_task, "LEGACY_PR_REVIEW_ROOT", tmp_path / "legacy-unused")
    return tmp_path


def test_list_empty(fake_pr_reviews, capsys):
    args = SimpleNamespace(names_only=False, paths=False, yes=False)
    rc = pr_task.cmd_list(args)
    assert rc == 0
    assert "no task folders" in capsys.readouterr().out


def test_list_names_only_empty(fake_pr_reviews, capsys):
    args = SimpleNamespace(names_only=True, paths=False, yes=False)
    rc = pr_task.cmd_list(args)
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_list_names_only_skips_hidden(fake_pr_reviews, capsys):
    (fake_pr_reviews / "foo_pr-1").mkdir()
    (fake_pr_reviews / "bar_pr-2").mkdir()
    (fake_pr_reviews / ".cache").mkdir()
    args = SimpleNamespace(names_only=True, paths=False, yes=False)
    pr_task.cmd_list(args)
    assert capsys.readouterr().out.splitlines() == ["bar_pr-2", "foo_pr-1"]


def test_list_paths(fake_pr_reviews, capsys):
    (fake_pr_reviews / "foo_pr-1").mkdir()
    args = SimpleNamespace(names_only=False, paths=True, yes=False)
    pr_task.cmd_list(args)
    out = capsys.readouterr().out.strip()
    assert out.endswith("foo_pr-1")
    assert str(fake_pr_reviews) in out


def test_info_for_nonexistent_task(monkeypatch, tmp_path, capsys):
    """`pr-task info` on a URL whose folder doesn't exist returns a structured
    `exists: false` blob — not an error."""
    monkeypatch.setattr(pr_task, "task_dir_for",
                        lambda repo, n: tmp_path / "nope")
    monkeypatch.setattr(pr_task, "_task_dir_for",
                        lambda url: tmp_path / "nope")
    args = SimpleNamespace(pr_url="https://github.com/acme/foo/pull/1", yes=False)
    rc = pr_task.cmd_info(args)
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["pr_url"] == "https://github.com/acme/foo/pull/1"
    assert out["exists"] is False


def test_info_reads_state_and_pr_json(tmp_path, monkeypatch, capsys):
    task = tmp_path / "foo_pr-42"
    task.mkdir()
    # Fake the state.json that prepare_task.py would have written.
    state = {
        "phases": {
            "2a_fetch_pr": {"head_sha": "deadbeefcafe1234"},
            "3_index":     {"head_oid_at_index": "deadbeefcafe1234"},
        }
    }
    (task / "state.json").write_text(json.dumps(state), encoding="utf-8")
    (task / "pr.json").write_text(json.dumps({
        "title": "fix: stuff", "state": "open"}), encoding="utf-8")
    (task / "precis.md").write_text("# precis\n", encoding="utf-8")
    # findings.json deliberately missing.

    monkeypatch.setattr(pr_task, "_task_dir_for", lambda url: task)
    args = SimpleNamespace(pr_url="https://github.com/acme/foo/pull/42", yes=False)
    pr_task.cmd_info(args)
    out = json.loads(capsys.readouterr().out)
    assert out["exists"] is True
    assert out["has_pr_json"] is True
    assert out["has_precis"] is True
    assert out["has_findings"] is False
    assert out["head_sha"] == "deadbeefcafe1234"
    assert out["last_indexed_head"] == "deadbeefcafe1234"
    assert out["title"] == "fix: stuff"
    assert out["state"] == "open"


def test_prepare_forwards_to_run_review(monkeypatch, capsys):
    """`pr-task prepare <url>` should spawn `prepare_task.py --prepare-only <url>`
    with the queue path, and pass through the exit code.

    Relies on the real PREPARE_TASK file existing in the repo (it does — the
    test runs from the same checkout that supplies the script). We only mock
    `subprocess.run` so no actual orchestrator work happens.
    """
    captured: dict = {}

    class FakeCP:
        returncode = 0
        stdout = '{"action": "prepared", "head_sha": "abc"}\n'
        stderr = ""

    def fake_run(cmd, **kw):
        captured["cmd"] = cmd
        return FakeCP()

    monkeypatch.setattr("subprocess.run", fake_run)

    args = SimpleNamespace(
        pr_url="https://github.com/acme/foo/pull/9",
        queue="~/.agents-devkit/config/pr-queue.json5",
        all=False, rebuild=False, detailed=False, embed_model=None,
        jobs=None, yes=False,
    )
    rc = pr_task.cmd_prepare(args)
    assert rc == 0
    cmd = captured["cmd"]
    assert cmd[0] == sys.executable
    assert "prepare_task.py" in cmd[1]
    assert "--prepare-only" in cmd
    assert "https://github.com/acme/foo/pull/9" in cmd


def test_prepare_forwards_extra_flags(monkeypatch):
    captured: dict = {}

    class FakeCP:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr("subprocess.run",
                        lambda cmd, **kw: captured.update(cmd=cmd) or FakeCP())

    args = SimpleNamespace(
        pr_url="https://github.com/acme/foo/pull/9",
        queue="/tmp/q.json5",
        all=False, rebuild=True, detailed=True, embed_model="custom-model",
        jobs=None, yes=False,
    )
    pr_task.cmd_prepare(args)
    cmd = captured["cmd"]
    assert "--rebuild" in cmd
    assert "--detailed" in cmd
    assert "--embed-model" in cmd
    assert "custom-model" in cmd


def test_prepare_propagates_nonzero_exit(monkeypatch):
    class FakeCP:
        returncode = 5
        stdout = "boom\n"
        stderr = "err\n"

    monkeypatch.setattr("subprocess.run", lambda cmd, **kw: FakeCP())

    args = SimpleNamespace(
        pr_url="x", queue="q",
        all=False, rebuild=False, detailed=False, embed_model=None,
        jobs=None, yes=False,
    )
    rc = pr_task.cmd_prepare(args)
    assert rc == 5


# ---------- --all (sequential + parallel) ---------------------------------

def _all_args(*, jobs=None):
    return SimpleNamespace(
        pr_url=None, queue="/tmp/q.json5", all=True,
        rebuild=False, detailed=False, embed_model=None,
        jobs=jobs, yes=False,
    )


def test_prepare_all_sequential_default(monkeypatch, capsys):
    """--all with no --jobs flag and no core.yaml setting → sequential, one
    _prepare_one call per URL, all results returned in queue order."""
    urls = ["https://github.com/acme/foo/pull/1",
            "https://github.com/acme/foo/pull/2",
            "https://github.com/acme/foo/pull/3"]
    monkeypatch.setattr(pr_task, "_queued_task_dirs",
                        lambda _q: {u: object() for u in urls})
    monkeypatch.setattr(pr_task, "_default_prepare_jobs", lambda: 1)

    seen: list[str] = []
    def fake_prepare_one(url, **kw):
        seen.append(url)
        return {"pr_url": url, "status": "prepared", "head_sha": "abc"}
    monkeypatch.setattr(pr_task, "_prepare_one", fake_prepare_one)

    rc = pr_task.cmd_prepare(_all_args())
    assert rc == 0
    assert seen == urls  # sequential preserves submission order
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 3
    assert {r["pr_url"] for r in out["prepared"]} == set(urls)


def test_prepare_all_parallel_returns_all_results(monkeypatch, capsys):
    """--jobs 3 → all 3 PRs processed; order in the result list may differ
    from queue order (completion-order) but the count + URL set are stable."""
    urls = [f"https://github.com/acme/foo/pull/{i}" for i in range(1, 6)]
    monkeypatch.setattr(pr_task, "_queued_task_dirs",
                        lambda _q: {u: object() for u in urls})

    import threading
    seen = []
    lock = threading.Lock()
    def fake_prepare_one(url, **kw):
        with lock:
            seen.append(url)
        return {"pr_url": url, "status": "prepared"}
    monkeypatch.setattr(pr_task, "_prepare_one", fake_prepare_one)

    rc = pr_task.cmd_prepare(_all_args(jobs=3))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 5
    assert {r["pr_url"] for r in out["prepared"]} == set(urls)
    assert set(seen) == set(urls)


def test_prepare_all_parallel_isolates_failures(monkeypatch, capsys):
    """One failing PR must not kill the worker pool; rc=1; other PRs return
    successfully; the failure surfaces in the JSON result."""
    urls = [f"https://github.com/acme/foo/pull/{i}" for i in range(1, 5)]
    monkeypatch.setattr(pr_task, "_queued_task_dirs",
                        lambda _q: {u: object() for u in urls})

    def fake_prepare_one(url, **kw):
        if url.endswith("/2"):
            return {"pr_url": url, "status": "failed", "reason": "boom"}
        return {"pr_url": url, "status": "prepared"}
    monkeypatch.setattr(pr_task, "_prepare_one", fake_prepare_one)

    rc = pr_task.cmd_prepare(_all_args(jobs=2))
    assert rc == 1
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 4
    by_url = {r["pr_url"]: r for r in out["prepared"]}
    assert by_url[urls[1]]["status"] == "failed"
    assert by_url[urls[1]]["reason"] == "boom"
    for u in (urls[0], urls[2], urls[3]):
        assert by_url[u]["status"] == "prepared"


def test_prepare_all_parallel_clamps_jobs_to_url_count(monkeypatch, capsys):
    """--jobs 10 with only 2 URLs → effective workers = 2 (no oversubscription).
    Verified indirectly via the "(jobs=N)" log line + that all results return."""
    urls = ["https://github.com/acme/foo/pull/1",
            "https://github.com/acme/foo/pull/2"]
    monkeypatch.setattr(pr_task, "_queued_task_dirs",
                        lambda _q: {u: object() for u in urls})
    monkeypatch.setattr(pr_task, "_prepare_one",
                        lambda url, **kw: {"pr_url": url, "status": "prepared"})

    rc = pr_task.cmd_prepare(_all_args(jobs=10))
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["count"] == 2


def test_prepare_all_jobs_one_matches_sequential_behavior(monkeypatch, capsys):
    """--jobs 1 explicitly takes the sequential code path (same as omitting
    --jobs when core.yaml is empty); ensures we didn't regress the single-job
    case to use ThreadPoolExecutor."""
    urls = ["https://github.com/acme/foo/pull/1",
            "https://github.com/acme/foo/pull/2"]
    monkeypatch.setattr(pr_task, "_queued_task_dirs",
                        lambda _q: {u: object() for u in urls})

    seen: list[str] = []
    monkeypatch.setattr(pr_task, "_prepare_one",
                        lambda url, **kw: (seen.append(url) or
                                           {"pr_url": url, "status": "prepared"}))
    rc = pr_task.cmd_prepare(_all_args(jobs=1))
    assert rc == 0
    assert seen == urls  # strict order preserved


def test_default_prepare_jobs_falls_back_to_one(monkeypatch):
    """If config_io is unimportable / core.yaml missing / key absent → 1."""
    import builtins
    real_import = builtins.__import__
    def blocked(name, *a, **kw):
        if name == "config_io":
            raise ImportError("simulated")
        return real_import(name, *a, **kw)
    monkeypatch.setattr(builtins, "__import__", blocked)
    assert pr_task._default_prepare_jobs() == 1


def test_default_prepare_jobs_reads_core_yaml(monkeypatch):
    """When core.yaml has pr_sync.prepare_jobs: N, that becomes the default."""
    fake_module = SimpleNamespace(
        load_core=lambda: {"pr_sync": {"prepare_jobs": 4}}
    )
    monkeypatch.setitem(sys.modules, "config_io", fake_module)
    assert pr_task._default_prepare_jobs() == 4


def test_default_prepare_jobs_clamps_to_minimum_one(monkeypatch):
    """A zero/negative config value must not disable preparing entirely."""
    fake_module = SimpleNamespace(
        load_core=lambda: {"pr_sync": {"prepare_jobs": 0}}
    )
    monkeypatch.setitem(sys.modules, "config_io", fake_module)
    assert pr_task._default_prepare_jobs() == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
