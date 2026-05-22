# TUI sub-phase η — binding interface SPEC

Status: **frozen**, parallel build.

η adds two adjacent UX pieces:

1. **Add-PR modal** (`+` on the main screen) — a single-input modal that accepts a PR URL, `owner/repo#N` shorthand, or bare PR number, then spawns `adk pr-queue add <input>` and streams its output into the LogPane.
2. **Repo management screen** (`b` on the main screen) — a separate Screen showing every repo under `~/.agents-devkit/repos/` and each repo's tracked branches with origin (user/auto), last-indexed age, etc. Actions: `+` add repo (spawns `adk repo add <url>`); `a` add branch (spawns `adk repo branch add <name> --branch X`); `R` rebuild (spawns `adk repo rebuild-index <name> [--branch X]`); `d` delete auto-base (spawns `adk repo auto-bases clean --force <name> --branch X` after confirm); `escape` returns to the main screen.

All α–ζ behavior keeps working. The existing 497 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/app.py` (MODIFIED — `+` and `b` bindings, `action_add_pr` / `action_repos`), `tui/widgets/help_screen.py` (MODIFIED — new bindings text), `tui/screens/__init__.py` (NEW), `tui/screens/prompt_screen.py` (NEW), `tui/screens/repo_screen.py` (NEW) | all α–ζ files |
| **B** | `adk-agent-implementer` | `tui/model/repo_model.py` (NEW), `tui/model/__init__.py` (MODIFIED) | all α–ζ files |
| **C** | `adk-agent-test-engineer` | `tui/tests/test_repo_model.py` (NEW), `tui/tests/test_prompt_screen.py` (NEW), `tui/tests/test_repo_screen.py` (NEW), `tui/tests/test_add_pr_action.py` (NEW), `tui/tests/conftest.py` (MODIFIED — add `fake_repos_dir` fixture) | everything |

**Hard rule**: A does not touch `tui/model/*` or tests. B does not touch `tui/app.py`, screens, widgets, or tests. C does not write production code.

---

## 2. The PromptScreen modal (generic)

### 2.1 `tui/screens/prompt_screen.py`

A reusable single-input modal. Used by Add-PR (from main screen), Add-Repo (from RepoScreen), and Add-Branch (from RepoScreen).

```python
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Input, Static


class PromptScreen(ModalScreen[str | None]):
    """Single-input modal. dismiss() with the typed value on submit,
    dismiss(None) on cancel (escape)."""

    BINDINGS = [Binding("escape", "cancel", show=False)]

    DEFAULT_CSS = """
    PromptScreen {
        align: center middle;
    }
    PromptScreen > Container {
        width: 60;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    PromptScreen Static {
        width: 100%;
    }
    PromptScreen Input {
        width: 100%;
    }
    """

    def __init__(self, label: str, placeholder: str = "") -> None:
        super().__init__()
        self._label = label
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(self._label, markup=False)
            yield Input(placeholder=self._placeholder)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss(None)
```

The dismiss-value contract: a string (the submitted value) on submit; `None` on cancel.

### 2.2 Empty input handling

If the user hits Enter with an empty input, `event.value` is `""`. Callers must treat empty as cancel (don't spawn a subprocess on empty input):

```python
value = await self.push_screen_wait(PromptScreen("Add PR", "URL, owner/repo#N, or number"))
if not value:
    return
```

---

## 3. Agent A — `tui/app.py` changes

### 3.1 New bindings

```python
Binding("plus", "add_pr", "add-pr"),
Binding("b", "repos", "repos"),
```

The `+` key's canonical Textual name is `"plus"`. Verify by spawning a Pilot test that presses `"plus"` and asserts the modal opens.

### 3.2 `action_add_pr`

```python
async def action_add_pr(self) -> None:
    from tui.screens.prompt_screen import PromptScreen
    value = await self.push_screen_wait(
        PromptScreen("Add PR", "URL, owner/repo#N, or PR number")
    )
    if not value:
        return
    busy = self._busy_label()
    if busy is not None:
        self.query_one(LogPane).write(f"(can't add PR — {busy} already running)")
        return
    self._add_pr_task = asyncio.create_task(self._run_add_pr(value.strip()))
```

### 3.3 `_run_add_pr(text)`

Subprocess driver — mirror `_run_sync`'s shape but for the `pr-queue add` verb. Streams output into the LogPane. Reuses the existing `_resolve_adk_bin`.

```python
async def _run_add_pr(self, text: str) -> None:
    log_pane = self.query_one(LogPane)
    adk = self._resolve_adk_bin()
    cmd: list[str] = [str(adk), "pr-queue", "add", text, "-y"]
    if self._queue_path is not None:
        cmd += ["--queue", str(self._queue_path)]
    log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except (FileNotFoundError, PermissionError, OSError) as exc:
        log_pane.write(f"(error: {exc})")
        return
    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        log_pane.write(line.decode(errors="replace").rstrip("\n"))
    rc = await proc.wait()
    log_pane.write(f"(pr-queue add exited rc={rc})")
    if self._model is not None:
        self._reload(force=True)
```

### 3.4 `action_repos`

```python
def action_repos(self) -> None:
    from tui.screens.repo_screen import RepoScreen
    self.push_screen(RepoScreen(
        repos_dir=self._repos_dir,
        adk_bin_resolver=self._resolve_adk_bin,
    ))
```

Add `self._repos_dir: Path | None` to `__init__` kwargs (`None` → defaults to `~/.agents-devkit/repos/`). Tests can override.

### 3.5 `_busy_label()` extension

Add `_add_pr_task` and `_repo_action_task` slots so we don't accidentally allow two add-PR calls at once:

```python
def _busy_label(self) -> str | None:
    if self._sync_proc is not None and self._sync_proc.returncode is None:
        return "sync"
    if self._batch_task is not None and not self._batch_task.done():
        return "batch"
    if self._add_pr_task is not None and not self._add_pr_task.done():
        return "add-pr"
    if self._review_workers:
        return "review"
    return None
```

Initialize `self._add_pr_task: asyncio.Task | None = None` in `__init__`.

---

## 4. Agent A — `tui/screens/repo_screen.py` (NEW)

A full Screen (not modal) that takes over the viewport. Pressing `escape` pops back to the main AdkApp screen.

### 4.1 Shape

```python
from __future__ import annotations

import asyncio
import shlex
from pathlib import Path
from typing import Callable

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static, Tree

from tui.model.repo_model import RepoModel, RepoRow, RepoBranchRow
from tui.screens.prompt_screen import PromptScreen


class RepoScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "back"),
        Binding("plus", "add_repo", "add-repo"),
        Binding("a", "add_branch", "add-branch"),
        Binding("R", "rebuild", "rebuild"),
        Binding("d", "delete_auto_base", "delete-auto-base"),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
    ]

    DEFAULT_CSS = """
    RepoScreen { layout: vertical; }
    RepoScreen Static#repo_header {
        height: 1;
        background: $primary-background;
        color: $text;
        padding: 0 1;
    }
    RepoScreen Tree {
        height: 1fr;
    }
    RepoScreen Static#repo_footer {
        dock: bottom;
        height: 1;
        background: $primary-background;
        color: $text;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        *,
        repos_dir: Path | None = None,
        adk_bin_resolver: Callable[[], Path] | None = None,
        poll_interval: float = 5.0,
    ) -> None:
        super().__init__()
        self._model = RepoModel(repos_dir=repos_dir)
        self._adk_bin_resolver = adk_bin_resolver or (lambda: Path("adk"))
        self._poll_interval = poll_interval
        self._action_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield Static("Repos · [escape] back  [+] add  [a] add-branch  [R] rebuild  [d] delete-auto-base",
                     id="repo_header", markup=False)
        yield Tree("Repos", id="repo_tree")
        yield Static("", id="repo_footer", markup=False)

    def on_mount(self) -> None:
        self._refresh()
        self.set_interval(self._poll_interval, self._refresh)

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_cursor_down(self) -> None:
        self.query_one(Tree).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(Tree).action_cursor_up()

    def _refresh(self) -> None:
        rows = self._model.snapshot()
        tree = self.query_one(Tree)
        tree.clear()
        for repo in rows:
            node = tree.root.add(_format_repo_label(repo), expand=True)
            for br in repo.branches:
                node.add(_format_branch_label(br), data=("branch", repo.name, br.branch))
            node.data = ("repo", repo.name, None)
        self.query_one("#repo_footer", Static).update(
            f"{len(rows)} repos · {sum(len(r.branches) for r in rows)} branches"
        )

    # --- actions ---
    async def action_add_repo(self) -> None:
        url = await self.app.push_screen_wait(
            PromptScreen("Add repo", "git URL (git@... or https://...)")
        )
        if not url:
            return
        await self._spawn_subprocess(
            [str(self._adk_bin_resolver()), "repo", "add", url.strip(), "-y"],
            label="repo-add",
        )

    async def action_add_branch(self) -> None:
        # Use the highlighted repo (if a branch row is highlighted, use its parent).
        repo_name = self._cursor_repo_name()
        if not repo_name:
            self._log_screen("(no repo highlighted)")
            return
        branch = await self.app.push_screen_wait(
            PromptScreen(f"Add branch to {repo_name}", "branch name (e.g., release/v2.1)")
        )
        if not branch:
            return
        await self._spawn_subprocess(
            [str(self._adk_bin_resolver()), "repo", "branch", "add",
             repo_name, "--branch", branch.strip(), "-y"],
            label="branch-add",
        )

    async def action_rebuild(self) -> None:
        ctx = self._cursor_context()
        if ctx is None:
            self._log_screen("(no row highlighted)")
            return
        kind, repo_name, branch = ctx
        cmd = [str(self._adk_bin_resolver()), "repo", "rebuild-index", repo_name]
        if kind == "branch" and branch:
            cmd += ["--branch", branch]
        cmd += ["-y"]
        await self._spawn_subprocess(cmd, label="rebuild-index")

    async def action_delete_auto_base(self) -> None:
        ctx = self._cursor_context()
        if ctx is None or ctx[0] != "branch":
            self._log_screen("(highlight an auto-base branch to delete)")
            return
        _, repo_name, branch = ctx
        await self._spawn_subprocess(
            [str(self._adk_bin_resolver()), "repo", "auto-bases", "clean",
             "--force", repo_name, "--branch", branch, "-y"],
            label="auto-base-clean",
        )

    # --- helpers ---
    def _cursor_context(self) -> tuple[str, str, str | None] | None:
        tree = self.query_one(Tree)
        node = tree.cursor_node
        if node is None or node.data is None:
            return None
        return node.data  # type: ignore[return-value]

    def _cursor_repo_name(self) -> str | None:
        ctx = self._cursor_context()
        if ctx is None:
            return None
        return ctx[1]

    def _log_screen(self, msg: str) -> None:
        self.query_one("#repo_footer", Static).update(msg)

    async def _spawn_subprocess(self, cmd: list[str], *, label: str) -> None:
        self._log_screen(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self._log_screen(f"(error: {exc})")
            return
        # Drain output line-by-line to the footer; the user sees the last line.
        # For richer logging, we could route to the main screen's LogPane, but
        # that requires app-level coordination; footer is good enough for now.
        assert proc.stdout is not None
        last_line = ""
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            last_line = line.decode(errors="replace").rstrip("\n")
            self._log_screen(last_line[:200])
        rc = await proc.wait()
        self._log_screen(f"{label}: rc={rc}  ·  {last_line[:150]}")
        self._refresh()


def _format_repo_label(repo: RepoRow) -> str:
    return f"{repo.name}  ({repo.url})"


def _format_branch_label(br: RepoBranchRow) -> str:
    origin = "user" if br.created_by == "user" else "auto"
    age = _format_age_s(br.age_s)
    indexed = br.last_indexed_at or "—"
    return f"{br.branch}  ·  {origin}  ·  indexed {indexed}  ·  used {age}"


def _format_age_s(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    if seconds < 60:
        return f"{int(seconds)}s ago"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m ago"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours}h ago"
    return f"{int(hours // 24)}d ago"
```

### 4.2 Cursor data convention

Each Tree node has `data` set to `(kind, repo_name, branch_or_None)` where `kind ∈ {"repo", "branch"}`. The `_cursor_context()` helper returns that tuple or `None` if the cursor is on the implicit root.

### 4.3 Subprocess output routing

For η simplicity, the RepoScreen's subprocess output is routed to its OWN footer line (last-line view), not the main LogPane. This avoids coupling the modal screen to the main app's LogPane. If the user wants full output, they can return to the main screen and re-run via the CLI.

A `_refresh()` call at the end of `_spawn_subprocess` ensures the tree updates after add/remove/rebuild.

---

## 5. Agent A — `tui/screens/__init__.py` and `tui/widgets/help_screen.py`

### 5.1 `tui/screens/__init__.py`

```python
from .prompt_screen import PromptScreen
from .repo_screen import RepoScreen

__all__ = ["PromptScreen", "RepoScreen"]
```

### 5.2 Help text

Add these lines under the existing `p` line (in the order shown):

```
  +              add PR (modal — URL, owner/repo#N, or number)
  b              switch to repos screen (manage repos + branches)
```

---

## 6. Agent B — `tui/model/repo_model.py`

### 6.1 Shape

```python
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class RepoBranchRow:
    repo_name: str
    branch: str
    slug: str
    created_by: str  # "user" | "auto"
    last_indexed_at: str | None
    last_used_at: str | None
    age_s: float | None  # seconds since last_used_at, or None if not set
    auto_reason: str | None


@dataclass(frozen=True)
class RepoRow:
    name: str
    url: str
    default_branch: str
    branches: tuple[RepoBranchRow, ...]


def default_repos_dir() -> Path:
    return Path.home() / ".agents-devkit" / "repos"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


class RepoModel:
    """Reads ~/.agents-devkit/repos/ and exposes repos + branches as
    frozen dataclasses. Mtime-gated via a directory-fingerprint signature."""

    def __init__(
        self,
        repos_dir: Path | None = None,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.repos_dir = repos_dir if repos_dir is not None else default_repos_dir()
        if now_fn is None:
            now_fn = lambda: datetime.now(tz=timezone.utc)  # noqa: E731
        self._now_fn = now_fn
        self._last_signature: tuple | None = None

    def _signature(self) -> tuple:
        if not self.repos_dir.exists():
            return ()
        items: list[tuple[str, float]] = []
        try:
            for p in self.repos_dir.iterdir():
                if not p.is_dir():
                    continue
                meta = p / "repo-meta.json"
                try:
                    items.append((p.name, meta.stat().st_mtime if meta.exists() else 0.0))
                except OSError:
                    items.append((p.name, 0.0))
                # also sample each branch-meta.json mtime for change detection
                for child in p.iterdir():
                    if child.is_dir() and child.name.startswith("branch-"):
                        bm = child / "branch-meta.json"
                        try:
                            items.append((f"{p.name}/{child.name}",
                                          bm.stat().st_mtime if bm.exists() else 0.0))
                        except OSError:
                            items.append((f"{p.name}/{child.name}", 0.0))
        except OSError:
            return ()
        items.sort()
        return tuple(items)

    def has_changed(self) -> bool:
        cur = self._signature()
        if cur != self._last_signature:
            return True
        return False

    def snapshot(self) -> list[RepoRow]:
        self._last_signature = self._signature()
        if not self.repos_dir.exists():
            return []
        now = self._now_fn()
        rows: list[RepoRow] = []
        for p in sorted(self.repos_dir.iterdir()):
            if not p.is_dir():
                continue
            meta_path = p / "repo-meta.json"
            if not meta_path.exists():
                continue
            try:
                raw = json.loads(meta_path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            branches = self._collect_branches(p, raw.get("name") or p.name, now)
            rows.append(RepoRow(
                name=str(raw.get("name") or p.name),
                url=str(raw.get("url") or raw.get("input_url") or ""),
                default_branch=str(raw.get("default_branch") or ""),
                branches=tuple(branches),
            ))
        return rows

    def _collect_branches(self, repo_dir: Path, repo_name: str,
                          now: datetime) -> list[RepoBranchRow]:
        out: list[RepoBranchRow] = []
        for child in sorted(repo_dir.iterdir()):
            if not (child.is_dir() and child.name.startswith("branch-")):
                continue
            bm = child / "branch-meta.json"
            if not bm.exists():
                continue
            try:
                raw = json.loads(bm.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            last_used = _parse_iso(raw.get("last_used_at"))
            age_s = (now - last_used).total_seconds() if last_used is not None else None
            out.append(RepoBranchRow(
                repo_name=repo_name,
                branch=str(raw.get("branch") or ""),
                slug=str(raw.get("slug") or child.name.removeprefix("branch-")),
                created_by=str(raw.get("created_by") or "user"),
                last_indexed_at=raw.get("last_indexed_at"),
                last_used_at=raw.get("last_used_at"),
                age_s=age_s,
                auto_reason=raw.get("auto_reason"),
            ))
        return out
```

### 6.2 `tui/model/__init__.py`

Re-export `RepoModel`, `RepoRow`, `RepoBranchRow`.

### 6.3 Constraints

- ≤ 180 LOC.
- Pure stdlib; no third-party deps.
- Robust to: missing dir, corrupt JSON, non-dict JSON, missing fields, OSError on stat/iterdir.

---

## 7. Agent C — tests

### 7.1 `tui/tests/test_repo_model.py`

Use a tmp_path-backed `~/.agents-devkit/repos`-like layout:
- Test empty `repos_dir` → snapshot is `[]`.
- Test one repo with one user branch → snapshot returns RepoRow with one RepoBranchRow whose `created_by="user"`.
- Test one repo with one user + one auto branch → both shown.
- Test missing `repo-meta.json` in a sub-dir → skipped silently.
- Test corrupt `repo-meta.json` → skipped silently.
- Test non-dict JSON → skipped silently.
- Test `has_changed()` returns True initially, False on second call, True after mutating a branch-meta.json.
- Test `last_used_at` → `age_s` calculation with injected `now_fn`.

### 7.2 `tui/tests/test_prompt_screen.py`

- Pilot: push a `PromptScreen("test", "...")`, type `"hello"`, press enter → dismiss value is `"hello"`.
- Pilot: push a screen, press escape → dismiss value is `None`.
- Pilot: push, enter empty → dismiss value is `""` (caller treats as cancel).

### 7.3 `tui/tests/test_add_pr_action.py`

Pilot tests for the `+` binding on the main screen:
- Press `+` → modal appears (assert `len(app.screen_stack) == 2`).
- Press `+`, type `"https://github.com/foo/bar/pull/42"`, enter → modal dismisses, LogPane shows `$ ...adk pr-queue add ... -y` (use `fake_adk_script` to make the subprocess succeed).
- Press `+`, press escape → modal dismisses, no subprocess line in LogPane.
- Press `+`, type "", enter → modal dismisses, no subprocess.

### 7.4 `tui/tests/test_repo_screen.py`

Pilot tests for `b` binding:
- Press `b` → RepoScreen appears (assert `isinstance(app.screen, RepoScreen)`).
- After mount, RepoScreen tree shows the test fixture's repos + branches.
- Press `escape` → returns to main screen.
- Press `+` on RepoScreen → PromptScreen appears asking for URL.
- Press `a` with cursor on a repo → PromptScreen appears asking for branch name.

### 7.5 `tui/tests/conftest.py`

Add `fake_repos_dir` fixture:
```python
@pytest.fixture
def fake_repos_dir(tmp_path: Path) -> Path:
    import json
    root = tmp_path / "repos"
    repo = root / "fake-repo"
    repo.mkdir(parents=True)
    (repo / "repo-meta.json").write_text(json.dumps({
        "name": "fake-repo", "url": "git@github.com:acme/fake.git",
        "default_branch": "main",
    }))
    branch = repo / "branch-main"
    branch.mkdir()
    (branch / "branch-meta.json").write_text(json.dumps({
        "branch": "main", "slug": "main", "created_by": "user",
        "last_indexed_at": "2026-05-22T10:00:00Z",
        "last_used_at": "2026-05-22T13:00:00Z",
    }))
    auto_branch = repo / "branch-feat-x"
    auto_branch.mkdir()
    (auto_branch / "branch-meta.json").write_text(json.dumps({
        "branch": "feat/x", "slug": "feat-x", "created_by": "auto",
        "last_indexed_at": "2026-05-22T13:30:00Z",
        "last_used_at": "2026-05-22T13:30:00Z",
        "auto_reason": "3 PRs target feat/x",
    }))
    return root
```

---

## 8. Definition of done

- `+` opens PromptScreen modal; submit spawns `adk pr-queue add` subprocess streaming into LogPane.
- `b` switches to RepoScreen showing all repos + branches (origin tagged).
- RepoScreen actions (`+`, `a`, `R`, `d`) spawn the right subprocess and refresh the tree.
- `escape` from RepoScreen returns to main; escape from PromptScreen cancels.
- 497 baseline tests stay green.
- ≥ 10 net-new tests.

---

## 9. Spec deviations — explicit policy

Same as γ–ζ. Small, named deviations OK; surface in completion message.
