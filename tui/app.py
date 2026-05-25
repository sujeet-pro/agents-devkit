from __future__ import annotations

import argparse
import asyncio
import json
import os
import shlex
import sys
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING

from textual import work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from tui.widgets.detail_pane import TabbedDetailPane
from tui.widgets.footer_bar import FooterBar
from tui.widgets.header_bar import HeaderBar
from tui.widgets.help_screen import HelpScreen
from tui.widgets.log_pane import LogPane
from tui.widgets.queue_table import QueueTable
from tui.widgets.runs_pane import RunsPane
from tui.widgets.sync_plan_pane import SyncPlanPane
from tui.widgets.workers_pane import WorkersPane

if TYPE_CHECKING:
    from tui.model.queue_model import FilterMode, QueueModel, QueueRow, SortMode
    from tui.model.runs_model import RunRow, RunsModel
    from tui.model.sync_plan_model import SyncPlanModel
    from tui.model.workers_model import WorkerRow, WorkersModel


_FILTER_CYCLE: tuple[FilterMode, ...] = ("all", "open", "ready", "reviewed", "terminal")
_SORT_CYCLE: tuple[SortMode, ...] = ("queue", "newest", "repo")
_THEME_CYCLE: tuple[str, ...] = (
    "textual-dark", "textual-light", "nord", "gruvbox", "dracula",
)
_RUNNER_CHOICES: tuple[str, ...] = ("claude", "cursor", "codex", "opencode", "headless")


def _configured_runner(default: str = "claude") -> str:
    cfg_path = (
        Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
        / "config"
        / "adk-cli.json5"
    )
    if not cfg_path.exists():
        return default
    try:
        text = cfg_path.read_text(encoding="utf-8")
        try:
            import json5  # type: ignore[import-untyped]

            cfg = json5.loads(text)
        except ImportError:
            cfg = json.loads(text)
    except (OSError, ValueError, TypeError):
        return default
    if not isinstance(cfg, dict):
        return default
    pr_review_all = cfg.get("pr_review_all")
    if not isinstance(pr_review_all, dict):
        return default
    runner = pr_review_all.get("runner")
    if not isinstance(runner, str):
        return default
    runner = runner.strip()
    return runner if runner in _RUNNER_CHOICES else default


def _format_operations_summary(rows: list["RunRow"]) -> str:
    if not rows:
        return "ops: none"
    running = sum(1 for row in rows if row.status == "running")
    failed = sum(1 for row in rows if row.status == "failed")
    latest = rows[0]
    latest_label = latest.task_type or latest.run_id
    if running:
        return f"ops: {running} running · latest {latest_label}"
    if failed:
        return f"ops: {failed} failed · latest {latest_label}"
    return f"ops: latest {latest.status or 'unknown'} {latest_label}"


class AdkApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "adk"

    BINDINGS = [
        Binding("q", "quit", "quit"),
        Binding("question_mark", "help", "help"),
        Binding("f", "cycle_filter", "filter"),
        Binding("S", "cycle_sort", "sort"),
        Binding("1", "sync_pr", "Sync PR"),
        Binding("2", "sync_review_pr", "Sync+Review"),
        Binding("s", "sync_all", "Sync all"),
        Binding("A", "sync_review_all", "Sync+Review all"),
        Binding("l", "show_logs", "logs"),
        Binding("L", "show_run_logs", "run-logs"),
        Binding("enter", "pr_actions", "actions"),
        Binding("a", "pick_agent", "runner"),
        Binding("plus", "add_pr", "add-pr"),
        Binding("b", "repos", "repos"),
        Binding("t", "cycle_theme", "theme"),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("g", "cursor_home", show=False),
        Binding("G", "cursor_end", show=False),
        Binding("escape", "escape", show=False),
        # Secondary/hidden — accessible but not shown in primary footer.
        Binding("u", "update_pr", show=False),
        Binding("x", "refresh_context", show=False),
        Binding("I", "update_index", show=False),
        Binding("v", "rereview", show=False),
        Binding("m", "merge_status", show=False),
        Binding("M", "merge_pr", show=False),
        Binding("o", "open_links", show=False),
        Binding("O", "open_slack", show=False),
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
        runs_dir: Path | None = None,
        worker_script: Path | None = None,
        repos_dir: Path | None = None,
        agent: str = "claude",
    ) -> None:
        super().__init__()
        self._queue_path = queue_path
        self._ascii_only = ascii_only
        self.poll_interval = poll_interval
        self._plan_path = plan_path
        self._adk_bin = adk_bin
        self._agent_bin = agent_bin
        self._heartbeat_dir = heartbeat_dir
        self._runs_dir = runs_dir
        self._worker_script = worker_script
        self._repos_dir: Path | None = repos_dir
        self._current_agent: str = agent
        self._filter_mode: FilterMode = "all"
        self._sort_mode: SortMode = "queue"
        self._model: QueueModel | None = None
        self._plan_model: SyncPlanModel | None = None
        self._workers_model: WorkersModel | None = None
        self._runs_model: RunsModel | None = None
        self._rows_by_url: dict[str, QueueRow] = {}
        self._workers_by_url: dict[str, WorkerRow] = {}
        self._run_rows: list[RunRow] = []
        self._operations_summary = "ops: none"
        self._sync_proc: asyncio.subprocess.Process | None = None
        self._sync_task: asyncio.Task | None = None
        self._review_workers: dict[str, asyncio.subprocess.Process] = {}
        self._review_tasks: dict[str, asyncio.Task] = {}
        self._add_pr_task: asyncio.Task | None = None
        from tui.model.work_queue_model import WorkQueueModel

        self._work_queue = WorkQueueModel()
        self._work_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with Horizontal(id="main"):
            yield QueueTable()
            yield TabbedDetailPane()
        yield WorkersPane()
        yield RunsPane()
        yield SyncPlanPane()
        yield LogPane()
        yield FooterBar()

    async def on_mount(self) -> None:
        from tui.model.queue_model import QueueModel
        from tui.model.runs_model import RunsModel
        from tui.model.sync_plan_model import SyncPlanModel
        from tui.model.workers_model import WorkersModel

        self._model = QueueModel(queue_path=self._queue_path)
        self._plan_model = SyncPlanModel(plan_path=self._plan_path)
        self._workers_model = WorkersModel(workers_dir=self._heartbeat_dir)
        self._runs_model = RunsModel(runs_dir=self._runs_dir)
        self._update_footer()
        self._reload(force=True)
        self._reload_plan(force=True)
        self._reload_workers(force=True)
        self._reload_runs(force=True)
        # Reattach-on-restart banner: surface pre-existing live workers (from
        # this user's other terminals OR from a prior TUI session) so the
        # operator knows the TUI is observing them — even though it didn't
        # spawn them and can't kill them on quit.
        n_existing = len(self._workers_by_url)
        if n_existing > 0:
            self.query_one(LogPane).write(
                f"(reattached: {n_existing} existing worker"
                f"{'' if n_existing == 1 else 's'} from heartbeat dir)"
            )
        self.set_interval(self.poll_interval, self._maybe_reload)

    def _default_query(self, widget_type):
        """Query for a widget on the DEFAULT screen, not the active one.
        Critical for timer-driven reloads: when a modal (HelpScreen,
        PromptScreen, RecapScreen, etc.) is on top, `self.query_one(X)`
        searches the modal and raises NoMatches. The default screen
        (`screen_stack[0]`) is where the AdkApp's main widgets live.

        Raises `IndexError` if the screen_stack is empty (app is
        unmounting); callers in periodic timers should guard via
        `_maybe_reload`'s screen_stack check."""
        return self.screen_stack[0].query_one(widget_type)

    def _sync_all_running(self) -> bool:
        if self._sync_proc is not None and self._sync_proc.returncode is None:
            return True
        return self._sync_task is not None and not self._sync_task.done()

    def _work_running(self) -> bool:
        return self._work_task is not None and not self._work_task.done()

    def _update_footer(self, *, row: "QueueRow | None" = None) -> None:
        if not self.screen_stack:
            return
        self._default_query(FooterBar).update_status(
            self._filter_mode,
            self._sort_mode,
            sync_all_running=self._sync_all_running(),
            work_running=self._work_running(),
            agent=self._current_agent,
            row=row,
        )

    def _work_text_for_url(self, url: str | None) -> str | None:
        if not url:
            return None
        state = self._work_queue.get(url)
        if state is None:
            return None
        from tui.model.work_queue_model import format_work_cell

        return format_work_cell(state)

    def _selected_pr_url(self) -> str | None:
        if not self.screen_stack:
            return None
        return self._default_query(QueueTable).selected_pr_url()

    def _reload(self, *, force: bool = False) -> None:
        if self._model is None:
            return
        # Skip during unmount — background tasks (worker finally, batch task)
        # can call this after on_unmount drains screen_stack.
        if not self.screen_stack:
            return
        if not force and not self._model.has_changed():
            return
        snapshot = self._model.snapshot(
            filter_mode=self._filter_mode,
            sort_mode=self._sort_mode,
        )
        self._rows_by_url = {row.pr_url: row for row in snapshot.rows}
        self._default_query(HeaderBar).update_snapshot(
            snapshot,
            operations=self._operations_summary,
        )
        self._default_query(QueueTable).load(
            snapshot,
            ascii_only=self._ascii_only,
            work_states=self._work_queue.all_states(),
            workers_by_url=self._workers_by_url,
        )
        self._update_footer()
        self._refresh_detail()

    def _reload_plan(self, *, force: bool = False) -> None:
        if self._plan_model is None:
            return
        if not self.screen_stack:
            return
        if not force and not self._plan_model.has_changed():
            return
        snapshot = self._plan_model.snapshot()
        self._default_query(SyncPlanPane).update_snapshot(snapshot, ascii_only=self._ascii_only)

    def _reload_workers(self, *, force: bool = False) -> None:
        if self._workers_model is None:
            return
        if not self.screen_stack:
            return
        if not force and not self._workers_model.has_changed():
            return
        rows = self._workers_model.snapshot()
        self._default_query(WorkersPane).update_workers(rows, ascii_only=self._ascii_only)
        self._workers_by_url = {w.pr_url: w for w in rows if not w.is_stale}
        if self._model is not None:
            self._reload(force=True)
        self._refresh_detail()

    def _reload_runs(self, *, force: bool = False) -> None:
        if self._runs_model is None:
            return
        if not self.screen_stack:
            return
        if not force and not self._runs_model.has_changed():
            return
        rows = self._runs_model.snapshot()
        self._run_rows = rows
        self._operations_summary = _format_operations_summary(rows)
        self._default_query(RunsPane).update_runs(rows)
        if self._model is not None:
            self._reload(force=True)

    def _maybe_reload(self) -> None:
        # Skip if the app is unmounting (screen_stack drains during teardown);
        # the timer can fire one last tick after on_unmount starts.
        if not self.screen_stack:
            return
        if self._model is not None and self._model.has_changed():
            self._reload(force=True)
        self._reload_plan()
        self._reload_workers()
        self._reload_runs()

    def _refresh_detail(self) -> None:
        if not self.screen_stack:
            return
        table = self._default_query(QueueTable)
        url = table.selected_pr_url()
        row = self._rows_by_url.get(url) if url else None
        worker = self._workers_by_url.get(url) if url else None
        self._default_query(TabbedDetailPane).show(
            row,
            worker=worker,
            work_text=self._work_text_for_url(url),
        )
        self._update_footer(row=row)

    def on_data_table_row_highlighted(self) -> None:
        self._refresh_detail()

    def on_queue_table_pr_number_clicked(self, event: QueueTable.PrNumberClicked) -> None:
        pr_url = event.pr_url
        if not pr_url:
            return
        self._run_pr_command("open PR", ["pr", "open"], pr_url)

    def on_data_table_row_selected(self, event) -> None:
        if not isinstance(event.data_table, QueueTable):
            return
        event.stop()
        self.action_pr_actions()

    @work
    async def action_pr_actions(self) -> None:
        from tui.screens.pr_action_screen import PrActionScreen

        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        row = self._rows_by_url.get(pr_url)
        label = f"{row.repo}#{row.number}" if row is not None else pr_url
        # Pre-fetch CLI action availability non-blockingly; falls back to None
        # if the subprocess is unavailable or times out, so the modal still
        # opens with local state-based filtering applied.
        availability = await self._fetch_action_availability(pr_url)
        action = await self.push_screen_wait(
            PrActionScreen(pr_label=label, row=row, availability=availability)
        )
        if action is None:
            return
        await self._perform_pr_action(action, pr_url)

    async def _fetch_action_availability(self, pr_url: str) -> "dict | None":
        """Run ``adk pr action-availability <pr_url>`` and return the parsed JSON.

        Non-blocking: times out after 2 s so the action menu never hangs.
        Returns ``None`` on any error so callers fall back to local filtering.
        """
        adk = self._resolve_adk_bin()
        cmd = [str(adk), "pr"]
        if self._queue_path is not None:
            cmd += ["--queue", str(self._queue_path)]
        cmd += ["action-availability", pr_url]
        try:
            proc = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                ),
                timeout=2.0,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=2.0)
            if proc.returncode == 0:
                return json.loads(stdout.decode(errors="replace"))
        except (
            asyncio.TimeoutError,
            FileNotFoundError,
            PermissionError,
            OSError,
            json.JSONDecodeError,
            ValueError,
        ):
            pass
        return None

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

    def action_cycle_theme(self) -> None:
        """Rotate through the curated theme set; falls through to the first
        if the current theme isn't in the cycle."""
        try:
            idx = _THEME_CYCLE.index(self.theme)
        except ValueError:
            idx = -1
        new_theme = _THEME_CYCLE[(idx + 1) % len(_THEME_CYCLE)]
        self.theme = new_theme
        self.query_one(LogPane).write(f"(theme: {new_theme})")

    @work
    async def action_quit(self) -> None:
        """Override Textual's default quit so we can warn when reviews are
        still running. The user can confirm (terminate + exit) or cancel."""
        n_live = sum(
            1 for proc in self._review_workers.values()
            if proc.returncode is None
        )
        if self._sync_proc is not None and self._sync_proc.returncode is None:
            n_live += 1
        if self._work_task is not None and not self._work_task.done():
            n_live += 1
        if n_live > 0:
            from tui.screens.confirm_screen import ConfirmScreen
            if any(isinstance(s, ConfirmScreen) for s in self.screen_stack):
                return  # already prompting; ignore double-q
            ok = await self.push_screen_wait(ConfirmScreen(
                f"{n_live} subprocess{'es' if n_live != 1 else ''} still running. "
                "Quit anyway? (workers will be terminated)"
            ))
            if not ok:
                return
        self.exit()

    @work
    async def action_pick_agent(self) -> None:
        from tui.screens.agent_picker_screen import AgentPickerScreen
        if any(isinstance(s, AgentPickerScreen) for s in self.screen_stack):
            return
        picked = await self.push_screen_wait(
            AgentPickerScreen(current=self._current_agent)
        )
        if not picked:
            return
        self._current_agent = picked
        self._update_footer()

    @work
    async def action_add_pr(self) -> None:
        # @work wraps the coroutine in a Textual worker, which is required for
        # push_screen_wait to resolve. Without it, push_screen_wait raises
        # NoActiveWorker.
        from tui.screens.prompt_screen import PromptScreen
        # Pre-check busy state BEFORE opening the modal so the user isn't
        # asked to type a value that we'll just reject.
        busy = self._busy_label()
        if busy is not None:
            self.query_one(LogPane).write(f"(can't add PR — {busy} already running)")
            return
        # Don't stack a second PromptScreen if one's already up.
        if any(isinstance(s, PromptScreen) for s in self.screen_stack):
            return
        value = await self.push_screen_wait(
            PromptScreen("Add PR", "URL, owner/repo#N, or PR number")
        )
        if not value:
            return
        self._add_pr_task = asyncio.create_task(self._run_add_pr(value.strip()))

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

    def action_repos(self) -> None:
        from tui.screens.repo_screen import RepoScreen
        self.push_screen(RepoScreen(
            repos_dir=self._repos_dir,
            adk_bin_resolver=self._resolve_adk_bin,
        ))

    def _busy_label(self) -> str | None:
        """Return a short label of any running subprocess, else None."""
        if self._sync_all_running():
            return "sync all"
        if self._work_running():
            return "work queue"
        if self._add_pr_task is not None and not self._add_pr_task.done():
            return "add-pr"
        if self._review_workers:
            return "review"
        return None

    def action_sync_all(self) -> None:
        busy = self._busy_label()
        if busy == "sync all":
            self.query_one(LogPane).write("(Sync all already running — wait or quit and restart)")
            return
        if busy is not None:
            self.query_one(LogPane).write(f"(can't start Sync all — {busy} already running)")
            return
        self._sync_task = asyncio.create_task(self._run_sync())
        self._sync_task.add_done_callback(self._on_sync_task_done)

    def action_sync_pr(self) -> None:
        pr_url = self._selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        busy = self._busy_label()
        if busy is not None:
            self.query_one(LogPane).write(f"(can't start Sync PR — {busy} already running)")
            return
        self._work_task = asyncio.create_task(self._work_sync_pr(pr_url))
        self._work_task.add_done_callback(self._on_work_task_done)

    def action_sync_review_pr(self) -> None:
        pr_url = self._selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        busy = self._busy_label()
        if busy is not None:
            self.query_one(LogPane).write(
                f"(can't start Sync + Review — {busy} already running)"
            )
            return
        self._work_task = asyncio.create_task(self._work_sync_review_pr(pr_url))
        self._work_task.add_done_callback(self._on_work_task_done)
        self._update_footer()

    def action_sync_review_all(self) -> None:
        busy = self._busy_label()
        if busy is not None:
            self.query_one(LogPane).write(
                f"(can't start Sync + Review all — {busy} already running)"
            )
            return
        self._work_task = asyncio.create_task(self._work_sync_review_all())
        self._work_task.add_done_callback(self._on_work_task_done)
        self._update_footer()

    async def _work_sync_pr(self, pr_url: str) -> None:
        log_pane = self.query_one(LogPane)
        self._work_queue.set_global_mode("sync-pr")
        self._work_queue.set(pr_url, "running", "sync")
        self._reload(force=True)
        try:
            rc = await self._sync_single_pr(pr_url)
            self._work_queue.set(
                pr_url,
                "done" if rc == 0 else "failed",
                "sync",
                message=f"rc={rc}",
            )
        except BaseException as exc:
            self._work_queue.set(pr_url, "failed", "sync", message=repr(exc))
            log_pane.write(f"(Sync PR crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    async def _work_sync_review_pr(self, pr_url: str) -> None:
        log_pane = self.query_one(LogPane)
        self._work_queue.set_global_mode("sync-review")
        self._work_queue.set(pr_url, "running", "sync+review")
        self._reload(force=True)
        try:
            rc = await self._sync_single_pr(pr_url)
            if rc != 0:
                self._work_queue.set(pr_url, "failed", "sync+review", message=f"sync rc={rc}")
                return
            self._reload(force=True)
            row = self._rows_by_url.get(pr_url)
            if row is None or not row.ready_for_review:
                self._work_queue.set(pr_url, "skipped", "sync+review", message="not ready")
                log_pane.write(f"(skipping review — row not ready: {pr_url})")
                return
            self._work_queue.set(pr_url, "running", "sync+review")
            self._reload(force=True)
            result = await self._run_review(pr_url)
            outcome = result.get("outcome", "failed")
            self._work_queue.set(
                pr_url,
                "done" if outcome == "ok" else "failed",
                "sync+review",
                message=str(result.get("last_line") or outcome)[:40],
            )
        except BaseException as exc:
            self._work_queue.set(pr_url, "failed", "sync+review", message=repr(exc))
            log_pane.write(f"(Sync + Review crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    async def _work_sync_review_all(self) -> None:
        log_pane = self.query_one(LogPane)
        self._work_queue.set_global_mode("sync-review-all")
        self._update_footer()
        try:
            await self._run_sync()
            self._reload(force=True)
            urls = [
                row.pr_url
                for row in self._rows_by_url.values()
                if row.ready_for_review
            ]
            if not urls:
                log_pane.write("(Sync + Review all — no eligible rows after sync)")
                return
            for url in urls:
                self._work_queue.set(url, "queued", "sync+review")
            self._reload(force=True)
            outcomes: list[dict] = []
            for url in urls:
                row = self._rows_by_url.get(url)
                if row is None or not row.ready_for_review:
                    self._work_queue.set(url, "skipped", "sync+review", message="not ready")
                    outcomes.append({
                        "pr_url": url, "rc": None,
                        "last_line": "not ready", "outcome": "skipped",
                    })
                    continue
                self._work_queue.set(url, "running", "sync+review")
                self._reload(force=True)
                result = await self._run_review(url)
                outcome = result.get("outcome", "failed")
                self._work_queue.set(
                    url,
                    "done" if outcome == "ok" else "failed",
                    "sync+review",
                    message=str(result.get("last_line") or outcome)[:40],
                )
                outcomes.append(result)
                self._reload(force=True)
            log_pane.write(f"(Sync + Review all done — {len(urls)} row(s))")
            if outcomes:
                from tui.screens.recap_screen import RecapScreen
                self.push_screen(RecapScreen(outcomes=outcomes, ascii_only=self._ascii_only))
        except BaseException as exc:
            log_pane.write(f"(Sync + Review all crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    async def _sync_single_pr(self, pr_url: str) -> int:
        rc = await self._run_adk_command("update PR", ["pr-queue", "update", pr_url])
        if rc != 0:
            return rc
        return await self._run_adk_command("prepare index", ["pr-task", "prepare", pr_url])

    def _on_work_task_done(self, task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(work queue crashed: {exc!r})")
            except Exception:
                pass
        self._work_task = None
        self._work_queue.set_global_mode(None)
        self._update_footer()

    def action_update_pr(self) -> None:
        self._run_selected_pr_command("update PR", ["pr-queue", "update"])

    def action_refresh_context(self) -> None:
        self._run_selected_pr_command("refresh context", ["pr", "context-refresh"])

    def action_update_index(self) -> None:
        self._run_selected_pr_command("update index", ["pr-task", "prepare"])

    def action_merge_status(self) -> None:
        self._run_selected_info_pr_command("merge status", ["pr", "merge-status"])

    def action_open_links(self) -> None:
        self._run_selected_pr_command("open PR", ["pr", "open"])

    def action_open_slack(self) -> None:
        self._run_selected_pr_command("open Slack", ["pr", "open", "--target", "slack"])

    def action_rereview(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        self._start_review_for_url(pr_url, force=True)

    @work
    async def action_merge_pr(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        await self._confirm_and_merge(pr_url)

    def action_show_logs(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        worker = self._workers_by_url.get(pr_url)
        log_path = worker.log_path if worker is not None else None
        label = "active worker"
        if not log_path:
            log_path = self._latest_result_log_for_pr(pr_url)
            label = "latest review result"
        if not log_path:
            self.query_one(LogPane).write(f"(no log found for {pr_url})")
            return
        self._write_log_tail(log_path, label=label, max_lines=120)

    def action_show_run_logs(self) -> None:
        if not self._run_rows:
            self.query_one(LogPane).write("(no run logs found)")
            return
        run = self._run_rows[0]
        log_pane = self.query_one(LogPane)
        log_pane.write(f"(run logs: {run.run_id})")

        written = False
        for step in run.steps:
            log_path = step.get("log_path")
            if log_path:
                self._write_log_tail(
                    str(log_path),
                    label=str(step.get("name") or "step"),
                    max_lines=60,
                )
                written = True

        active_workers = [
            w for w in self._workers_by_url.values()
            if (run.run_id and w.run_id == run.run_id) or run.status == "running"
        ]
        for worker in active_workers:
            if worker.log_path:
                label = worker.current_phase or worker.pr_url or worker.worker_id
                self._write_log_tail(worker.log_path, label=label, max_lines=60)
                written = True

        for result in run.results:
            log_path = result.get("log")
            if log_path:
                label = str(result.get("pr_url") or "review")
                self._write_log_tail(str(log_path), label=label, max_lines=60)
                written = True

        if not written and run.run_dir:
            sync_log = Path(run.run_dir).expanduser() / "pr-sync.log"
            if sync_log.exists():
                self._write_log_tail(str(sync_log), label="pr-sync", max_lines=60)
                written = True

        if not written:
            log_pane.write("(latest run has no log paths yet)")

    async def _perform_pr_action(self, action: str, pr_url: str) -> None:
        if action == "open-pr":
            self._run_pr_command("open PR", ["pr", "open"], pr_url)
        elif action == "open-slack":
            self._run_pr_command("open Slack", ["pr", "open", "--target", "slack"], pr_url)
        elif action == "update-pr":
            self._run_pr_command("update PR", ["pr-queue", "update"], pr_url)
        elif action == "refresh-context":
            self._run_pr_command("refresh context", ["pr", "context-refresh"], pr_url)
        elif action == "update-index":
            self._run_pr_command("update index", ["pr-task", "prepare"], pr_url)
        elif action == "review":
            self._start_review_for_url(pr_url, force=False)
        elif action == "rereview":
            self._start_review_for_url(pr_url, force=True)
        elif action == "merge-status":
            self._run_info_pr_command("merge status", ["pr", "merge-status"], pr_url)
        elif action == "merge":
            await self._confirm_and_merge(pr_url)
        elif action == "show-logs":
            self.action_show_logs()

    def _start_review_for_url(self, pr_url: str, *, force: bool) -> None:
        if pr_url in self._review_tasks and not self._review_tasks[pr_url].done():
            self.query_one(LogPane).write(f"(review already running for {pr_url})")
            return
        extra = ["--force"] if force else None
        task = asyncio.create_task(self._run_review(pr_url, extra_worker_args=extra))
        self._review_tasks[pr_url] = task
        task.add_done_callback(self._on_review_task_done)

    async def _confirm_and_merge(self, pr_url: str) -> None:
        from tui.screens.confirm_screen import ConfirmScreen

        ok = await self.push_screen_wait(ConfirmScreen(
            f"Merge this PR via provider API?\n\n{pr_url}\n\n"
            "This is never run by auto mode. The CLI will re-check merge status first.",
            yes_label="merge",
            no_label="cancel",
        ))
        if not ok:
            return
        self._run_pr_command("merge PR", ["pr", "merge", "--yes", "--tui-confirmed"], pr_url)

    def _on_review_task_done(self, task: asyncio.Task) -> None:
        # Find the URL this task was associated with so we can drop it from the registry.
        url_done: str | None = None
        for url, t in self._review_tasks.items():
            if t is task:
                url_done = url
                break
        if url_done is not None:
            self._review_tasks.pop(url_done, None)
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(review crashed: {exc!r})")
                self._update_footer()
            except Exception:
                pass

    def _on_sync_task_done(self, task: asyncio.Task) -> None:
        self._sync_task = None
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            self._update_footer()
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(sync crashed: {exc!r})")
            except Exception:
                pass
            self._sync_proc = None
        self._update_footer()

    def _run_selected_pr_command(self, label: str, prefix: list[str]) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        self._run_pr_command(label, prefix, pr_url)

    def _run_pr_command(self, label: str, prefix: list[str], pr_url: str) -> None:
        task = asyncio.create_task(self._run_adk_command(label, [*prefix, pr_url]))
        task.add_done_callback(lambda t: self._on_background_action_done(label, t))

    def _run_info_pr_command(self, label: str, prefix: list[str], pr_url: str) -> None:
        """Like _run_pr_command but routes output to an InfoScreen instead of LogPane."""
        task = asyncio.create_task(self._run_info_adk_command(label, [*prefix, pr_url]))
        task.add_done_callback(lambda t: self._on_background_action_done(label, t))

    def _run_selected_info_pr_command(self, label: str, prefix: list[str]) -> None:
        """Like _run_selected_pr_command but routes output to an InfoScreen."""
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self.query_one(LogPane).write("(no row selected)")
            return
        self._run_info_pr_command(label, prefix, pr_url)

    def _on_background_action_done(self, label: str, task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"({label} crashed: {exc!r})")
            except Exception:
                pass

    async def _run_adk_command(self, label: str, args: list[str]) -> int:
        log_pane = self.query_one(LogPane)
        adk = self._resolve_adk_bin()
        if self._queue_path is not None and args and args[0] in {"pr-queue", "pr"}:
            cmd = [str(adk), args[0], "--queue", str(self._queue_path), *args[1:]]
        elif self._queue_path is not None and args[:2] == ["pr-task", "prepare"]:
            cmd = [str(adk), *args, "--queue", str(self._queue_path)]
        else:
            cmd = [str(adk), *args]
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            log_pane.write(f"({label} error: {exc})")
            return 2
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            log_pane.write(line.decode(errors="replace").rstrip("\n"))
        rc = await proc.wait()
        log_pane.write(f"({label} exited rc={rc})")
        self._reload(force=True)
        self._reload_runs(force=True)
        self._reload_workers(force=True)
        return rc

    async def _run_info_adk_command(self, label: str, args: list[str]) -> int:
        """Like _run_adk_command, but collects output and displays it in an InfoScreen.

        The LogPane still receives the command line and the exit-code line so
        the activity record is preserved.  The actual command output goes to a
        dedicated modal panel the user can review at their own pace.
        """
        from tui.screens.info_screen import InfoScreen

        log_pane = self.query_one(LogPane)
        adk = self._resolve_adk_bin()
        if self._queue_path is not None and args and args[0] in {"pr-queue", "pr"}:
            cmd = [str(adk), args[0], "--queue", str(self._queue_path), *args[1:]]
        elif self._queue_path is not None and args[:2] == ["pr-task", "prepare"]:
            cmd = [str(adk), *args, "--queue", str(self._queue_path)]
        else:
            cmd = [str(adk), *args]
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            log_pane.write(f"({label} error: {exc})")
            return 2
        assert proc.stdout is not None
        output_lines: list[str] = []
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            output_lines.append(line.decode(errors="replace").rstrip("\n"))
        rc = await proc.wait()
        log_pane.write(f"({label} exited rc={rc})")
        self._reload(force=True)
        self._reload_runs(force=True)
        self._reload_workers(force=True)
        self.push_screen(InfoScreen(title=label, content="\n".join(output_lines), rc=rc))
        return rc

    async def _run_sync(self) -> None:
        log_pane = self.query_one(LogPane)
        queue_arg: list[str] = []
        if self._queue_path is not None:
            queue_arg = ["--queue", str(self._queue_path)]
        adk = self._resolve_adk_bin()
        cmd = [str(adk), "pr-sync", *queue_arg]
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        self._update_footer()
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
            self._update_footer()
            return
        self._update_footer()
        assert self._sync_proc.stdout is not None
        while True:
            line = await self._sync_proc.stdout.readline()
            if not line:
                break
            log_pane.write(line.decode(errors="replace").rstrip("\n"))
        rc = await self._sync_proc.wait()
        log_pane.write(f"(pr-sync exited rc={rc})")
        self._sync_proc = None
        self._update_footer()
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

    def _latest_result_log_for_pr(self, pr_url: str) -> str | None:
        for run in self._run_rows:
            for result in run.results:
                if result.get("pr_url") == pr_url and result.get("log"):
                    return str(result["log"])
        return None

    def _write_log_tail(self, log_path: str, *, label: str, max_lines: int) -> None:
        log_pane = self.query_one(LogPane)
        path = Path(log_path).expanduser()
        if not path.exists():
            log_pane.write(f"(log missing: {path})")
            return
        try:
            lines: deque[str] = deque(maxlen=max_lines)
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    lines.append(line.rstrip("\n"))
        except OSError as exc:
            log_pane.write(f"(log read error: {path}: {exc})")
            return
        log_pane.write(f"(log: {label} — {path} — last {len(lines)} lines)")
        if not lines:
            log_pane.write("(log is empty)")
            return
        for line in lines:
            log_pane.write(line)

    def _resolve_worker_script(self) -> Path:
        if self._worker_script is not None:
            return self._worker_script
        return Path(__file__).resolve().parent / "worker.py"

    async def _run_review(self, pr_url: str, *, extra_worker_args: list[str] | None = None) -> dict:
        """Run one worker. Returns an outcome dict the batch driver collects
        for the end-of-run recap: `{pr_url, rc, last_line, outcome}` where
        outcome is `"ok"` (rc=0), `"failed"` (rc!=0), or `"spawn-error"` (the
        subprocess never started)."""
        log_pane = self.query_one(LogPane)
        worker = self._resolve_worker_script()
        cmd: list[str] = [sys.executable, str(worker), pr_url]
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
        if extra_worker_args:
            cmd += extra_worker_args
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            log_pane.write(f"(error: {exc})")
            self._update_footer()
            return {"pr_url": pr_url, "rc": None,
                    "last_line": f"spawn error: {exc}",
                    "outcome": "spawn-error"}
        self._review_workers[pr_url] = proc
        self._update_footer()
        last_line = ""
        try:
            assert proc.stdout is not None
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                text = line.decode(errors="replace").rstrip("\n")
                log_pane.write(text)
                if text:
                    last_line = text
            rc = await proc.wait()
            log_pane.write(f"(worker exited rc={rc})")
            return {"pr_url": pr_url, "rc": rc, "last_line": last_line,
                    "outcome": "ok" if rc == 0 else "failed"}
        finally:
            self._review_workers.pop(pr_url, None)
            self._update_footer()
            self._reload(force=True)

    async def on_unmount(self) -> None:
        procs = [self._sync_proc, *self._review_workers.values()]
        for proc in procs:
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
    parser.add_argument(
        "--runner",
        choices=_RUNNER_CHOICES,
        default=None,
        help="runner shown in the TUI and passed to review commands "
             "(default: pr_review_all.runner, fallback claude)",
    )
    args = parser.parse_args(argv)
    runner = args.runner or _configured_runner()

    try:
        app = AdkApp(
            queue_path=args.queue_path,
            ascii_only=args.ascii,
            poll_interval=args.poll_interval,
            agent=runner,
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
