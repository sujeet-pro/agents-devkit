# TUI sub-phase γ — binding interface SPEC

Status: **frozen**, parallel build. Companion to `SPEC.md` (α+β).

The α+β slice shipped a read-only queue viewer. γ adds:
1. `s` key spawns `adk pr-sync` as a subprocess and streams stdout into a new **Log pane**.
2. `pr_sync.py` emits a structured plan file at `~/.agents-devkit/tui/workers/sync-plan.json` at each step boundary.
3. The TUI has a new **Sync-plan pane** that reads that file mtime-gated and renders each step's status.

All three pieces must be built without breaking α+β. The existing 18 TUI tests + 1 quiet-hours test must keep passing.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `skills/adk-cli/scripts/tui_plan.py` (NEW), `skills/adk-cli/scripts/pr_sync.py` (MODIFIED) | `_common.py`, `queue_io.py` |
| **B** | `adk-agent-implementer` | `tui/app.py` (MODIFIED), `tui/styles.tcss` (MODIFIED), `tui/widgets/footer_bar.py` (MODIFIED), `tui/widgets/help_screen.py` (MODIFIED), `tui/widgets/__init__.py` (MODIFIED), `tui/widgets/log_pane.py` (NEW), `tui/widgets/sync_plan_pane.py` (NEW), `tui/model/__init__.py` (MODIFIED), `tui/model/sync_plan_model.py` (NEW) | all α+β files |
| **C** | `adk-agent-test-engineer` | `tui/tests/test_sync_plan_model.py` (NEW), `tui/tests/test_sync_plan_pane.py` (NEW), `tui/tests/test_sync_action.py` (NEW), `tui/tests/fixtures/sample_sync_plan.json` (NEW), `skills/adk-cli/scripts/tests/test_pr_sync_plan.py` (NEW), `tui/tests/conftest.py` (MODIFIED — add `fake_plan_path`, `sync_plan_in_progress`, `fake_adk_script` fixtures) | everything |

**Hard rule**: A does not touch any `tui/`. B does not touch any `skills/adk-cli/scripts/`. C does not touch any code outside `tests/` and `conftest.py`.

---

## 2. The plan-file contract (binding for A and B)

**Path**: `~/.agents-devkit/tui/workers/sync-plan.json` (call it `PLAN_PATH`). Override via `ADK_TUI_PLAN_PATH` env var (used by tests).

**Schema** (versioned; A writes, B reads):

```json
{
  "version": 1,
  "queue": "/Users/sujeet/.agents-devkit/config/pr-queue.json5",
  "argv": ["--no-scan"],
  "started_at": "2026-05-22T14:32:15Z",
  "updated_at": "2026-05-22T14:33:01Z",
  "completed_at": null,
  "rc": null,
  "steps": [
    {
      "name": "pr-scan",
      "status": "ok",
      "rc": 0,
      "started_at": "2026-05-22T14:32:15Z",
      "completed_at": "2026-05-22T14:32:42Z"
    },
    {
      "name": "pr-queue update --all",
      "status": "running",
      "rc": null,
      "started_at": "2026-05-22T14:32:42Z",
      "completed_at": null
    },
    {
      "name": "pr-queue clean (merged)",
      "status": "pending",
      "rc": null,
      "started_at": null,
      "completed_at": null
    }
  ]
}
```

**Field semantics**:
- `version`: int, currently `1`. B treats `version != 1` as "unknown — show raw text".
- `queue`: string, queue path the sync targets.
- `argv`: list[str], the pr-sync argv (for context; B may show in pane footer).
- `started_at` / `updated_at` / `completed_at`: ISO 8601 UTC with `Z` suffix.
- `rc`: int | null. Set on completion; sum-of-failures-style (0 == all ok, 1 == any failed).
- `steps[].name`: string. **Stable identifier** the user sees; matches the human label in pr_sync.
- `steps[].status`: one of `pending`, `running`, `ok`, `warn`, `failed`, `skipped`. (B has icons for each; see §5.2.)
- `steps[].rc`: int | null (null while pending / running).
- `steps[].started_at`, `steps[].completed_at`: ISO 8601 UTC with `Z` or null.

