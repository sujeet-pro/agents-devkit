from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from tui.widgets.detail_pane import DetailPane
from tui.widgets.footer_bar import FooterBar
from tui.widgets.header_bar import HeaderBar
from tui.widgets.help_screen import HelpScreen
from tui.widgets.log_pane import LogPane
from tui.widgets.queue_table import QueueTable
from tui.widgets.sync_plan_pane import SyncPlanPane

if TYPE_CHECKING:
    from tui.model.queue_model import FilterMode, QueueModel, QueueRow, SortMode
    from tui.model.sync_plan_model import SyncPlanModel


_FILTER_CYCLE: tuple[FilterMode, ...] = ("all", "open", "ready", "reviewed", "terminal")
_SORT_CYCLE: tuple[SortMode, ...] = ("fifo", "newest", "repo")


class AdkApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "adk"

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("question_mark", "help", "help"),
        Binding("f", "cycle_filter", "filter"),
        Binding("S", "cycle_sort", "sort"),
        Binding("s", "sync", "sync"),
        Binding("r", "review", "review"),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("g", "cursor_home", show=False),
        Binding("G", "cursor_end", show=False),
        Binding("escape", "escape", show=False),
    ]

    def __init__(
        self,
        *,
        queue_path: Path | None = None,
        ascii_only: bool = False,
        poll_interval: float = 2.0,
        plan_path: Path | None = None,
        adk_bin: Path | None = None,
        agent_bin: Path | None = None,
        heartbeat_dir: Path | None = None,
        worker_script: Path | None = None,
    ) -> None:
        super().__init__()
        self._queue_path = queue_path
        self._ascii_only = ascii_only
        self.poll_interval = poll_interval
        self._plan_path = plan_path
        self._adk_bin = adk_bin
        self._agent_bin = agent_bin
        self._heartbeat_dir = heartbeat_dir
        self._worker_script = worker_script
        self._filter_mode: FilterMode = "all"
        self._sort_mode: SortMode = "fifo"
        self._model: QueueModel | None = None
        self._plan_model: SyncPlanModel | None = None
        self._rows_by_url: dict[str, QueueRow] = {}
        self._sync_proc: asyncio.subprocess.Process | None = None
        self._sync_task: asyncio.Task | None = None
        self._review_proc: asyncio.subprocess.Process | None = None
        self._review_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with Horizontal(id="main"):
            yield QueueTable()
            yield DetailPane()
        yield SyncPlanPane()
        yield LogPane()
        yield FooterBar()

    async def on_mount(self) -> None:
        from tui.model.queue_model import QueueModel
        from tui.model.sync_plan_model import SyncPlanModel

        self._model = QueueModel(queue_path=self._queue_path)
        self._plan_model = SyncPlanModel(plan_path=self._plan_path)
        self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=False)
        self._reload(force=True)
        self._reload_plan(force=True)
        self.set_interval(self.poll_interval, self._maybe_reload)

    def _reload(self, *, force: bool = False) -> None:
        if self._model is None:
            return
        if not force and not self._model.has_changed():
            return
        snapshot = self._model.snapshot(
            filter_mode=self._filter_mode,
            sort_mode=self._sort_mode,
        )
        self._rows_by_url = {row.pr_url: row for row in snapshot.rows}
        self.query_one(HeaderBar).update_snapshot(snapshot)
        self.query_one(QueueTable).load(snapshot, ascii_only=self._ascii_only)
        self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode)
        self._refresh_detail()

    def _reload_plan(self, *, force: bool = False) -> None:
        if self._plan_model is None:
            return
        if not force and not self._plan_model.has_changed():
            return
        snapshot = self._plan_model.snapshot()
        self.query_one(SyncPlanPane).update_snapshot(snapshot, ascii_only=self._ascii_only)

    def _maybe_reload(self) -> None:
        if self._model is not None and self._model.has_changed():
            self._reload(force=True)
        self._reload_plan()

    def _refresh_detail(self) -> None:
        table = self.query_one(QueueTable)
        url = table.selected_pr_url()
        row = self._rows_by_url.get(url) if url else None
        self.query_one(DetailPane).show(row)

    def on_data_table_row_highlighted(self) -> None:
        self._refresh_detail()

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_cycle_filter(self) -> None:
        idx = _FILTER_CYCLE.index(self._filter_mode)
        self._filter_mode = _FILTER_CYCLE[(idx + 1) % len(_FILTER_CYCLE)]
        self._reload(force=True)

    def action_cycle_sort(self) -> None:
        idx = _SORT_CYCLE.index(self._sort_mode)
        self._sort_mode = _SORT_CYCLE[(idx + 1) % len(_SORT_CYCLE)]
        self._reload(force=True)

    def action_cursor_down(self) -> None:
        self.query_one(QueueTable).action_cursor_down()
        self._refresh_detail()

    def action_cursor_up(self) -> None:
        self.query_one(QueueTable).action_cursor_up()
        self._refresh_detail()

    def action_cursor_home(self) -> None:
        table = self.query_one(QueueTable)
        if table.row_count > 0:
            table.move_cursor(row=0)
            self._refresh_detail()

    def action_cursor_end(self) -> None:
        table = self.query_one(QueueTable)
        if table.row_count > 0:
            table.move_cursor(row=table.row_count - 1)
            self._refresh_detail()

    def action_escape(self) -> None:
        return None

    def _busy(self) -> str | None:
        """Return a short label of any running subprocess, else None."""
        if self._sync_proc is not None and self._sync_proc.returncode is None:
            return "sync"
        if self._review_proc is not None and self._review_proc.returncode is None:
            return "review"
        return None

    def action_sync(self) -> None:
        busy = self._busy()
        if busy == "sync":
            # Preserve legacy message for s-while-s-running (matches existing test).
            self.query_one(LogPane).write("(sync already running — wait or quit and restart)")
            return
        if busy is not None:
            self.query_one(LogPane).write(f"(can't start sync — {busy} already running)")
            return
        self._sync_task = asyncio.create_task(self._run_sync())
        self._sync_task.add_done_callback(self._on_sync_task_done)

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

    def _on_review_task_done(self, task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(review crashed: {exc!r})")
                self.query_one(FooterBar).update_status(
                    self._filter_mode, self._sort_mode,
                    sync_running=False, review_running=False,
                )
            except Exception:
                pass
            self._review_proc = None

    def _on_sync_task_done(self, task: asyncio.Task) -> None:
        # Surface unhandled exceptions to the LogPane so a quiet hang never
        # leaves the footer stuck on "(running…)".
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(sync crashed: {exc!r})")
                self.query_one(FooterBar).update_status(
                    self._filter_mode, self._sort_mode, sync_running=False,
                )
            except Exception:
                pass
            self._sync_proc = None

    async def _run_sync(self) -> None:
        log_pane = self.query_one(LogPane)
        queue_arg: list[str] = []
        if self._queue_path is not None:
            queue_arg = ["--queue", str(self._queue_path)]
        adk = self._resolve_adk_bin()
        cmd = [str(adk), "pr-sync", *queue_arg]
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
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
        except (FileNotFoundError, PermissionError, OSError) as exc:
            log_pane.write(f"(error: {exc})")
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
        log_pane.write(f"(pr-sync exited rc={rc})")
        self._sync_proc = None
        self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode, sync_running=False)
        self._reload_plan(force=True)
        if self._model is not None:
            self._reload(force=True)

    def _resolve_adk_bin(self) -> Path:
        if self._adk_bin is not None:
            return self._adk_bin
        repo_root = Path(__file__).resolve().parent.parent
        candidate = repo_root / "bin" / "adk"
        if candidate.exists():
            return candidate
        return Path("adk")  # last-resort PATH lookup

    def _resolve_worker_script(self) -> Path:
        if self._worker_script is not None:
            return self._worker_script
        return Path(__file__).resolve().parent / "worker.py"

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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="adk", description="adk TUI")
    parser.add_argument("--queue-path", type=Path, default=None)
    parser.add_argument("--ascii", action="store_true")
    parser.add_argument("--poll-interval", type=float, default=2.0)
    args = parser.parse_args(argv)

    try:
        app = AdkApp(
            queue_path=args.queue_path,
            ascii_only=args.ascii,
            poll_interval=args.poll_interval,
        )
    except ImportError as exc:
        print(f"adk TUI: missing dependency — {exc}")
        print("install with: pip install 'textual>=0.86'")
        return 2

    try:
        app.run()
    except KeyboardInterrupt:
        return 130
    return 0
