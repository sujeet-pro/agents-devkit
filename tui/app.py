from __future__ import annotations

import argparse
import asyncio
import os
import shlex
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from textual import work
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
from tui.widgets.workers_pane import WorkersPane

if TYPE_CHECKING:
    from tui.model.queue_model import FilterMode, QueueModel, QueueRow, SortMode
    from tui.model.sync_plan_model import SyncPlanModel
    from tui.model.workers_model import WorkerRow, WorkersModel


_FILTER_CYCLE: tuple[FilterMode, ...] = ("all", "open", "ready", "reviewed", "terminal")
_SORT_CYCLE: tuple[SortMode, ...] = ("fifo", "newest", "repo")
_PARALLEL_CYCLE: tuple[int, ...] = (1, 2, 4, 8)


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
        Binding("R", "run_selected", "run-selected"),
        Binding("space", "toggle_select", "select"),
        Binding("p", "cycle_parallel", "parallel"),
        Binding("a", "pick_agent", "agent"),
        Binding("plus", "add_pr", "add-pr"),
        Binding("b", "repos", "repos"),
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
        self._worker_script = worker_script
        self._repos_dir: Path | None = repos_dir
        self._current_agent: str = agent
        self._filter_mode: FilterMode = "all"
        self._sort_mode: SortMode = "fifo"
        self._model: QueueModel | None = None
        self._plan_model: SyncPlanModel | None = None
        self._workers_model: WorkersModel | None = None
        self._rows_by_url: dict[str, QueueRow] = {}
        self._workers_by_url: dict[str, WorkerRow] = {}
        self._sync_proc: asyncio.subprocess.Process | None = None
        self._sync_task: asyncio.Task | None = None
        self._selection_order: list[str] = []
        self._review_workers: dict[str, asyncio.subprocess.Process] = {}
        self._review_tasks: dict[str, asyncio.Task] = {}
        self._parallel_n: int = 4
        self._batch_task: asyncio.Task | None = None
        self._add_pr_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with Horizontal(id="main"):
            yield QueueTable()
            yield DetailPane()
        yield WorkersPane()
        yield SyncPlanPane()
        yield LogPane()
        yield FooterBar()

    async def on_mount(self) -> None:
        from tui.model.queue_model import QueueModel
        from tui.model.sync_plan_model import SyncPlanModel
        from tui.model.workers_model import WorkersModel

        self._model = QueueModel(queue_path=self._queue_path)
        self._plan_model = SyncPlanModel(plan_path=self._plan_path)
        self._workers_model = WorkersModel(workers_dir=self._heartbeat_dir)
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=False,
            review_running=False,
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
        self._reload(force=True)
        self._reload_plan(force=True)
        self._reload_workers(force=True)
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
        # Prune disappeared URLs from selection.
        self._selection_order = [u for u in self._selection_order if u in self._rows_by_url]
        self.query_one(HeaderBar).update_snapshot(snapshot)
        self.query_one(QueueTable).load(
            snapshot,
            ascii_only=self._ascii_only,
            selected_order=list(self._selection_order),
        )
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
        self._refresh_detail()

    def _reload_plan(self, *, force: bool = False) -> None:
        if self._plan_model is None:
            return
        if not force and not self._plan_model.has_changed():
            return
        snapshot = self._plan_model.snapshot()
        self.query_one(SyncPlanPane).update_snapshot(snapshot, ascii_only=self._ascii_only)

    def _reload_workers(self, *, force: bool = False) -> None:
        if self._workers_model is None:
            return
        if not force and not self._workers_model.has_changed():
            return
        rows = self._workers_model.snapshot()
        self.query_one(WorkersPane).update_workers(rows, ascii_only=self._ascii_only)
        self._workers_by_url = {w.pr_url: w for w in rows if not w.is_stale}
        self._refresh_detail()

    def _maybe_reload(self) -> None:
        if self._model is not None and self._model.has_changed():
            self._reload(force=True)
        self._reload_plan()
        self._reload_workers()

    def _refresh_detail(self) -> None:
        table = self.query_one(QueueTable)
        url = table.selected_pr_url()
        row = self._rows_by_url.get(url) if url else None
        worker = self._workers_by_url.get(url) if url else None
        self.query_one(DetailPane).show(row, worker=worker)

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
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )

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
        if self._sync_proc is not None and self._sync_proc.returncode is None:
            return "sync"
        if self._batch_task is not None and not self._batch_task.done():
            return "batch"
        if self._add_pr_task is not None and not self._add_pr_task.done():
            return "add-pr"
        if self._review_workers:
            return "review"
        return None

    def action_sync(self) -> None:
        busy = self._busy_label()
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
        busy = self._busy_label()
        if busy in ("sync", "batch"):
            self.query_one(LogPane).write(f"(can't start review — {busy} already running)")
            return
        # Count live tasks, not workers: _review_tasks is populated immediately
        # at task creation, _review_workers only after the subprocess exec returns.
        # Using tasks closes the race where a rapid `r` press could exceed the cap.
        live_tasks = sum(1 for t in self._review_tasks.values() if not t.done())
        if live_tasks >= self._parallel_n:
            self.query_one(LogPane).write(
                f"(can't start review — parallel cap reached ({self._parallel_n}))"
            )
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
        if pr_url in self._review_tasks and not self._review_tasks[pr_url].done():
            self.query_one(LogPane).write(f"(review already running for {pr_url})")
            return
        task = asyncio.create_task(self._run_review(pr_url))
        self._review_tasks[pr_url] = task
        task.add_done_callback(self._on_review_task_done)

    def action_toggle_select(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            return
        if pr_url in self._selection_order:
            self._selection_order.remove(pr_url)
        else:
            self._selection_order.append(pr_url)
        self._reload(force=True)

    def action_cycle_parallel(self) -> None:
        try:
            idx = _PARALLEL_CYCLE.index(self._parallel_n)
        except ValueError:
            idx = 0
        self._parallel_n = _PARALLEL_CYCLE[(idx + 1) % len(_PARALLEL_CYCLE)]
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )

    def action_run_selected(self) -> None:
        busy = self._busy_label()
        if busy is not None:
            self.query_one(LogPane).write(f"(can't start batch — {busy} already running)")
            return
        if not self._selection_order:
            self.query_one(LogPane).write("(no rows selected — press `space` on rows to select)")
            return
        ready: list[str] = []
        skipped: list[str] = []
        log_pane = self.query_one(LogPane)
        for url in list(self._selection_order):
            row = self._rows_by_url.get(url)
            if row is None or not row.ready_for_review:
                log_pane.write(f"(skipping {url} — not ready)")
                skipped.append(url)
                continue
            ready.append(url)
        if not ready:
            log_pane.write("(no eligible rows in selection)")
            return
        log_pane.write(f"(batch start — {len(ready)} rows, parallel={self._parallel_n})")
        self._batch_task = asyncio.create_task(self._run_batch(ready, skipped))
        self._batch_task.add_done_callback(self._on_batch_task_done)

    async def _run_batch(self, urls: list[str], skipped: list[str] | None = None) -> None:
        skipped = list(skipped or [])
        outcomes: list[dict] = []
        # Seed outcomes with skipped rows so the recap surfaces them too.
        for url in skipped:
            outcomes.append({
                "pr_url": url, "rc": None,
                "last_line": "not ready", "outcome": "skipped",
            })

        queue: list[str] = list(urls)
        inflight: dict[asyncio.Task, str] = {}

        def _start_next() -> None:
            while queue and len(inflight) < self._parallel_n:
                url = queue.pop(0)
                t = asyncio.create_task(self._run_review(url))
                self._review_tasks[url] = t
                t.add_done_callback(self._on_review_task_done)
                inflight[t] = url

        _start_next()
        while inflight:
            done, _pending = await asyncio.wait(
                set(inflight.keys()), return_when=asyncio.FIRST_COMPLETED,
            )
            for t in done:
                url = inflight.pop(t)
                try:
                    result = t.result()
                except BaseException as exc:  # CancelledError or anything else
                    result = {"pr_url": url, "rc": None,
                              "last_line": repr(exc), "outcome": "crashed"}
                if isinstance(result, dict):
                    outcomes.append(result)
                else:
                    outcomes.append({"pr_url": url, "rc": None,
                                     "last_line": "unknown", "outcome": "crashed"})
            _start_next()

        log_pane = self.query_one(LogPane)
        log_pane.write(f"(batch done — {len(urls)} rows)")
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=False,
            review_running=False,
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
        self._reload(force=True)

        # Push the recap modal so the user sees per-row outcomes without
        # having to scroll the LogPane. Dismissable via escape/enter/q.
        if outcomes:
            from tui.screens.recap_screen import RecapScreen
            self.push_screen(RecapScreen(outcomes=outcomes, ascii_only=self._ascii_only))

    def _on_batch_task_done(self, task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self.query_one(LogPane).write(f"(batch crashed: {exc!r})")
            except Exception:
                pass
        self._batch_task = None

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
                self.query_one(FooterBar).update_status(
                    self._filter_mode, self._sort_mode,
                    sync_running=False,
                    review_running=bool(self._review_workers),
                    selected_count=len(self._selection_order),
                    parallel_n=self._parallel_n,
                    agent=self._current_agent,
                )
            except Exception:
                pass
            # _review_workers is popped by _run_review's finally on every exit
            # path — no manual cleanup needed here.

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
                    self._filter_mode, self._sort_mode,
                    sync_running=False,
                    review_running=bool(self._review_workers),
                    selected_count=len(self._selection_order),
                    parallel_n=self._parallel_n,
                    agent=self._current_agent,
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
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=True,
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
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
            self.query_one(FooterBar).update_status(
                self._filter_mode, self._sort_mode,
                sync_running=False,
                review_running=bool(self._review_workers),
                selected_count=len(self._selection_order),
                parallel_n=self._parallel_n,
                agent=self._current_agent,
            )
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
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=False,
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
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

    async def _run_review(self, pr_url: str) -> dict:
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
        log_pane.write(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            log_pane.write(f"(error: {exc})")
            self.query_one(FooterBar).update_status(
                self._filter_mode, self._sort_mode,
                sync_running=False,
                review_running=bool(self._review_workers),
                selected_count=len(self._selection_order),
                parallel_n=self._parallel_n,
                agent=self._current_agent,
            )
            return {"pr_url": pr_url, "rc": None,
                    "last_line": f"spawn error: {exc}",
                    "outcome": "spawn-error"}
        self._review_workers[pr_url] = proc
        self.query_one(FooterBar).update_status(
            self._filter_mode, self._sort_mode,
            sync_running=False,
            review_running=bool(self._review_workers),
            selected_count=len(self._selection_order),
            parallel_n=self._parallel_n,
            agent=self._current_agent,
        )
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
            self.query_one(FooterBar).update_status(
                self._filter_mode, self._sort_mode,
                sync_running=False,
                review_running=bool(self._review_workers),
                selected_count=len(self._selection_order),
                parallel_n=self._parallel_n,
                agent=self._current_agent,
            )
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