**Atomic writes**: A writes to `PLAN_PATH.tmp` then `os.replace(PLAN_PATH.tmp, PLAN_PATH)`. Never partially-written JSON.

**Resilience**: if `PLAN_PATH` is unparseable or missing required keys, B treats it as "no plan" (does NOT crash). C's test_sync_plan_model has a corrupt-file fixture.

---

## 3. Agent A — pr_sync.py instrumentation

### 3.1 New module: `skills/adk-cli/scripts/tui_plan.py`

```python
"""TUI sync-plan writer. Persists ~/.agents-devkit/tui/workers/sync-plan.json
during pr-sync execution so the TUI's Sync-plan pane can render live progress.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

PLAN_VERSION = 1

DEFAULT_PLAN_PATH = Path.home() / ".agents-devkit" / "tui" / "workers" / "sync-plan.json"

StepStatus = Literal["pending", "running", "ok", "warn", "failed", "skipped"]


def plan_path() -> Path:
    """Return ADK_TUI_PLAN_PATH if set, else DEFAULT_PLAN_PATH."""
    env = os.environ.get("ADK_TUI_PLAN_PATH")
    return Path(env) if env else DEFAULT_PLAN_PATH


@dataclass
class StepRecord:
    name: str
    status: StepStatus = "pending"
    rc: int | None = None
    started_at: str | None = None
    completed_at: str | None = None


class SyncPlanWriter:
    """Append-only step tracker that persists to PLAN_PATH atomically."""

    def __init__(self, queue: str, argv: list[str], step_names: list[str], *, path: Path | None = None) -> None:
        self.path = path if path is not None else plan_path()
        self._queue = queue
        self._argv = list(argv)
        self._steps: list[StepRecord] = [StepRecord(name=n) for n in step_names]
        self._started_at = _utc_now_iso()
        self._completed_at: str | None = None
        self._rc: int | None = None
        self._index_by_name: dict[str, int] = {n: i for i, n in enumerate(step_names)}
        self._write()  # initial snapshot — TUI sees plan as soon as pr-sync starts

    def step_start(self, name: str) -> None:
        rec = self._get(name)
        rec.status = "running"
        rec.started_at = _utc_now_iso()
        self._write()

    def step_done(self, name: str, *, status: StepStatus, rc: int | None = None) -> None:
        rec = self._get(name)
        rec.status = status
        rec.rc = rc
        rec.completed_at = _utc_now_iso()
        self._write()

    def finish(self, rc: int) -> None:
        self._completed_at = _utc_now_iso()
        self._rc = rc
        self._write()

    # --- internals ---
    def _get(self, name: str) -> StepRecord:
        idx = self._index_by_name.get(name)
        if idx is None:
            # Tolerant: append a new step on the fly. Keeps pr_sync evolution painless.
            rec = StepRecord(name=name)
            self._steps.append(rec)
            self._index_by_name[name] = len(self._steps) - 1
            return rec
        return self._steps[idx]

    def _write(self) -> None:
        payload = {
            "version": PLAN_VERSION,
            "queue": self._queue,
            "argv": self._argv,
            "started_at": self._started_at,
            "updated_at": _utc_now_iso(),
            "completed_at": self._completed_at,
            "rc": self._rc,
            "steps": [asdict(s) for s in self._steps],
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2))
        os.replace(tmp, self.path)


def _utc_now_iso() -> str:
    import datetime as _dt
    return _dt.datetime.now(tz=_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
```

**A must keep this module ≤120 LOC.** No extra fields. No `dataclasses_json` or third-party libs.

### 3.2 `pr_sync.py` modifications

