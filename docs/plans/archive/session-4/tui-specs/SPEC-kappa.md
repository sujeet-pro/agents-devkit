# TUI sub-phase κ — binding interface SPEC

Status: **frozen**, parallel build.

κ adds an agent registry — a small structure that knows about `claude`, `codex`, `cursor-agent`, `opencode`, and a `headless` no-op — and exposes it as an `a` picker modal in the TUI. After κ, the user can pick a different agent for the next review without restarting the TUI; the worker is invoked with `--agent <name>` instead of (or in addition to) `--agent-bin <path>`.

The "headless fallback" is a registry entry whose binary is a stub script that just echoes a one-line confirmation and exits 0. Useful for testing the worker flow without burning agent tokens.

All α–ε behavior keeps working. Existing 534 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/agent_registry.py` (NEW), `tui/worker.py` (MODIFIED — accept `--agent <name>`), `tui/app.py` (MODIFIED — `_current_agent` state, `a` binding, AgentPickerScreen launcher, footer kwarg), `tui/screens/__init__.py` (MODIFIED — re-export), `tui/screens/agent_picker_screen.py` (NEW), `tui/widgets/footer_bar.py` (MODIFIED — `agent` kwarg), `tui/widgets/help_screen.py` (MODIFIED — `a` line) | all α–ε files |
| **B** | `adk-agent-test-engineer` | `tui/tests/test_agent_registry.py` (NEW), `tui/tests/test_agent_picker_screen.py` (NEW), `tui/tests/test_worker_agent_flag.py` (NEW), `tui/tests/conftest.py` (MODIFIED if needed) | everything |

---

## 2. Agent registry

### 2.1 `tui/agent_registry.py` (NEW)

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSpec:
    """One row in the agent registry. Knows how to invoke a slash command
    against this agent's binary."""
    name: str            # registry key, lower-case (e.g. "claude")
    bin: str             # binary name on PATH (e.g. "claude") or absolute path
    description: str     # one-line human label for the picker


# The default registry. Ordered as it appears in the picker.
DEFAULT_AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        name="claude",
        bin="claude",
        description="Anthropic Claude (recommended for /adk-pr-review)",
    ),
    AgentSpec(
        name="codex",
        bin="codex",
        description="OpenAI Codex CLI",
    ),
    AgentSpec(
        name="cursor",
        bin="cursor-agent",
        description="Cursor agent CLI",
    ),
    AgentSpec(
        name="opencode",
        bin="opencode",
        description="OpenCode CLI",
    ),
    AgentSpec(
        name="headless",
        bin="__headless__",
        description="No-op stub (for testing the worker without an agent)",
    ),
)


def list_agents() -> tuple[AgentSpec, ...]:
    return DEFAULT_AGENTS


def get_agent(name: str) -> AgentSpec | None:
    """Look up an agent by name (case-insensitive). Returns None if not found."""
    needle = (name or "").strip().lower()
    if not needle:
        return None
    for spec in DEFAULT_AGENTS:
        if spec.name == needle:
            return spec
    return None


def default_agent() -> AgentSpec:
    """The agent used when no `--agent` is passed. Always `claude` today."""
    return DEFAULT_AGENTS[0]
```

### 2.2 Invocation contract

