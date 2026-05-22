# TUI sub-phase θ — binding interface SPEC

Status: **frozen**, parallel build. Companion to `SPEC.md`, `SPEC-gamma.md`, `SPEC-delta.md`.

δ shipped the worker driver + heartbeat-file *writer*. θ adds:
1. **Worker `_run_sync` → async-streaming refactor**. Closes the S-1 / M-3 follow-ups from δ's review: the asyncio SIGTERM handler is installed once at the top of `_drive` and applies to every step (claim / prepare / release); claim/prepare/release stdout streams line-by-line instead of being buffered until the call completes.
2. **WorkersModel reader** that scans `~/.agents-devkit/tui/workers/*.json` mtime-gated, parses each `<pid>.json` heartbeat file, decides stale-vs-fresh based on `last_heartbeat` age, and offers a GC method that deletes files older than the GC threshold.
3. **WorkersPane** Textual widget that renders one line per active worker (pr_url, task_type, phase, agent, age). Polls the WorkersModel every 2 s. Empty state when no workers are running.
4. **`test_sigterm_releases_and_cleans_heartbeat` unflake** (S-3). The test currently sends SIGTERM unconditionally even if the heartbeat file never appeared within the 3 s poll window. With the refactor in §1 the signal handler is installed before claim runs, so the test can `assert_eventually` the heartbeat file exists before sending the signal.