The existing step list is, in order:
```
pr-scan
pr-queue update --all
pr-queue clean (merged)
pr-task clean-orphans                       (or '… (dry-run)' suffix when --dry-run)
pr-queue remind                             (or '… (dry-run)' suffix when --dry-run)
base-index audit
auto-base cleanup
pr-task prepare --all
```

(When a `--no-<step>` flag is set, the step still appears in the plan but with `status="skipped"`.)

**At the top of `main()` (after argparse, before step 1)**:
```python
from tui_plan import SyncPlanWriter  # NEW import (lazy in main, not module-level)

_PR_SYNC_STEPS = [
    "pr-scan",
    "pr-queue update --all",
    "pr-queue clean (merged)",
    "pr-task clean-orphans",
    "pr-queue remind",
    "base-index audit",
    "auto-base cleanup",
    "pr-task prepare --all",
]
plan_writer = SyncPlanWriter(queue=queue, argv=list(argv or []), step_names=_PR_SYNC_STEPS)
```

**Refactor `_run_step` to take the writer**:
```python
def _run_step(name: str, fn, log, *, plan: SyncPlanWriter | None = None) -> dict:
    log.info("=== step: %s ===", name)
    if plan is not None:
        plan.step_start(name)
    try:
        rc = fn()
        status = "ok" if rc == 0 else "warn"
        if plan is not None:
            plan.step_done(name, status=status, rc=rc)
        return {"step": name, "rc": rc, "status": status}
    except SystemExit as e:
        log.warning("%s: %s", name, e)
        if plan is not None:
            plan.step_done(name, status="failed", rc=1)
        return {"step": name, "rc": 1, "status": "failed", "reason": str(e)}
    except Exception as e:
        log.warning("%s: unexpected %s", name, e)
        if plan is not None:
            plan.step_done(name, status="failed", rc=1)
        return {"step": name, "rc": 1, "status": "failed", "reason": str(e)}
```

**Pass `plan=plan_writer` to every `_run_step` call.**

**For the special-cased branches that don't go through `_run_step`** (the base-index audit and the auto-base cleanup), wrap them with explicit `plan_writer.step_start("base-index audit")` / `plan_writer.step_done("base-index audit", status=..., rc=...)` calls.

**Skipped steps**: when the user passes `--no-scan`, `--no-clean-orphans`, `--no-remind`, `--no-prepare`, `--no-base-audit`, `--no-auto-demote`, mark that step `status="skipped"` (and never call `step_start`).

```python
if args.no_scan:
    plan_writer.step_done("pr-scan", status="skipped")
    results.append({"step": "pr-scan", "status": "skipped"})
else:
    # … existing code, including _run_step(..., plan=plan_writer)
```

**The suffix-renamed steps** (`pr-task clean-orphans (dry-run)`, `pr-queue remind (dry-run)`) must still map back to the canonical step name in the plan. **Strategy**: emit `step_start("pr-task clean-orphans")` (without the suffix) — the plan tracks the canonical name; the suffix is only in the log/CLI summary. This keeps the plan consistent regardless of `--dry-run`.

**At the very end**:
```python
rc_out = 1 if summary["failed"] else 0
plan_writer.finish(rc_out)
return rc_out
```

**Behavior preservation**: the existing `print(json.dumps(summary, ...))` MUST stay (the CLI output is a downstream contract). The plan-writer is purely additive.

### 3.3 Verify

- `python3 -m skills.adk-cli.scripts.pr_sync --no-scan --no-clean-orphans --no-remind --no-prepare --no-base-audit --no-auto-demote --queue /tmp/empty.json5` → plan emitted with all steps `skipped`, two non-skipped steps either ok/warn, plan completes.
- All pre-existing pr_sync tests still pass.

---

## 4. Agent B — TUI panes + sync action

### 4.1 New widget: `tui/widgets/log_pane.py`

