from __future__ import annotations

import asyncio
import shlex
from pathlib import Path
from typing import Callable

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static, Tree

from tui.model.repo_model import RepoBranchRow, RepoModel, RepoRow
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
        yield Static(
            "Repos · [escape] back  [+] add  [a] add-branch  [R] rebuild  [d] delete-auto-base",
            id="repo_header",
            markup=False,
        )
        yield Tree("Repos", id="repo_tree")
        yield Static("", id="repo_footer", markup=False)

    def on_mount(self) -> None:
        self._refresh(force=True)
        self.set_interval(self._poll_interval, self._refresh)

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_cursor_down(self) -> None:
        self.query_one(Tree).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one(Tree).action_cursor_up()

    def _refresh(self, *, force: bool = False) -> None:
        # Gate on the model's signature so the periodic tick doesn't rebuild
        # the tree (and wipe the cursor) when nothing on disk changed.
        if not force and not self._model.has_changed():
            return
        rows = self._model.snapshot()
        tree = self.query_one(Tree)
        # Preserve cursor + expand state across the rebuild.
        prior_ctx = self._cursor_context()
        expanded_names = {
            node.label.plain.split("  ")[0] if hasattr(node.label, "plain") else str(node.label).split("  ")[0]
            for node in tree.root.children if node.is_expanded
        }
        tree.clear()
        nodes_by_repo: dict[str, object] = {}
        for repo in rows:
            node = tree.root.add(
                _format_repo_label(repo),
                expand=(repo.name in expanded_names) if expanded_names else True,
            )
            for br in repo.branches:
                node.add(_format_branch_label(br), data=("branch", repo.name, br.branch))
            node.data = ("repo", repo.name, None)
            nodes_by_repo[repo.name] = node
        # Best-effort re-seat the cursor on the same row (by data tuple).
        if prior_ctx is not None:
            target_kind, target_repo, target_branch = prior_ctx
            for line_no in range(tree.last_line + 1):
                node = tree.get_node_at_line(line_no)
                if node is not None and node.data == prior_ctx:
                    tree.cursor_line = line_no
                    break
        self.query_one("#repo_footer", Static).update(
            f"{len(rows)} repos · {sum(len(r.branches) for r in rows)} branches"
        )

    # --- actions ---
    # @work is required because push_screen_wait only resolves inside a
    # Textual worker context; bare async action methods raise NoActiveWorker.
    @work
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

    @work
    async def action_add_branch(self) -> None:
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
            [
                str(self._adk_bin_resolver()),
                "repo",
                "branch",
                "add",
                repo_name,
                "--branch",
                branch.strip(),
                "-y",
            ],
            label="branch-add",
        )

    def action_rebuild(self) -> None:
        # Spawn-and-detach so the screen pump stays responsive while
        # `adk repo rebuild-index` runs (it can take minutes).
        ctx = self._cursor_context()
        if ctx is None:
            self._log_screen("(no row highlighted)")
            return
        kind, repo_name, branch = ctx
        cmd = [str(self._adk_bin_resolver()), "repo", "rebuild-index", repo_name]
        if kind == "branch" and branch:
            cmd += ["--branch", branch]
        cmd += ["-y"]
        self._action_task = asyncio.create_task(self._spawn_subprocess(cmd, label="rebuild-index"))

    def action_delete_auto_base(self) -> None:
        ctx = self._cursor_context()
        if ctx is None or ctx[0] != "branch":
            self._log_screen("(highlight an auto-base branch to delete)")
            return
        _, repo_name, branch = ctx
        self._action_task = asyncio.create_task(self._spawn_subprocess(
            [
                str(self._adk_bin_resolver()),
                "repo",
                "auto-bases",
                "clean",
                "--force",
                repo_name,
                "--branch",
                branch,
                "-y",
            ],
            label="auto-base-clean",
        ))

    # --- helpers ---
    def _cursor_context(self) -> tuple[str, str, str | None] | None:
        tree = self.query_one(Tree)
        node = tree.cursor_node
        if node is None:
            return None
        data = getattr(node, "data", None)
        if data is None:
            return None
        return data  # type: ignore[return-value]

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
        # Force refresh because the model's signature may not have updated yet
        # if the subprocess hasn't written its metadata to disk before we tick.
        self._refresh(force=True)


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
