# TUI sub-phase δ — binding interface SPEC

Status: **frozen**, parallel build. Companion to `SPEC.md` (α+β) and `SPEC-gamma.md` (γ).

γ shipped `s` → `adk pr-sync` subprocess with LogPane + SyncPlanPane. δ adds:
1. `r` key triggers a **worker** that drives one PR through claim → prepare → spawn `claude -p /adk-pr-review` → release.
2. A new `tui/worker.py` script — standalone, callable directly via `python3 tui/worker.py <pr_url>`. The TUI spawns it as a subprocess (mirroring γ's `adk pr-sync` model).
3. The worker writes a **heartbeat file** at `~/.agents-devkit/tui/workers/<pid>.json` every 5 s for future θ visibility, AND calls `adk pr-queue heartbeat <url>` every 5 min so a long review's lock doesn't expire (the TAKEN_LOCK_MAX_AGE_SECONDS default is 2 h).
4. Pressing `r` while a sync OR another review is running is a no-op (`_busy()` mutex; one long-running child at a time in this slice). Pressing `s` while a review is running is likewise blocked.
5. The agent binary (`claude`) and the `adk` binary are both injectable via flags for tests — no real `claude -p` calls in CI.

All α+β+γ behavior must keep working. The existing 457 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/worker.py` (NEW), `tui/__init__.py` (MAYBE — to re-export if needed) | `_common.py`, `queue_io.py`, `pr_queue.py`, `pr_task.py`, `tui_plan.py` |
| **B** | `adk-agent-implementer` | `tui/app.py` (MODIFIED), `tui/widgets/footer_bar.py` (MODIFIED), `tui/widgets/help_screen.py` (MODIFIED) | all α+β+γ files |
| **C** | `adk-agent-test-engineer` | `tui/tests/test_worker.py` (NEW), `tui/tests/test_review_action.py` (NEW), `tui/tests/conftest.py` (MODIFIED — add `fake_claude_script`, `worker_heartbeat_dir` fixtures), `tui/tests/fixtures/eligible_queue.json5` (NEW — a queue with one ready row for the review action to target) | everything |

**Hard rule**: A does not touch any TUI widget or test file. B does not touch worker.py or tests. C does not write production code.

---

## 2. The worker contract

### 2.1 CLI signature

```
python3 tui/worker.py <pr_url>
   [--queue PATH]
   [--agent-bin PATH]
   [--adk-bin PATH]
   [--no-prepare]
   [--heartbeat-bump-interval-s N]   # default 300 (5 min)
   [--heartbeat-file-interval-s N]   # default 5
   [--heartbeat-dir PATH]            # default ~/.agents-devkit/tui/workers/
```

**Argument semantics**:
- `pr_url` (positional): the PR to review. Validated by extracting (host, repo, number) via `parse_pr_url` from `_common.py`. Invalid URL → exit 2 with `(error: ...)` line on stdout.
- `--queue`: queue file to operate on. Default: `queue_io.DEFAULT_QUEUE_PATH`.
- `--agent-bin`: path to the agent binary. Default: `"claude"` (PATH lookup).
- `--adk-bin`: path to the `adk` binary. Default: resolve via `repo_root / "bin" / "adk"` if it exists, else `"adk"` (PATH lookup). (Same logic as `tui/app.py`'s `_resolve_adk_bin`; the worker MAY import that resolver or duplicate it.)
- `--no-prepare`: skip the `adk pr-task prepare <url>` step. Useful if a sync already prepared the task folder.
- `--heartbeat-bump-interval-s`: how often (seconds) the worker calls `adk pr-queue heartbeat <url>`. Default 300; tests use 0.5 to exercise the loop quickly.
- `--heartbeat-file-interval-s`: how often (seconds) the worker rewrites the heartbeat file. Default 5; tests use 0.1.
- `--heartbeat-dir`: where the heartbeat file is written. Default `~/.agents-devkit/tui/workers/`; tests redirect to `tmp_path`.

### 2.2 Flow

```
1.  Validate pr_url. On invalid → print "(error: invalid pr_url: <reason>)" → exit 2.

2.  Call: <adk-bin> pr-queue claim <pr_url> --queue <queue>
    On non-zero exit:
      Print "(error: claim failed — row may be locked by another reviewer)"
      Exit 2.
    On success:
      Print "(claimed: <pr_url>)"

3.  Unless --no-prepare:
    Call: <adk-bin> pr-task prepare <pr_url> --queue <queue>
    Stream its stdout/stderr to OUR stdout (so the TUI tails it).
    On non-zero exit:
      Print "(error: prepare failed rc=<rc>)"
      Goto step 7 (release with --status error).

4.  Write the heartbeat file (see §2.3 schema). Schedule async tasks:
       - heartbeat_bump_task: every <heartbeat-bump-interval-s>, call
         <adk-bin> pr-queue heartbeat <pr_url> --queue <queue>.
       - heartbeat_file_task: every <heartbeat-file-interval-s>, rewrite the
         heartbeat file with last_heartbeat=now.

5.  Spawn: <agent-bin> -p "/adk-pr-review <pr_url>"
    stdout=PIPE, stderr=STDOUT, env=os.environ
    Print "$ <cmd>" line first.
    Stream subprocess.stdout line-by-line to OUR stdout (line-buffered).

6.  On agent exit:
    Print "(review exited rc=<rc>)"
    Cancel heartbeat tasks. Remove heartbeat file.

7.  Release the lock as a safety net:
    Call: <adk-bin> pr-queue release <pr_url> --queue <queue>
       (If the agent already called `adk pr-task report` which released the
       lock, this is a no-op — release is idempotent.)
    The release call's --status arg is set only if the agent exited non-zero:
       --status error (rc != 0) / no --status (rc == 0, leave status alone
       because the agent's report.py already set the right terminal status).

8.  Exit with the agent's rc (or with 1 if a step before the agent failed).
    SIGTERM during any step:
      - Kill the agent subprocess if alive (terminate, 2 s grace, kill).
      - Cancel heartbeat tasks.
      - Remove heartbeat file.
      - Release the lock (with --status error if mid-review).
      - Exit 130.
```

### 2.3 Heartbeat file schema (`~/.agents-devkit/tui/workers/<pid>.json`)

```json5
{
  "pid": 12345,
  "pr_url": "https://github.com/acme/foo/pull/42",
  "task_type": "review",
  "agent": "claude",
  "queue": "/Users/sujeet/.agents-devkit/config/pr-queue.json5",
  "started_at": "2026-05-22T14:32:15Z",
  "last_heartbeat": "2026-05-22T14:32:20Z",
  "current_phase": "review",          // "claim" | "prepare" | "review" | "release" | "done" | "error"
  "rc": null                          // final rc on exit (only present in "done" / "error")
}
```

The file is written atomically (`tmp + os.replace`) and removed when the worker exits (cleanly or via SIGTERM). Crashes leave a stale file; the TUI's θ phase will GC stale files (older than 2 × heartbeat_file_interval). For δ, just write+delete.

### 2.4 Exit codes

| Code | Meaning |
|---|---|
| 0 | Review completed cleanly (agent exited 0). |
| 1 | Step or agent failed; lock released (with status=error if mid-review). |
| 2 | Claim failed (locked by another reviewer) OR invalid pr_url. |
| 130 | SIGTERM received; lock released with status=error. |

### 2.5 stdout contract (what the TUI sees)

One human-readable line at a time. Lines starting with `$ ` are commands; lines in `(...)` are meta. Anything else is straight through from the agent or prepare step.

```
(claimed: https://github.com/acme/foo/pull/42)
$ /Users/.../bin/adk pr-task prepare https://github.com/acme/foo/pull/42 --queue ...
prepare: ok (used base: acme/foo:main, 0s)
$ /opt/homebrew/bin/claude -p /adk-pr-review https://github.com/acme/foo/pull/42
[claude] Phase 2: query for relevant code...
[claude] Phase 5: posting 4 comments
(review exited rc=0)
(released: https://github.com/acme/foo/pull/42)
```

### 2.6 Implementation constraints

- Pure stdlib + the existing `_common.parse_pr_url`. No new deps.
- Async-throughout (`asyncio.create_subprocess_exec`, `asyncio.gather`). The heartbeat tasks are `asyncio.create_task`'d and cancelled at exit.
- `signal.SIGTERM` handler installed via `loop.add_signal_handler(SIGTERM, ...)`. macOS-friendly (POSIX). Windows not supported (matches constitution §VI.2).
- ≤ 250 LOC including blank lines.

---

## 3. Agent B — TUI integration

### 3.1 `tui/app.py` changes

**Imports**:
```python
# in BINDINGS list, after "s"
Binding("r", "review", "review"),
```

**`__init__` new slots**:
```python
self._review_proc: asyncio.subprocess.Process | None = None
self._review_task: asyncio.Task | None = None
self._agent_bin: Path | None = None    # NEW kwarg
self._heartbeat_dir: Path | None = None  # NEW kwarg
```

**`__init__` signature additions** (keep backward compat):
```python
def __init__(
    self,
    *,
    queue_path: Path | None = None,
    ascii_only: bool = False,
    poll_interval: float = 2.0,
    plan_path: Path | None = None,
    adk_bin: Path | None = None,
    agent_bin: Path | None = None,        # NEW
    heartbeat_dir: Path | None = None,    # NEW
    worker_script: Path | None = None,    # NEW — for tests; defaults to repo's tui/worker.py
) -> None:
```

**`_busy()` helper**:
```python
def _busy(self) -> str | None:
    """Return a short label of any running subprocess, else None."""
    if self._sync_proc is not None and self._sync_proc.returncode is None:
        return "sync"
    if self._review_proc is not None and self._review_proc.returncode is None:
        return "review"
    return None
```

**`action_sync` update** — replace the `_sync_proc` check with `_busy()`:
```python
def action_sync(self) -> None:
    busy = self._busy()
    if busy is not None:
        self.query_one(LogPane).write(f"(can't start sync — {busy} already running)")
        return
    self._sync_task = asyncio.create_task(self._run_sync())
    self._sync_task.add_done_callback(self._on_sync_task_done)
```

**`action_review`**:
```python
def action_review(self) -> None:
    busy = self._busy()
    if busy is not None:
        self.query_one(LogPane).write(f"(can't start review — {busy} already running)")
        return
    table = self.query_one(QueueTable)
    pr_url = table.selected_pr_url()
    if not pr_url:
        self.query_one(LogPane).write("(no row selected)")
        return
    row = self._rows_by_url.get(pr_url)
    if row is None:
        self.query_one(LogPane).write("(row not found in current snapshot)")
        return
    if not row.ready_for_review:
        self.query_one(LogPane).write(
            f"(row not ready: prep_status={row.prep_status!r}, status={row.status!r})"
        )
        return
    self._review_task = asyncio.create_task(self._run_review(pr_url))
    self._review_task.add_done_callback(self._on_review_task_done)
```

**`_on_review_task_done`**: mirror `_on_sync_task_done`.

**`_run_review(pr_url)`**:
```python
async def _run_review(self, pr_url: str) -> None:
    log_pane = self.query_one(LogPane)
    worker = self._resolve_worker_script()
    cmd: list[str] = [sys.executable, str(worker), pr_url]
    if self._queue_path is not None:
        cmd += ["--queue", str(self._queue_path)]
    if self._adk_bin is not None:
        cmd += ["--adk-bin", str(self._adk_bin)]
    if self._agent_bin is not None:
        cmd += ["--agent-bin", str(self._agent_bin)]
    if self._heartbeat_dir is not None:
        cmd += ["--heartbeat-dir", str(self._heartbeat_dir)]
    log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=False, review_running=True,
    )
    try:
        self._review_proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except (FileNotFoundError, PermissionError, OSError) as exc:
        log_pane.write(f"(error: {exc})")
        self._review_proc = None
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=False, review_running=False,
        )
        return
    assert self._review_proc.stdout is not None
    while True:
        line = await self._review_proc.stdout.readline()
        if not line:
            break
        log_pane.write(line.decode(errors="replace").rstrip("\n"))
    rc = await self._review_proc.wait()
    log_pane.write(f"(worker exited rc={rc})")
    self._review_proc = None
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=False, review_running=False,
    )
    self._reload(force=True)
```

**`_resolve_worker_script`**:
```python
def _resolve_worker_script(self) -> Path:
    if self._worker_script is not None:
        return self._worker_script
    return Path(__file__).resolve().parent / "worker.py"
```

**`on_unmount` extension** — also terminate the review subprocess:
```python
async def on_unmount(self) -> None:
    for proc in (self._sync_proc, self._review_proc):
        if proc is not None and proc.returncode is None:
            try:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    proc.kill()
            except ProcessLookupError:
                pass
```

### 3.2 `tui/widgets/footer_bar.py`

Extend signature:
```python
def update_status(
    self, filter_mode: str, sort_mode: str,
    *, sync_running: bool = False, review_running: bool = False,
) -> None:
    sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
    review_label = "[r] review (running…)" if review_running else "[r] review"
    text = (
        f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
        f"  [j/k] nav  [q] quit  ·  {sync_label}  {review_label}"
    )
    self.update(text)
```

Note: the `[r] run (disabled)` legacy slot from γ goes away — `r` is now wired.

### 3.3 `tui/widgets/help_screen.py`

Add the `r` line right under the `s` line:

```
  s              start `adk pr-sync` (streams into log pane)
  r              start a review on the highlighted row (claim+prepare+claude)
```

### 3.4 Add `import sys` to `tui/app.py`

`_run_review` uses `sys.executable`.

---

## 4. Agent C — tests

### 4.1 New fixtures in `tui/tests/conftest.py`

```python
@pytest.fixture
def fake_claude_script(tmp_path: Path) -> Path:
    p = tmp_path / "fake-claude"
    p.write_text(
        "#!/bin/sh\n"
        "echo '[claude] phase 2: querying'\n"
        "echo '[claude] phase 5: posting comments'\n"
        "echo '[claude] phase 6: report'\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p


@pytest.fixture
def worker_heartbeat_dir(tmp_path: Path) -> Path:
    d = tmp_path / "tui-workers"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.fixture
def eligible_queue_path(tmp_path: Path) -> Path:
    """A queue with exactly one row that's ready_for_review=True."""
    src = Path(__file__).resolve().parent / "fixtures" / "eligible_queue.json5"
    dst = tmp_path / "eligible-queue.json5"
    shutil.copyfile(src, dst)
    return dst
```

### 4.2 `tui/tests/fixtures/eligible_queue.json5`

A queue with one row whose `prep_status="ready"`, `prep_head_sha` matches `head_sha`, `status="pending"`, `taken_at=None`. The exact fields come from inspecting `queue_io.ready_for_review`'s predicate — copy from `tui/tests/fixtures/sample_queue.json5` and tweak.

### 4.3 `tui/tests/test_worker.py`

Unit + integration tests for `tui/worker.py`. Use a FAKE `adk` binary fixture (already exists as `fake_adk_script` from γ) AND a fake `claude` binary fixture (new). Run the worker as a real subprocess via `python3 tui/worker.py`.

Tests:
1. **Happy path**: invoke worker with `pr_url`, `--adk-bin=<fake_adk>`, `--agent-bin=<fake_claude>`, `--heartbeat-dir=<tmp>`, `--heartbeat-file-interval-s=0.1`, `--heartbeat-bump-interval-s=0.5`, `--no-prepare`. Worker exits 0. Stdout contains `(claimed: ...)`, `$ <fake_claude> ...`, the 3 claude lines, `(review exited rc=0)`, `(released: ...)`.
2. **Heartbeat file**: same setup, but inspect the heartbeat dir mid-run by adding a slow agent that sleeps. Assert at least one `<pid>.json` file exists with `pid`, `pr_url`, `task_type=review`, `current_phase=review`. After exit, the file is removed.
3. **Claim failure**: fake_adk script that exits 2 on `pr-queue claim`. Worker exits 2 with "(error: claim failed ...)" in stdout.
4. **Agent failure**: fake_claude exits 1. Worker exits 1, called release with `--status error` (verify by inspecting fake_adk's recording).
5. **Invalid pr_url**: pass `not-a-url`. Worker exits 2 with "(error: invalid pr_url ...)".
6. **SIGTERM**: spawn worker with a fake_claude that sleeps 30s; send SIGTERM; assert worker exits 130 within 3s; heartbeat file removed; release was called.

**fake_adk recording**: tests need a fake_adk that records what verbs were called. Make it write to a logfile:
```sh
#!/bin/sh
echo "$@" >> "$ADK_FAKE_LOG"
case "$1" in
  pr-queue) ;;        # claim / heartbeat / release
  pr-task) ;;         # prepare