```python
from __future__ import annotations

from textual.widgets import RichLog


class LogPane(RichLog):
    """Streaming output pane for `adk pr-sync` stdout."""

    def __init__(self) -> None:
        super().__init__(highlight=False, markup=False, wrap=False, auto_scroll=True)

    def announce(self, msg: str) -> None:
        """Write a meta-line (start/exit/error). The pane doesn't distinguish
        types; the message itself includes its prefix."""
        self.write(msg)
```

- `markup=False` for the same Rich-bracket reason as α+β.
- Use `write(line)` for each stdout line. RichLog auto-scrolls.

### 4.2 New widget: `tui/widgets/sync_plan_pane.py`

```python
from __future__ import annotations

from textual.widgets import Static

from tui.model.sync_plan_model import SyncPlanSnapshot

_ICONS = {
    "pending":  ("…",  "[--]"),
    "running":  ("⚡", "[..]"),
    "ok":       ("✓",  "[ok]"),
    "warn":     ("⚠",  "[wn]"),
    "failed":   ("✗",  "[fl]"),
    "skipped":  ("↷",  "[sk]"),
}


class SyncPlanPane(Static):
    def __init__(self) -> None:
        super().__init__("(no sync run yet — press `s` to start)", markup=False)

    def update_snapshot(self, snapshot: SyncPlanSnapshot | None, *, ascii_only: bool = False) -> None:
        if snapshot is None:
            self.update("(no sync run yet — press `s` to start)")
            return
        # First line: header. Second line onwards: one step per row.
        header = _format_header(snapshot)
        body = [_format_step(s, ascii_only=ascii_only) for s in snapshot.steps]
        self.update("\n".join([header, *body]))


def _format_header(snap: SyncPlanSnapshot) -> str:
    done = sum(1 for s in snap.steps if s.status in ("ok", "warn", "failed", "skipped"))
    total = len(snap.steps)
    if snap.completed_at is not None:
        outcome = "✓ done" if (snap.rc or 0) == 0 else "✗ done (with failures)"
        return f"Sync plan ({outcome} · {done}/{total} steps)"
    return f"Sync plan (running · {done}/{total} steps)"


def _format_step(step, *, ascii_only: bool) -> str:
    icon = _ICONS[step.status][1 if ascii_only else 0]
    return f"  {icon}  {step.name}"
```

### 4.3 New model: `tui/model/sync_plan_model.py`

```python
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SyncPlanStep:
    name: str
    status: str
    rc: int | None
    started_at: str | None
    completed_at: str | None


@dataclass(frozen=True)
class SyncPlanSnapshot:
    queue: str
    started_at: str
    updated_at: str
    completed_at: str | None
    rc: int | None
    steps: list[SyncPlanStep]


def default_plan_path() -> Path:
    env = os.environ.get("ADK_TUI_PLAN_PATH")
    if env:
        return Path(env)
    return Path.home() / ".agents-devkit" / "tui" / "workers" / "sync-plan.json"


class SyncPlanModel:
    def __init__(self, plan_path: Path | None = None) -> None:
        self.plan_path = plan_path if plan_path is not None else default_plan_path()
        self._last_mtime: float | None = None

    def has_changed(self) -> bool:
        if not self.plan_path.exists():
            return self._last_mtime not in (None, 0.0) or self._last_mtime is None
        try:
            cur = self.plan_path.stat().st_mtime
        except OSError:
            return False
        return cur != self._last_mtime

    def snapshot(self) -> SyncPlanSnapshot | None:
        if not self.plan_path.exists():
            self._last_mtime = 0.0
            return None
        try:
            self._last_mtime = self.plan_path.stat().st_mtime
            raw = json.loads(self.plan_path.read_text())
        except (OSError, json.JSONDecodeError):
            return None
        if raw.get("version") != 1:
            return None
        try:
            steps = [
                SyncPlanStep(
                    name=str(s.get("name", "")),
                    status=str(s.get("status", "pending")),
                    rc=s.get("rc"),
                    started_at=s.get("started_at"),
                    completed_at=s.get("completed_at"),
                )
                for s in raw.get("steps") or []
            ]
            return SyncPlanSnapshot(
                queue=str(raw.get("queue", "")),
                started_at=str(raw.get("started_at", "")),
                updated_at=str(raw.get("updated_at", "")),
                completed_at=raw.get("completed_at"),
                rc=raw.get("rc"),
                steps=steps,
            )
        except (TypeError, ValueError):
            return None
```