All α+β+γ+δ behavior must keep working. The existing 468 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/worker.py` (MODIFIED — async refactor) | `_common.py`, `queue_io.py` |
| **B** | `adk-agent-implementer` | `tui/app.py` (MODIFIED — WorkersPane wiring + poll), `tui/styles.tcss` (MODIFIED), `tui/widgets/__init__.py` (MODIFIED), `tui/widgets/workers_pane.py` (NEW), `tui/model/__init__.py` (MODIFIED), `tui/model/workers_model.py` (NEW) | all α+β+γ+δ files |
| **C** | `adk-agent-test-engineer` | `tui/tests/test_worker_async.py` (NEW — covers the S-1 fix + M-3 streaming), `tui/tests/test_workers_model.py` (NEW), `tui/tests/test_workers_pane.py` (NEW), `tui/tests/test_worker.py` (MODIFIED — unflake S-3), `tui/tests/conftest.py` (MODIFIED — add `workers_dir_with_two`, `fake_slow_adk_script`, `stale_worker_file` fixtures) | everything |

**Hard rule**: A does not touch TUI widgets or tests. B does not touch worker.py or tests. C does not write production code.

---

## 2. Agent A — worker.py async refactor

### 2.1 Replace `_run_sync` with `_run_streamed`

```python
async def _run_streamed(cmd: list[str]) -> int:
    """Async streaming variant of the previous blocking _run_sync. stdout is
    line-buffered to OUR stdout so the TUI tails it live; rc is returned."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        sys.stdout.write(line.decode(errors="replace"))
        sys.stdout.flush()
    return await proc.wait()
```

The old `_run_sync` is **removed**. All three call sites (claim, prepare, release) now `await _run_streamed(cmd)`.

### 2.2 Hoist the SIGTERM handler

Currently the `add_signal_handler` call is at line 159 — between prepare and the agent spawn. **Move it to the very top of `_drive`**, right after `parse_pr_url`. The handler closure needs `agent_proc` to be a nonlocal that's `None` initially and reassigned later:

```python
async def _drive(args):
    try:
        parse_pr_url(args.pr_url)
    except Exception as exc:
        _emit(f"(error: invalid pr_url: {exc})")
        return 2

    adk_bin = ...; agent_bin = ...; queue = ...

    agent_proc: asyncio.subprocess.Process | None = None
    sig_received = False

    def _on_sigterm() -> None:
        nonlocal sig_received
        sig_received = True
        if agent_proc is not None and agent_proc.returncode is None:
            try:
                agent_proc.terminate()
            except ProcessLookupError:
                pass

    try:
        asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, _on_sigterm)
    except NotImplementedError:  # pragma: no cover
        pass

    # Now claim/prepare/release calls run with the handler in place.
    ...
```

### 2.3 Add `sig_received` checks between steps

After each `await _run_streamed(...)`, before proceeding:
- After claim succeeds: if `sig_received`, immediately call release (status=error) and return 130.
- After prepare succeeds: same.
- After agent spawn fails: same (lock release with --status error).

```python
rc = await _run_streamed([adk_bin, "pr-queue", "claim", args.pr_url, "--queue", queue])
if rc != 0:
    _emit("(error: claim failed — row may be locked by another reviewer)")
    return 2
_emit(f"(claimed: {args.pr_url})")
if sig_received:
    await _release(adk_bin, args.pr_url, queue, status="error")
    return 130

if not args.no_prepare:
    prep_cmd = [adk_bin, "pr-task", "prepare", args.pr_url, "--queue", queue]
    _emit("$ " + " ".join(prep_cmd))
    rc = await _run_streamed(prep_cmd)
    if rc != 0:
        _emit(f"(error: prepare failed rc={rc})")
        await _release(adk_bin, args.pr_url, queue, status="error")
        return 1
    if sig_received:
        await _release(adk_bin, args.pr_url, queue, status="error")
        return 130
```

Helper:
```python
async def _release(adk_bin: str, pr_url: str, queue: str, *, status: str | None = None) -> None:
    cmd = [adk_bin, "pr-queue", "release", pr_url, "--queue", queue]
    if status:
        cmd += ["--status", status]
    rc = await _run_streamed(cmd)
    if rc == 0:
        _emit(f"(released: {pr_url})")
    else:
        _emit(f"(error: release rc={rc} — lock may be stuck)")
```

The existing `finally` block at line 174 can now use this helper.

### 2.4 Constraints unchanged

- Exit codes unchanged (§2.4 of SPEC-delta).
- stdout contract unchanged (§2.5 of SPEC-delta) — the order of lines is the same; only the timing changes (streaming now).
- Heartbeat schema unchanged.
- ≤ 250 LOC; refactor should NOT bloat the file. Likely shrinks by removing `_run_sync` and the legacy duplicate release-after-prepare-fail block (now handled by `_release` helper).

### 2.5 Verify

After the refactor, run:
```
python3 tui/worker.py https://github.com/foo/bar/pull/200 \
  --adk-bin /tmp/fake-adk --agent-bin /tmp/fake-claude \
  --queue /tmp/q --heartbeat-dir /tmp/w \
  --no-prepare --heartbeat-bump-interval-s 0.3 --heartbeat-file-interval-s 0.1
```
Output should be identical to δ's smoke (modulo timing). All 6 existing `test_worker.py` tests still pass.

---

## 3. Agent B — WorkersModel + WorkersPane + TUI wiring

### 3.1 `tui/model/workers_model.py` (NEW)

```python
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class WorkerRow:
    pid: int
    pr_url: str
    task_type: str
    agent: str
    queue: str
    started_at: str
    last_heartbeat: str
    current_phase: str
    rc: int | None
    age_s: float
    is_stale: bool


def default_workers_dir() -> Path:
    return Path.home() / ".agents-devkit" / "tui" / "workers"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


class WorkersModel:
    """Scans a directory of <pid>.json heartbeat files. Returns the live ones,
    GCs the dead. Mtime-gated by directory mtime AND by aggregate file mtime
    (to catch a single file's update without a directory mutation)."""

    def __init__(
        self,
        workers_dir: Path | None = None,
        *,
        stale_after_s: float = 30.0,
        gc_after_s: float = 120.0,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.workers_dir = workers_dir if workers_dir is not None else default_workers_dir()
        self.stale_after_s = stale_after_s
        self.gc_after_s = gc_after_s
        if now_fn is None:
            now_fn = lambda: datetime.now(tz=timezone.utc)  # noqa: E731
        self._now_fn = now_fn
        self._last_signature: tuple | None = None

    def _signature(self) -> tuple:
        """Cheap directory fingerprint. (dir_mtime, [(name, mtime, size)...])."""
        if not self.workers_dir.exists():
            return (0.0, ())
        try:
            dm = self.workers_dir.stat().st_mtime
        except OSError:
            return (0.0, ())
        items: list[tuple[str, float, int]] = []
        try:
            for p in self.workers_dir.iterdir():
                if p.suffix == ".json":
                    try:
                        st = p.stat()
                        items.append((p.name, st.st_mtime, st.st_size))
                    except OSError:
                        continue
        except OSError:
            return (dm, ())
        items.sort()
        return (dm, tuple(items))

    def has_changed(self) -> bool:
        cur = self._signature()
        if cur != self._last_signature:
            return True
        return False

    def snapshot(self) -> list[WorkerRow]:
        self._last_signature = self._signature()
        if not self.workers_dir.exists():
            return []
        now = self._now_fn()
        rows: list[WorkerRow] = []
        for p in sorted(self.workers_dir.iterdir()):
            if p.suffix != ".json":
                continue
            row = self._parse_one(p, now)
            if row is None:
                continue
            rows.append(row)
        return rows

    def gc(self) -> int:
        """Remove heartbeat files older than gc_after_s. Returns the count removed."""
        if not self.workers_dir.exists():
            return 0
        now = self._now_fn()
        removed = 0
        for p in self.workers_dir.iterdir():
            if p.suffix != ".json":
                continue
            try:
                raw = json.loads(p.read_text())
                last = _parse_iso(raw.get("last_heartbeat"))
            except (OSError, json.JSONDecodeError, TypeError):
                last = None
            if last is None:
                # Unparseable file — GC if its mtime is also old enough.
                try:
                    file_age = (now.timestamp() - p.stat().st_mtime)
                except OSError:
                    continue
                if file_age > self.gc_after_s:
                    self._unlink(p)
                    removed += 1
                continue
            age = (now - last).total_seconds()
            if age > self.gc_after_s:
                self._unlink(p)
                removed += 1
        return removed

    def _parse_one(self, p: Path, now: datetime) -> WorkerRow | None:
        try:
            raw = json.loads(p.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        last = _parse_iso(raw.get("last_heartbeat"))
        if last is None:
            return None
        age = (now - last).total_seconds()
        is_stale = age > self.stale_after_s
        try:
            return WorkerRow(
                pid=int(raw.get("pid", 0)),
                pr_url=str(raw.get("pr_url", "")),
                task_type=str(raw.get("task_type", "")),
                agent=str(raw.get("agent", "")),
                queue=str(raw.get("queue", "")),
                started_at=str(raw.get("started_at", "")),
                last_heartbeat=str(raw.get("last_heartbeat", "")),
                current_phase=str(raw.get("current_phase", "")),
                rc=raw.get("rc"),
                age_s=age,
                is_stale=is_stale,
            )
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _unlink(p: Path) -> None:
        try:
            p.unlink()
        except OSError:
            pass
```

### 3.2 `tui/widgets/workers_pane.py` (NEW)

```python
from __future__ import annotations

from textual.widgets import Static

from tui.model.workers_model import WorkerRow


class WorkersPane(Static):
    def __init__(self) -> None:
        super().__init__("(no active workers)", markup=False)

    def update_workers(self, rows: list[WorkerRow], *, ascii_only: bool = False) -> None:
        # Stale rows are hidden by default (the user only sees live workers).
        live = [r for r in rows if not r.is_stale]
        if not live:
            self.update("(no active workers)")
            return
        header = f"Workers ({len(live)} active)"
        body = [_format_row(r, ascii_only=ascii_only) for r in live]
        self.update("\n".join([header, *body]))


def _format_row(row: WorkerRow, *, ascii_only: bool) -> str:
    pr_short = _shorten(row.pr_url)
    age = _format_age(row.age_s)
    glyph = "⚙↻" if not ascii_only else "~"
    return f"  {glyph}  {pr_short}  ·  {row.task_type}/{row.current_phase}  ·  {row.agent}  ·  {age}"


def _shorten(pr_url: str) -> str:
    # https://github.com/acme/foo/pull/42 → acme/foo#42
    # https://bitbucket.org/o/r/pull-requests/5 → o/r#5
    import re
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    m = re.search(r"bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    return pr_url


def _format_age(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours}h"
    return f"{int(hours // 24)}d"
```

### 3.3 `tui/styles.tcss` — add WorkersPane styling

```tcss
WorkersPane {
    height: auto;
    min-height: 1;
    max-height: 10;
    padding: 0 1;
    background: $boost;
}
```

### 3.4 `tui/app.py` — wire it in

**Imports**:
```python
from tui.widgets.workers_pane import WorkersPane
if TYPE_CHECKING:
    from tui.model.workers_model import WorkersModel
```

**`__init__` additions**:
```python
self._workers_model: WorkersModel | None = None
self._workers_dir_override: Path | None = None  # populated from heartbeat_dir kwarg
```

(The `heartbeat_dir` kwarg from δ doubles as the workers-dir override here — single source of truth.)

**Compose** (modify):
```python
def compose(self) -> ComposeResult:
    yield HeaderBar()
    with Horizontal(id="main"):
        yield QueueTable()
        yield DetailPane()
    yield WorkersPane()
    yield SyncPlanPane()
    yield LogPane()
    yield FooterBar()
```

WorkersPane goes ABOVE SyncPlanPane to match the v4 plan §8.4 layout mock.

**`on_mount`**:
```python
async def on_mount(self) -> None:
    from tui.model.queue_model import QueueModel
    from tui.model.sync_plan_model import SyncPlanModel
    from tui.model.workers_model import WorkersModel

    self._model = QueueModel(queue_path=self._queue_path)
    self._plan_model = SyncPlanModel(plan_path=self._plan_path)
    self._workers_model = WorkersModel(workers_dir=self._heartbeat_dir)
    self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode)
    self._reload(force=True)
    self._reload_plan(force=True)
    self._reload_workers(force=True)
    self.set_interval(self.poll_interval, self._maybe_reload)
```

**`_reload_workers`**:
```python
def _reload_workers(self, *, force: bool = False) -> None:
    if self._workers_model is None:
        return
    if not force and not self._workers_model.has_changed():
        return
    rows = self._workers_model.snapshot()
    self.query_one(WorkersPane).update_workers(rows, ascii_only=self._ascii_only)
```

**`_maybe_reload`**:
```python
def _maybe_reload(self) -> None:
    if self._model is not None and self._model.has_changed():
        self._reload(force=True)
    self._reload_plan()
    self._reload_workers()
```

No GC from the TUI in this slice — the GC method exists on the model for future use (the `adk worker gc` CLI verb would call it). Stale rows are simply hidden from the WorkersPane.

### 3.5 Constraints

- `WorkersModel` ≤ 130 LOC.
- `WorkersPane` ≤ 60 LOC.
- No third-party deps.
- Don't break α/β/γ/δ tests.

---

## 4. Agent C — tests

### 4.1 New fixtures in `tui/tests/conftest.py`

```python
@pytest.fixture
def workers_dir_with_two(tmp_path: Path) -> Path:
    """A workers/ dir containing two fresh heartbeat files."""
    import json
    d = tmp_path / "workers"
    d.mkdir(parents=True)
    now_iso = "2026-05-22T14:00:00Z"
    for pid, pr in [(11111, "https://github.com/acme/foo/pull/42"),
                    (22222, "https://github.com/acme/bar/pull/7")]:
        (d / f"{pid}.json").write_text(json.dumps({
            "pid": pid, "pr_url": pr, "task_type": "review",
            "agent": "claude", "queue": "/tmp/q",
            "started_at": now_iso, "last_heartbeat": now_iso,
            "current_phase": "review", "rc": None,
        }))
    return d


@pytest.fixture
def stale_worker_file(tmp_path: Path) -> Path:
    """A workers/ dir with a single STALE heartbeat (5 min ago)."""
    import json
    d = tmp_path / "workers"
    d.mkdir(parents=True)
    old_iso = "2026-05-22T13:55:00Z"
    (d / "99999.json").write_text(json.dumps({
        "pid": 99999, "pr_url": "https://github.com/acme/old/pull/1",
        "task_type": "review", "agent": "claude", "queue": "/tmp/q",
        "started_at": old_iso, "last_heartbeat": old_iso,
        "current_phase": "review", "rc": None,
    }))
    return d


@pytest.fixture
def fake_slow_adk_script(tmp_path: Path) -> Path:
    """A /bin/sh adk that takes >1s to complete each verb — used by the SIGTERM
    streaming tests. Reads $ADK_SLOW_S (default 2) for sleep duration."""
    p = tmp_path / "slow-adk"
    p.write_text(
        "#!/bin/sh\n"
        "echo \"slow-adk $@\"\n"
        "sleep \"${ADK_SLOW_S:-2}\"\n"
        "echo ok\n"
        "exit 0\n"
    )
    p.chmod(0o755)
    return p
```

### 4.2 `tui/tests/test_workers_model.py`

- Empty dir → `snapshot()` is `[]`; `has_changed()` returns False on second call.
- Two fresh files → `snapshot()` returns 2 WorkerRow with `is_stale=False`.
- Stale file (5 min ago) → `snapshot()` returns 1 row with `is_stale=True`; `age_s > stale_after_s`.
- Corrupt JSON file → row excluded from snapshot (no crash).
- Wrong shape (missing `last_heartbeat`) → row excluded.
- `gc()` removes only files older than `gc_after_s` (test: fresh stays, very-old removed). Returns count.
- `has_changed()` returns True after a new file is added.

Inject `now_fn` so the tests don't depend on wall clock.

### 4.3 `tui/tests/test_workers_pane.py`

- Empty list → "(no active workers)".
- Two live rows → header "Workers (2 active)" + two `acme/foo#42`-style lines + each row contains `task_type/current_phase` + `claude` + age.
- ASCII mode swaps glyph to `~`.
- Stale rows ARE HIDDEN — pane renders empty if all rows are stale.

### 4.4 `tui/tests/test_workers_pane_integration.py` (Pilot, optional)

Construct AdkApp with `heartbeat_dir=workers_dir_with_two`, poll, assert WorkersPane render contains the two PR shortcodes. This may be merged into `test_workers_pane.py` with a Pilot helper if it's the only Pilot-style test for this feature.

### 4.5 `tui/tests/test_worker_async.py`

Tests that exercise the S-1 / M-3 fixes. These use the real `tui/worker.py` script as a subprocess (just like `test_worker.py`).

1. **`test_streamed_prepare_output_arrives_line_by_line`** (M-3 fix). Use a slow adk script that emits 3 separate echo lines with a 0.3s `sleep` between each (configurable via env). Launch the worker with `--no-prepare=false`; while it's running, poll its stdout via `Popen.stdout.readline()` with a timeout. Assert the 3 lines arrive incrementally (each within 1.5s) rather than all at the end.

2. **`test_sigterm_mid_prepare_releases_lock`** (S-1 fix). Use a slow adk that sleeps 3 s on `pr-task prepare`. Launch the worker. Wait until the worker has emitted the first prepare line (so we know it's inside the prepare call). Send SIGTERM. Worker should exit 130 within 3 s. Verify the recording adk log shows `pr-queue release` was called.

3. **`test_sigterm_before_claim_releases_nothing`** — invariant check. SIGTERM before claim completes → exit 130 immediately, NO release call (nothing was acquired).

### 4.6 `tui/tests/test_worker.py` — unflake S-3

The existing test:
```python
deadline = time.time() + 3.0
while time.time() < deadline:
    if list(worker_heartbeat_dir.glob("*.json")):
        break
    time.sleep(0.05)
proc.send_signal(signal.SIGTERM)
```

becomes:

```python
deadline = time.time() + 3.0
while time.time() < deadline:
    if list(worker_heartbeat_dir.glob("*.json")):
        break
    time.sleep(0.05)
else:
    proc.terminate()  # belt and suspenders cleanup
    proc.wait(timeout=2)
    pytest.fail("heartbeat file never appeared within 3 s")
proc.send_signal(signal.SIGTERM)
```

(The `for-else` pattern fires only if the loop exits without breaking.)

---

## 5. Definition of done

- `python3 tui/worker.py ...` smoke output identical to δ's (modulo timing). All 6 existing `test_worker.py` tests pass.
- New `test_worker_async.py` has at least 3 tests, all passing.
- `WorkersModel.snapshot()` returns the expected fields. `gc()` removes stale files when called.
- WorkersPane renders empty state + populated state correctly.
- TUI launch: when no review running, WorkersPane shows "(no active workers)". When a review starts, the pane shows that row.
- 468 baseline tests stay green. New test count up by ≥ 10.

---

## 6. Spec deviations — explicit policy

Same as γ/δ. Small, named deviations OK; surface in your completion message.