esac
echo "ok"
exit 0
```
Fail-cases set `ADK_FAKE_RC=2` to make it exit non-zero.

### 4.4 `tui/tests/test_review_action.py`

Pilot tests for the TUI `r` action:
1. **`r` with no row selected** → LogPane shows `(no row selected)`.
2. **`r` on a not-ready row** → LogPane shows `(row not ready: ...)`.
3. **`r` on an eligible row** → LogPane shows `$ <python> <worker.py> <pr_url> ...`, then the worker's output, then `(worker exited rc=0)`. Footer flips to `[r] review (running…)` mid-run and back to `[r] review` after.
4. **`s` while a review is running** → LogPane shows `(can't start sync — review already running)`.
5. **`r` while a sync is running** → LogPane shows `(can't start review — sync already running)`.

All Pilot tests pass `worker_script`, `agent_bin=fake_claude_script`, `adk_bin=fake_adk_script`, `heartbeat_dir=worker_heartbeat_dir`, plus `queue_path=eligible_queue_path` for tests #3-5.

Use the same `_poll_until` helper from `test_sync_action.py`.

### 4.5 Test environment for fake_adk

Tests need to pass `ADK_FAKE_LOG` (and optionally `ADK_FAKE_RC`) into the worker subprocess's env. The worker forwards `os.environ` to its children, so simply setting these env vars before launching the worker via Pilot works (TUI inherits process env).

---

## 5. Visual contract

The visible TUI is unchanged from γ except:
- Footer's `[r] run (disabled)` is now `[r] review` (or `[r] review (running…)` mid-flight).
- LogPane shows the worker's lines.

---

## 6. Definition of done

- `python3 tui/worker.py <fake_pr_url> --adk-bin=<fake_adk> --agent-bin=<fake_claude> --no-prepare --heartbeat-dir=<tmp> --heartbeat-bump-interval-s=0.5 --heartbeat-file-interval-s=0.1` → exits 0; heartbeat file existed mid-run and is gone post-run; fake_adk log shows `pr-queue claim`, ≥1 `pr-queue heartbeat`, `pr-queue release`.
- TUI: launch `adk`, highlight an eligible row, press `r`, see worker output stream into the LogPane.
- Pressing `s` while review is running → blocked message in LogPane. Pressing `r` while sync is running → blocked message.
- Quitting TUI mid-review sends SIGTERM; worker releases lock and removes heartbeat file.
- Test count goes up by ≥ 8 (5 worker + 5 review-action ≈ 10). No regressions.

---

## 7. Spec deviations — explicit policy

Same as γ §8. Small, named deviations OK; surface in your completion message.