The `has_changed()` returns True on first call even when no file exists (so the pane gets the initial "(no sync run yet)" render). After that, it only returns True on real mtime change OR on a transition from "exists" ↔ "doesn't exist".

### 4.4 `tui/widgets/__init__.py` and `tui/model/__init__.py`

Add `from .log_pane import LogPane` and `from .sync_plan_pane import SyncPlanPane` to widgets; add `from .sync_plan_model import …` to model.

### 4.5 Layout — `tui/styles.tcss`

```tcss
Screen {
    layout: vertical;
}

HeaderBar {
    dock: top;
    height: 1;
    background: $primary-background;
    color: $text;
    padding: 0 1;
}

FooterBar {
    dock: bottom;
    height: 1;
    background: $primary-background;
    color: $text;
    padding: 0 1;
}

#main {
    layout: horizontal;
    height: 1fr;
}

QueueTable {
    width: 2fr;
    height: 1fr;
}

QueueTable > .datatable--header {
    text-style: bold;
}

DetailPane {
    width: 1fr;
    height: 1fr;
    padding: 1 2;
    background: $surface;
}

SyncPlanPane {
    height: auto;
    min-height: 3;
    max-height: 12;
    padding: 0 1;
    background: $boost;
}

LogPane {
    height: 14;
    border-top: solid $primary;
    background: $surface;
}
```

`SyncPlanPane.height: auto` so it grows with the step list (8 steps → ~9 lines). LogPane fixed at 14 rows (~10 visible lines after RichLog padding). When the user wants more, they can scroll within the log pane (RichLog supports it).

### 4.6 `tui/app.py` — compose + action_sync

**Imports** (add):
```python
import asyncio
import os
import shlex

from tui.widgets.log_pane import LogPane
from tui.widgets.sync_plan_pane import SyncPlanPane

if TYPE_CHECKING:
    from tui.model.sync_plan_model import SyncPlanModel
```

**`__init__` additions**:
```python
def __init__(
    self,
    *,
    queue_path: Path | None = None,
    ascii_only: bool = False,
    poll_interval: float = 2.0,
    plan_path: Path | None = None,
    adk_bin: Path | None = None,
) -> None:
    super().__init__()
    self._queue_path = queue_path
    self._ascii_only = ascii_only
    self.poll_interval = poll_interval
    self._plan_path = plan_path
    self._adk_bin = adk_bin  # Path to `adk` binary; None → resolve to repo's bin/adk
    self._filter_mode: FilterMode = "all"
    self._sort_mode: SortMode = "fifo"
    self._model: QueueModel | None = None
    self._plan_model: SyncPlanModel | None = None
    self._rows_by_url: dict[str, QueueRow] = {}
    self._sync_proc: asyncio.subprocess.Process | None = None
    self._sync_task: asyncio.Task | None = None
```

**Compose** (modify):
```python
def compose(self) -> ComposeResult:
    yield HeaderBar()
    with Horizontal(id="main"):
        yield QueueTable()
        yield DetailPane()
    yield SyncPlanPane()
    yield LogPane()
    yield FooterBar()
```

**Bindings** (add):
```python
Binding("s", "sync", "sync"),
```

**`on_mount`** (extend):
```python
async def on_mount(self) -> None:
    from tui.model.queue_model import QueueModel
    from tui.model.sync_plan_model import SyncPlanModel

    self._model = QueueModel(queue_path=self._queue_path)
    self._plan_model = SyncPlanModel(plan_path=self._plan_path)
    self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=False)
    self._reload(force=True)
    self._reload_plan(force=True)
    self.set_interval(self.poll_interval, self._maybe_reload)
```

