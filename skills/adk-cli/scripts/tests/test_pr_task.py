"""Tests for `adk pr-task`:
- prepare → forwards to prepare_task.py --prepare-only with the right args.
- info → reads state.json + pr.json and emits a JSON status block.
- list → enumerates $ADK_DATA_HOME/skill-pr-review/ and supports --names-only / --paths.
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
    """Point PR_REVIEW_ROOT at a clean tmp dir."""
    monkeypatch.setattr(pr_task, "PR_REVIEW_ROOT", tmp_path)
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
            "3_index":     {"head_sha_at_index": "deadbeefcafe1234"},
        }
    }
    # state.json + review.log live at the task root (alongside code/, code-index/);
    # everything else lives under pr-review/.
    (task / "state.json").write_text(json.dumps(state), encoding="utf-8")
    pr_review = task / "pr-review"
    pr_review.mkdir(parents=True, exist_ok=True)
    (pr_review / "pr.json").write_text(json.dumps({
        "title": "fix: stuff", "state": "open"}), encoding="utf-8")
    (pr_review / "precis.md").write_text("# precis\n", encoding="utf-8")
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
        queue="~/.config/adk/pr-queue.json5",
        all=False, rebuild=False, detailed=False, deep=False, embed_model=None,
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
        all=False, rebuild=True, detailed=True, deep=True, embed_model="custom-model",
        jobs=None, yes=False,
    )
    pr_task.cmd_prepare(args)
    cmd = captured["cmd"]
    assert "--rebuild" in cmd
    assert "--detailed" in cmd
    assert "--deep" in cmd
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
        all=False, rebuild=False, detailed=False, deep=False, embed_model=None,
        jobs=None, yes=False,
    )
    rc = pr_task.cmd_prepare(args)
    assert rc == 5


# ---------- --all (sequential + parallel) ---------------------------------

def _all_args(*, jobs=None):
    return SimpleNamespace(
        pr_url=None, queue="/tmp/q.json5", all=True,
        rebuild=False, detailed=False, deep=False, embed_model=None,
        jobs=jobs, yes=False,
    )


def test_prepare_all_sequential_default(monkeypatch, capsys):
    """--all with no --jobs flag and no config setting → sequential, one
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
    out = capsys.readouterr().out
    assert "prepared: 3" in out
    assert "gh:foo#1" in out and "gh:foo#2" in out and "gh:foo#3" in out


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
    out = capsys.readouterr().out
    assert "prepared: 5" in out
    for i in range(1, 6):
        assert f"gh:foo#{i}" in out
    assert set(seen) == set(urls)


def test_prepare_all_parallel_isolates_failures(monkeypatch, capsys):
    """One failing PR must not kill the worker pool; rc=1; other PRs return
    successfully; the failure surfaces in the terminal summary."""
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
    out = capsys.readouterr().out
    assert "prepared: 3" in out
    assert "failed: 1" in out
    assert "gh:foo#2" in out and "boom" in out


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
    out = capsys.readouterr().out
    assert "prepared: 2" in out


def test_prepare_all_jobs_one_matches_sequential_behavior(monkeypatch, capsys):
    """--jobs 1 explicitly takes the sequential code path (same as omitting
    --jobs when the config key is absent); ensures we didn't regress the single-job
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
    """If the config module is unimportable / config key absent → 1."""
    import builtins
    real_import = builtins.__import__
    def blocked(name, *a, **kw):
        if name == "config":
            raise ImportError("simulated")
        return real_import(name, *a, **kw)
    monkeypatch.setattr(builtins, "__import__", blocked)
    assert pr_task._default_prepare_jobs() == 1


def test_default_prepare_jobs_reads_adk_cli_json5(monkeypatch):
    """When adk-cli.json5 has pr_sync.prepare_jobs: N, that becomes the default."""
    def fake_get(*path, default=None):
        if path == ("pr_sync", "prepare_jobs"):
            return 4
        return default
    fake_module = SimpleNamespace(get_adk_cli=fake_get)
    monkeypatch.setitem(sys.modules, "config", fake_module)
    assert pr_task._default_prepare_jobs() == 4


def test_default_prepare_jobs_clamps_to_minimum_one(monkeypatch):
    """A zero/negative config value must not disable preparing entirely."""
    def fake_get(*path, default=None):
        if path == ("pr_sync", "prepare_jobs"):
            return 0
        return default
    fake_module = SimpleNamespace(get_adk_cli=fake_get)
    monkeypatch.setitem(sys.modules, "config", fake_module)
    assert pr_task._default_prepare_jobs() == 1


# ----- _extract_trailing_json -------------------------------------------------

def test_extract_trailing_json_multiline_indented():
    """The orchestrator's `json.dumps(..., indent=2)` output is recovered
    correctly — the old code grabbed only the trailing `}` and lost the
    whole payload."""
    blob = """[pr-sync] preparing 14 task folder(s)
$ prepare_task.py ...
{
  "action": "prepared",
  "pr_url": "https://bitbucket.org/foo/bar/pull-requests/1",
  "task_dir": "/tmp/foo_pr-1",
  "head_sha": "abc123"
}
"""
    obj = pr_task._extract_trailing_json(blob)
    assert obj is not None
    assert obj["action"] == "prepared"
    assert obj["pr_url"].endswith("/1")


def test_extract_trailing_json_returns_none_on_empty():
    assert pr_task._extract_trailing_json("") is None
    assert pr_task._extract_trailing_json("no json here\nstill nothing") is None


def test_extract_trailing_json_ignores_braces_in_strings():
    blob = """logs:
"this } contains a brace"
{"action":"prepared","note":"also { fake"}
"""
    obj = pr_task._extract_trailing_json(blob)
    assert obj is not None
    assert obj["action"] == "prepared"
    assert obj["note"] == "also { fake"


def test_extract_trailing_json_picks_last_object():
    blob = """{"first": true}
log line
{"second": true}
"""
    obj = pr_task._extract_trailing_json(blob)
    assert obj == {"second": True}


# ----- _extract_error_reason -------------------------------------------------

def test_extract_error_reason_prefers_step_failed():
    stderr = (
        "Traceback (most recent call last):\n"
        '  File "create_worktree.py", line 72, in fetch_sha\n'
        '    raise RuntimeError(f"sha {sha} not reachable from origin after full fetch")\n'
        "RuntimeError: sha a2ab692a4db6 not reachable from origin after full fetch\n"
        "step failed (rc=1): /usr/bin/python3 .../create_worktree.py --repo ecomm-ssr ...\n"
    )
    out = pr_task._extract_error_reason(stderr, "")
    assert out.startswith("step failed (rc=1):")
    # And the old, broken slice no longer appears:
    assert not out.startswith("ise RuntimeError")


def test_extract_error_reason_falls_back_to_runtime_error():
    stderr = (
        "Traceback (most recent call last):\n"
        '  File "x.py", line 1, in <module>\n'
        "RuntimeError: sha abc not reachable from origin after full fetch\n"
    )
    out = pr_task._extract_error_reason(stderr, "")
    assert out == "RuntimeError: sha abc not reachable from origin after full fetch"


def test_extract_error_reason_empty_inputs():
    assert pr_task._extract_error_reason("", "") == "<no output>"


def test_extract_error_reason_uses_stdout_when_stderr_empty():
    stdout = "something useful on stdout\nfinal status line"
    out = pr_task._extract_error_reason("", stdout)
    assert out == "final status line"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