Every agent in the registry is invoked the same way: `<bin> -p "/adk-pr-review <pr_url>"`. (The two-arg form `-p <slash>` matches Claude's CLI; we assume the others honor the same convention OR will be patched in their respective sections of the registry later.)

If a future agent needs a different shape (e.g., `codex run "/slash <args>"`), extend `AgentSpec` with `argv_template: tuple[str, ...] | None` and have `worker.py` interpolate. For κ MVP, stick with `-p <slash>`.

### 2.3 The `headless` agent

`bin="__headless__"` is a sentinel — the worker treats it specially. Instead of spawning a subprocess, the worker writes a single line `[headless] no agent spawned for <pr_url>` to its own stdout, sleeps 0.5 s (so the heartbeat file has time to update), and exits the agent-run section with `agent_rc=0`. This avoids needing a real binary on PATH for the headless case.

---

## 3. Worker integration

### 3.1 New `--agent` flag

`tui/worker.py` adds `--agent <name>` (registry lookup). Existing `--agent-bin <path>` continues to work as a raw override (takes precedence over `--agent` if both are passed).

```python
ap.add_argument("--agent", default=None,
                help="agent name in the registry (e.g. 'claude'); "
                     "ignored if --agent-bin is also set")
```

### 3.2 Resolution

In `_drive`, after argparse:

```python
from tui.agent_registry import default_agent, get_agent

if args.agent_bin:
    agent_bin = str(args.agent_bin)
    agent_name = "custom"  # for the heartbeat payload
elif args.agent:
    spec = get_agent(args.agent)
    if spec is None:
        _emit(f"(error: unknown agent {args.agent!r}; available: "
              f"{', '.join(s.name for s in list_agents())})")
        return 2
    agent_bin = spec.bin
    agent_name = spec.name
else:
    spec = default_agent()
    agent_bin = spec.bin
    agent_name = spec.name
```

Update the heartbeat payload to use the resolved `agent_name`:

```python
payload = {
    ...,
    "agent": agent_name,  # was hardcoded "claude"
    ...,
}
```

### 3.3 Headless shortcut

If `agent_bin == "__headless__"`, skip the `asyncio.create_subprocess_exec` call entirely:

```python
if agent_bin == "__headless__":
    _emit(f"[headless] no agent spawned for {args.pr_url}")
    await asyncio.sleep(0.5)
    agent_rc = 0
else:
    try:
        agent_proc = await asyncio.create_subprocess_exec(*agent_cmd, ...)
        await _stream_proc(agent_proc, payload)
        agent_rc = await agent_proc.wait()
    except FileNotFoundError as exc:
        ...
```

Cleanup (heartbeat unlink, release) runs as normal in the finally block.

---

## 4. AdkApp integration

### 4.1 New state

```python
self._current_agent: str = "claude"  # registry name; default is claude
```

(Default could come from a constructor kwarg `agent: str = "claude"` if we want tests to override.)

### 4.2 New binding

```python
Binding("a", "pick_agent", "agent"),
```

### 4.3 `action_pick_agent`

```python
@work
async def action_pick_agent(self) -> None:
    from tui.screens.agent_picker_screen import AgentPickerScreen
    if any(isinstance(s, AgentPickerScreen) for s in self.screen_stack):
        return
    picked = await self.push_screen_wait(AgentPickerScreen(current=self._current_agent))
    if not picked:
        return
    self._current_agent = picked
    # Refresh footer immediately so the user sees the new agent.
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
        review_running=bool(self._review_workers),
        selected_count=len(self._selection_order),
        parallel_n=self._parallel_n,
        agent=self._current_agent,
    )
```

### 4.4 `_run_review` passes the current agent

Replace the `--agent-bin` arg construction with `--agent <self._current_agent>`. Keep the existing `_agent_bin` kwarg for test injection (which still takes precedence — tests pass a fake script as `--agent-bin`).

```python
cmd = [sys.executable, str(worker), pr_url]
if self._queue_path is not None:
    cmd += ["--queue", str(self._queue_path)]
if self._adk_bin is not None:
    cmd += ["--adk-bin", str(self._adk_bin)]
if self._agent_bin is not None:
    cmd += ["--agent-bin", str(self._agent_bin)]
else:
    cmd += ["--agent", self._current_agent]
if self._heartbeat_dir is not None:
    cmd += ["--heartbeat-dir", str(self._heartbeat_dir)]
```

### 4.5 Other `update_status` call sites

All ~12 call sites must add `agent=self._current_agent` as a kwarg. Safe default in the footer (omit when None) keeps any missed callsite from crashing.

---

## 5. `tui/screens/agent_picker_screen.py`

### 5.1 Shape

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static, OptionList
from textual.widgets.option_list import Option

from tui.agent_registry import list_agents


class AgentPickerScreen(ModalScreen[str | None]):
    """Modal picker for the agent registry. Dismiss with the picked name
    on enter; dismiss with None on escape."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    DEFAULT_CSS = """
    AgentPickerScreen {
        align: center middle;
    }
    AgentPickerScreen > Container {
        width: 64;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    AgentPickerScreen Static {
        width: 100%;
        padding-bottom: 1;
    }
    AgentPickerScreen OptionList {
        width: 100%;
        height: auto;
    }
    """

    def __init__(self, *, current: str = "claude") -> None:
        super().__init__()
        self._current = current

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(
                f"Pick agent (current: {self._current})",
                markup=False,
            )
            opts = [
                Option(f"{spec.name:10s}  {spec.description}", id=spec.name)
                for spec in list_agents()
            ]
            yield OptionList(*opts)

    def on_mount(self) -> None:
        # Highlight the current agent in the OptionList.
        opt_list = self.query_one(OptionList)
        for i, spec in enumerate(list_agents()):
            if spec.name == self._current:
                opt_list.highlighted = i
                break

    def on_option_list_option_selected(self, event) -> None:
        self.dismiss(event.option.id)

    def action_cancel(self) -> None:
        self.dismiss(None)
```

### 5.2 `tui/screens/__init__.py`

Add `from .agent_picker_screen import AgentPickerScreen` and append to `__all__`.

---

## 6. FooterBar update

### 6.1 New signature

```python
def update_status(
    self,
    filter_mode: str,
    sort_mode: str,
    *,
    sync_running: bool = False,
    review_running: bool = False,
    selected_count: int = 0,
    parallel_n: int = 4,
    agent: str | None = None,
) -> None:
    sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
    review_label = "[r] review (running…)" if review_running else "[r] review"
    sel_label = f"sel:{selected_count}"
    par_label = f"par:{parallel_n}"
    agent_label = f"agent:{agent}" if agent else ""
    extras = f"  ·  {sel_label}  {par_label}"
    if agent_label:
        extras += f"  {agent_label}"
    text = (
        f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
        f"  [j/k] nav  [q] quit"
        f"  ·  {sync_label}  {review_label}  [R] run-sel  [space] sel  [p] par  [a] agent"
        f"{extras}"
    )
    self.update(text)
```

`agent=None` (the default) omits the chip — keeps backward compat for any caller that hasn't been updated.

---

## 7. HelpScreen update

Add a line for `a`:

```
  a              pick agent (claude / codex / cursor / headless ...)
```

Position: right after the `p` line.

---

## 8. Tests (Agent B)

### 8.1 `tui/tests/test_agent_registry.py`

- `list_agents()` returns ≥ 5 specs (claude, codex, cursor, opencode, headless).
- `get_agent("claude")` returns the spec.
- `get_agent("CLAUDE")` is case-insensitive.
- `get_agent("ghost")` returns None.
- `get_agent("")` and `get_agent(None)` return None.
- `default_agent().name == "claude"`.
- Every spec's `bin` is a non-empty string.
- The `headless` spec has `bin == "__headless__"`.

### 8.2 `tui/tests/test_agent_picker_screen.py`

Pilot tests:
- Push AgentPickerScreen, assert modal appears, current is highlighted.
- Press escape → dismiss(None).
- Press down then enter → dismiss with the second agent's name ("codex").
- Tests construct AgentPickerScreen via a parent AdkApp + push, not directly (Textual modals need a host App).

### 8.3 `tui/tests/test_worker_agent_flag.py`

- `python3 tui/worker.py <url> --agent claude --agent-bin <fake>` (both passed): uses --agent-bin (raw override wins). Heartbeat payload `agent` field is "custom".
- `python3 tui/worker.py <url> --agent claude`: uses `claude` from PATH. (Real claude binary not invoked — use `subprocess.run(..., env=PATH-override-to-empty, timeout=2)` and assert FileNotFoundError-ish exit code OR have claude on PATH be a fake. Simpler: pass `--agent-bin /tmp/fake-claude` and check the agent_name override behavior via heartbeat file.)
- `python3 tui/worker.py <url> --agent headless` (no `--agent-bin`): worker emits `[headless] no agent spawned ...` line; exit code 0; release called; heartbeat `agent` field is "headless".
- `python3 tui/worker.py <url> --agent ghost`: exit code 2; stdout shows `(error: unknown agent 'ghost'; available: ...)`.
- `python3 tui/worker.py <url>` (no --agent, no --agent-bin): uses default agent (claude). Real claude binary required — skip this test or use a tmpdir on PATH with a fake claude.

### 8.4 Optional pilot test in `test_review_action.py`

If trivial, add a test that:
- Construct AdkApp, press `a`, modal appears, pick "headless", modal dismisses.
- Press `r` on eligible row, worker spawns with `--agent headless`, exits cleanly.
- Footer shows `agent:headless`.

---

## 9. Definition of done

- `tui/agent_registry.py` exposes the 5 default agents + helper functions.
- `tui/worker.py` honors `--agent <name>` (registry lookup) + `--agent-bin <path>` (raw override).
- Headless agent works end-to-end (no real binary needed; worker emits a stub line and exits 0).
- `a` opens AgentPickerScreen; submitted name persists in `AdkApp._current_agent`; footer reflects the pick.
- All ~12 `update_status` call sites updated with the new `agent=` kwarg.
- 534 baseline tests stay green.
- ≥ 10 net-new tests.

---

## 10. Spec deviations — explicit policy

Same as γ–ε. Small named deviations OK; surface in completion message.