**`_reload_plan`**:
```python
def _reload_plan(self, *, force: bool = False) -> None:
    if self._plan_model is None:
        return
    if not force and not self._plan_model.has_changed():
        return
    snapshot = self._plan_model.snapshot()
    self.query_one(SyncPlanPane).update_snapshot(snapshot, ascii_only=self._ascii_only)
```

**`_maybe_reload`**:
```python
def _maybe_reload(self) -> None:
    if self._model is not None and self._model.has_changed():
        self._reload(force=True)
    self._reload_plan()
```

**`action_sync`**:
```python
def action_sync(self) -> None:
    if self._sync_proc is not None and self._sync_proc.returncode is None:
        self.query_one(LogPane).announce("(sync already running — wait or quit and restart)")
        return
    self._sync_task = asyncio.create_task(self._run_sync())

async def _run_sync(self) -> None:
    log_pane = self.query_one(LogPane)
    queue_arg: list[str] = []
    if self._queue_path is not None:
        queue_arg = ["--queue", str(self._queue_path)]
    adk = self._resolve_adk_bin()
    if adk is None:
        log_pane.announce("(error: could not locate `adk` binary)")
        return
    cmd = [str(adk), "pr-sync", *queue_arg]
    log_pane.announce(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=True)
    env = dict(os.environ)
    if self._plan_path is not None:
        env["ADK_TUI_PLAN_PATH"] = str(self._plan_path)
    try:
        self._sync_proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            env=env,
        )
    except (FileNotFoundError, PermissionError) as exc:
        log_pane.announce(f"(error: {exc})")
        self._sync_proc = None
        self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=False)
        return
    assert self._sync_proc.stdout is not None
    while True:
        line = await self._sync_proc.stdout.readline()
        if not line:
            break
        log_pane.write(line.decode(errors="replace").rstrip("\n"))
    rc = await self._sync_proc.wait()
    log_pane.announce(f"(pr-sync exited rc={rc})")
    self._sync_proc = None
    self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=False)
    self._reload_plan(force=True)
    if self._model is not None:
        # The sync rewrote the queue; force a re-read.
        self._reload(force=True)

def _resolve_adk_bin(self) -> Path | None:
    if self._adk_bin is not None:
        return self._adk_bin
    # Fall back to repo's bin/adk
    repo_root = Path(__file__).resolve().parent.parent
    candidate = repo_root / "bin" / "adk"
    if candidate.exists():
        return candidate
    # Last-resort: hope it's on PATH
    return Path("adk")
```

**Cleanup on quit**:
```python
async def on_unmount(self) -> None:
    if self._sync_proc is not None and self._sync_proc.returncode is None:
        try:
            self._sync_proc.terminate()
            try:
                await asyncio.wait_for(self._sync_proc.wait(), timeout=2.0)
            except asyncio.TimeoutError:
                self._sync_proc.kill()
        except ProcessLookupError:
            pass
```

### 4.7 `tui/widgets/footer_bar.py` — surface sync state

```python
def update_status(self, filter_mode: str, sort_mode: str, *, sync_running: bool = False) -> None:
    sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
    text = (
        f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
        f"  [j/k] nav  [q] quit  ·  {sync_label}  [r] run (disabled)"
    )
    self.update(text)
```

The legacy 2-arg signature is being extended — keep `sync_running` as a kwarg with default `False` so the existing call sites that haven't been updated keep working until B touches them all.

### 4.8 `tui/widgets/help_screen.py` — add `s` row

Add `  s              start `adk pr-sync` (streams into log pane)` before the `enter` line.

### 4.9 `bin/adk` — no change

`bin/adk` is unchanged. The TUI invokes `adk pr-sync` via subprocess, not `bin/adk` directly. (`_resolve_adk_bin()` will find `bin/adk` if installed; otherwise falls back to PATH.)

---

## 5. Visual contract

### 5.1 Layout

```
adk · queue: 12 · ready: 8 · in-review: 2/4 · platform: github+bitbucket
┌─ Queue ──────────────────────┐┌─ Details ─────────────────────────────┐
│ ✓  1234  acme/sf-bff …       ││ acme/sf-bff#1234                       │
│ ⚙  1235  acme/sf-bff …       ││ Title: …                                │
│ …                            ││ Author: …                               │
└──────────────────────────────┘└────────────────────────────────────────┘
Sync plan (running · 3/8 steps)
  ✓  pr-scan
  ✓  pr-queue update --all
  ⚡ pr-queue clean (merged)
  …  pr-task clean-orphans
  …  pr-queue remind
  …  base-index audit
  …  auto-base cleanup
  …  pr-task prepare --all
┌─ Log ─────────────────────────────────────────────────────────────────┐
│ $ /Users/.../bin/adk pr-sync                                          │
│ pr-scan: scanning channel #eng-prs since 1.0h ago                     │
│ pr-scan: found 3 new PR URLs                                          │
│ ...                                                                    │
└────────────────────────────────────────────────────────────────────────┘
[?] help  [f] filter:all  [S] sort:fifo  [j/k] nav  [q] quit  ·  [s] sync (running…)  [r] run (disabled)
```

### 5.2 Icon set

| Status | Unicode | ASCII fallback |
|---|---|---|
| pending | `…` | `[--]` |
| running | `⚡` | `[..]` |
| ok | `✓` | `[ok]` |
| warn | `⚠` | `[wn]` |
| failed | `✗` | `[fl]` |
| skipped | `↷` | `[sk]` |

---

## 6. Agent C — tests

### 6.1 `skills/adk-cli/scripts/tests/test_pr_sync_plan.py`

Unit:
- `SyncPlanWriter(queue=..., argv=[...], step_names=["a", "b"])` writes a file with `version=1`, both steps `pending`, no completed_at.
- `step_start("a")` → step `a` becomes `running`, `started_at` set.
- `step_done("a", status="ok", rc=0)` → step `a` becomes `ok`, `completed_at` set, `rc=0`.
- `finish(rc=0)` → top-level `completed_at` set, `rc=0`.
- Tolerant: `step_start("x")` for an unknown name appends a new step.
- Atomic: temp file is cleaned up after replace (no `.tmp` lingering).

Integration:
- Spawn `python3 skills/adk-cli/scripts/pr_sync.py --no-scan --no-clean-orphans --no-remind --no-prepare --no-base-audit --no-auto-demote --queue tmp.json5` in a subprocess with `ADK_TUI_PLAN_PATH=<tmp>/plan.json` env. Plan file exists, has 8 steps, 6 are `skipped`, top-level `completed_at` set, `rc` is set. (`pr-queue update --all` and `pr-queue clean (merged)` will run; they may warn on an empty queue but that's fine.)

### 6.2 `tui/tests/test_sync_plan_model.py`

- Missing plan file → `has_changed()` True initially, `snapshot()` None.
- After writing a valid plan, `snapshot()` returns SyncPlanSnapshot with the expected steps.
- Corrupt JSON → `snapshot()` returns None (no crash).
- Wrong version (`{"version": 999}`) → `snapshot()` returns None.
- `has_changed()` returns False on second call when mtime unchanged.

### 6.3 `tui/tests/test_sync_plan_pane.py`

- Pane renders "(no sync run yet)" when given None.
- Pane renders header + step lines when given a snapshot.
- ASCII mode swaps icons.
- "done" header for completed plan; "running" header otherwise.

### 6.4 `tui/tests/test_sync_action.py` (Pilot)

- Fake `adk` script: `tmp_path / "fake-adk"` is a `#!/bin/sh` echoing 3 lines then `exit 0`. Use `chmod +x`.
- Construct `AdkApp(queue_path=fake_queue_path, adk_bin=fake_adk_path, plan_path=tmp_path / "plan.json")`.
- Press `s`. Use `pilot.pause()` to allow the subprocess + the readline loop to run.
- Assert LogPane contains the 3 echoed lines + the `$ …` command line + the `(pr-sync exited rc=0)` announce line.
- Assert FooterBar text contains `[s] sync (running…)` while in flight (use a longer-lived fake script + intermediate pause).

### 6.5 `tui/tests/conftest.py` — new fixtures

```python
@pytest.fixture
def fake_plan_path(tmp_path: Path) -> Path:
    return tmp_path / "sync-plan.json"


@pytest.fixture
def sync_plan_in_progress(tmp_path: Path) -> Path:
    """A plan file with 2 ok steps + 1 running step + 5 pending."""
    p = tmp_path / "sync-plan.json"
    p.write_text(json.dumps({
        "version": 1,
        "queue": "/tmp/q.json5",
        "argv": [],
        "started_at": "2026-05-22T14:00:00Z",
        "updated_at": "2026-05-22T14:01:30Z",
        "completed_at": None,
        "rc": None,
        "steps": [
            {"name": "pr-scan", "status": "ok", "rc": 0, "started_at": "...", "completed_at": "..."},
            {"name": "pr-queue update --all", "status": "ok", "rc": 0, "started_at": "...", "completed_at": "..."},
            {"name": "pr-queue clean (merged)", "status": "running", "rc": None, "started_at": "...", "completed_at": None},
            *[{"name": n, "status": "pending", "rc": None, "started_at": None, "completed_at": None}
              for n in ["pr-task clean-orphans", "pr-queue remind", "base-index audit", "auto-base cleanup", "pr-task prepare --all"]],
        ],
    }))
    return p


@pytest.fixture
def fake_adk_script(tmp_path: Path) -> Path:
    p = tmp_path / "fake-adk"
    p.write_text("#!/bin/sh\n"
                 "echo 'pr-scan: running'\n"
                 "echo 'pr-scan: 0 new'\n"
                 "echo 'done'\n"
                 "exit 0\n")
    p.chmod(0o755)
    return p
```

---

## 7. Definition of done

Per-agent acceptance:

- **A**: `python3 skills/adk-cli/scripts/pr_sync.py --no-scan --no-clean-orphans --no-remind --no-prepare --no-base-audit --no-auto-demote --queue <empty>` with `ADK_TUI_PLAN_PATH=<tmp>` emits a `version: 1` plan with 8 steps; all pre-existing pr_sync behavior unchanged; `python3 -m pytest skills/adk-cli/scripts/tests/test_pr_sync_plan.py` green.
- **B**: `adk` launches; `s` spawns `adk pr-sync` and streams its stdout into the log pane; the sync-plan pane updates as the plan file changes; quitting the TUI kills the child; existing α+β tests still pass.
- **C**: `python3 -m pytest tui/tests/ skills/adk-cli/scripts/tests/` green; ≥7 net-new tests (3 plan-writer, 3 plan-model, 1 plan-pane render, ≥1 sync action).

Whole-slice:
- Repo-wide test count goes up by ≥10. No regressions on the 430 baseline.
- `bin/adk` is unchanged.
- Manual smoke: launch `adk`, press `s`, see real lines stream in.
- No new top-level dependencies (still just `textual>=0.86`).

---

## 8. Spec deviations — explicit policy

If an interface in this spec doesn't survive contact with Textual 8.x (e.g., a `RichLog` kwarg doesn't exist, or `on_unmount` is async-incompatible), the implementing agent SHOULD adapt locally and surface the deviation in its completion message. Two known α+β deviations (renaming `update` → `update_snapshot` and `?` → `question_mark`) set the precedent: small, named deviations are OK; silent contract changes are not.
