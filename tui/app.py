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
from textual.containers import Container
from textual.widgets import TabbedContent, TabPane

from tui.model.prefs import (
    ADJUST_STEP,
    LayoutPrefs,
    MAX_SPLIT_PERCENT,
    MIN_SPLIT_PERCENT,
    load_prefs,
    save_prefs,
    toggle_direction,
)
from tui.widgets.detail_pane import TabbedDetailPane
from tui.widgets.footer_bar import FooterBar
from tui.widgets.header_bar import HeaderBar
from tui.widgets.help_screen import HelpScreen
from tui.widgets.queue_table import QueueTable
from tui.widgets.splitter_handle import SplitterHandle

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

# Stage tab IDs and their display order for action_cycle_stage_tab.
_STAGE_TAB_IDS: tuple[str, ...] = (
    "stage-all", "stage-refresh", "stage-index", "stage-review",
    "stage-resolve", "stage-ready", "stage-done",
)


def _configured_runner(default: str = "claude") -> str:
    import sys as _sys
    _lib = Path(__file__).resolve().parents[1] / "scripts" / "lib"
    if str(_lib) not in _sys.path:
        _sys.path.insert(0, str(_lib))
    from adk_home import adk_config_home  # noqa: E402
    cfg_path = adk_config_home() / "adk-cli.json5"
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


def _stage_filter_pred(tab_id: str):
    """Return a predicate ``(task_status: str) -> bool`` for the given stage tab,
    or None if no filtering is needed (All tab)."""
    if tab_id == "stage-all":
        return None
    if tab_id == "stage-refresh":
        statuses = frozenset({"queued_for_sync", "syncing"})
        return lambda s: s in statuses
    if tab_id == "stage-index":
        statuses = frozenset({"queued_for_index", "indexing"})
        return lambda s: s in statuses
    if tab_id == "stage-review":
        statuses = frozenset({"reviewing", "ready_to_act"})
        return lambda s: s in statuses
    if tab_id == "stage-resolve":
        statuses = frozenset({"reviewed", "comments"})
        return lambda s: s in statuses
    if tab_id == "stage-ready":
        statuses = frozenset({"ready_to_merge"})
        return lambda s: s in statuses
    if tab_id == "stage-done":
        return lambda s: s.startswith("merged")
    return None


def _compute_stage_counts(rows_by_url: "dict[str, QueueRow]") -> dict[str, int]:
    """Compute per-stage row counts from all (unfiltered) rows."""
    from tui.model.pr_status import derive_task_status

    counts: dict[str, int] = {
        "refresh": 0, "index": 0, "review": 0,
        "resolve": 0, "ready": 0, "done": 0,
    }
    refresh_s = frozenset({"queued_for_sync", "syncing"})
    index_s   = frozenset({"queued_for_index", "indexing"})
    review_s  = frozenset({"reviewing", "ready_to_act"})
    resolve_s = frozenset({"reviewed", "comments"})
    ready_s   = frozenset({"ready_to_merge"})

    for row in rows_by_url.values():
        ts = derive_task_status(row, None)
        if ts in refresh_s:
            counts["refresh"] += 1
        elif ts in index_s:
            counts["index"] += 1
        elif ts in review_s:
            counts["review"] += 1
        elif ts in resolve_s:
            counts["resolve"] += 1
        elif ts in ready_s:
            counts["ready"] += 1
        elif ts.startswith("merged"):
            counts["done"] += 1
    return counts


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
        Binding("K", "cycle_sort", "sort"),
        Binding("1", "select_tab_overview", "tab:overview"),
        Binding("2", "select_tab_review", "tab:review"),
        Binding("3", "select_tab_comments", "tab:comments"),
        Binding("4", "select_tab_diff", "tab:diff"),
        Binding("5", "select_tab_activity", "tab:activity"),
        Binding("pagedown", "scroll_tab_down", show=False),
        Binding("pageup", "scroll_tab_up", show=False),
        Binding("J", "scroll_tab_line_down", show=False),
        Binding("n", "next_comment", show=False),
        Binding("N", "prev_comment", show=False),
        Binding("S", "sync_pr", "Sync PR"),
        Binding("R", "sync_review_pr", "Sync+Review"),
        Binding("s", "sync_all", "Sync all"),
        Binding("A", "sync_review_all", "Sync+Review all"),
        Binding("l", "show_logs", "logs"),
        Binding("L", "show_run_logs", "run-logs"),
        Binding("enter", "pr_actions", "actions"),
        Binding("a", "approve_pr", "approve"),
        Binding("v", "rereview", "re-review"),
        Binding("x", "refresh_cascade", "refresh"),
        Binding("m", "merge_status", "mergeable?"),
        Binding("M", "merge_pr", "merge"),
        Binding("r", "pick_agent", "runner"),
        Binding("plus", "add_pr", "add-pr"),
        Binding("b", "repos", "repos"),
        Binding("t", "cycle_theme", "theme"),
        Binding("tab", "focus_next_pane", "pane"),
        Binding("backslash", "toggle_layout_direction", "split:h/v"),
        Binding("left_square_bracket", "shrink_queue", show=False),
        Binding("right_square_bracket", "grow_queue", show=False),
        Binding("equals_sign", "reset_split", show=False),
        Binding("j", "cursor_down", show=False),
        Binding("k", "cursor_up", show=False),
        Binding("g", "cursor_home", show=False),
        Binding("G", "cursor_end", show=False),
        Binding("escape", "escape", show=False),
        # Secondary/hidden — accessible but not shown in primary footer.
        Binding("u", "update_pr", show=False),
        Binding("X", "refresh_context", show=False),
        Binding("I", "update_index", show=False),
        Binding("o", "open_links", show=False),
        Binding("O", "open_slack", show=False),
        Binding("period", "cycle_stage_tab_next", show=False),
        Binding("comma", "cycle_stage_tab_prev", show=False),
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

        self._layout_prefs: LayoutPrefs = load_prefs()
        self._active_stage_tab: str = "stage-all"

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with TabbedContent(id="stage-tabs"):
            yield TabPane("All",     id="stage-all")
            yield TabPane("Refresh", id="stage-refresh")
            yield TabPane("Index",   id="stage-index")
            yield TabPane("Review",  id="stage-review")
            yield TabPane("Resolve", id="stage-resolve")
            yield TabPane("Ready",   id="stage-ready")
            yield TabPane("Done",    id="stage-done")
        with Container(id="main"):
            yield QueueTable()
            yield SplitterHandle(ascii_only=self._ascii_only)
            yield TabbedDetailPane()
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
            self._log(
                f"(reattached: {n_existing} existing worker"
                f"{'' if n_existing == 1 else 's'} from heartbeat dir)"
            )
        self.set_interval(self.poll_interval, self._maybe_reload)
        self._apply_layout()

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

    def _activity(self):
        """Shorthand: the live ActivityPane (inside the detail tabs)."""
        if not self.screen_stack:
            return None
        try:
            return self._default_query(TabbedDetailPane).activity_pane()
        except Exception:
            return None

    def _log(self, text: str) -> None:
        """Append a line to the Activity tab's log section."""
        ap = self._activity()
        if ap is not None:
            ap.write(text)

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
            layout_direction=self._layout_prefs.direction,
            split_percent=self._layout_prefs.split_percent,
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

        # Apply stage filter on top of the existing filter_mode snapshot.
        stage_pred = _stage_filter_pred(self._active_stage_tab)
        if stage_pred is not None:
            from tui.model.pr_status import derive_task_status
            filtered_rows = [
                r for r in snapshot.rows
                if stage_pred(derive_task_status(r, None))
            ]
            from dataclasses import replace as _dc_replace
            snapshot = _dc_replace(snapshot, rows=filtered_rows)

        header = self._default_query(HeaderBar)
        header.update_snapshot(
            snapshot,
            operations=self._operations_summary,
            runner=self._current_agent,
        )
        # Compute per-stage counts for the header's second line.
        header.update_stage_counts(_compute_stage_counts(self._rows_by_url))

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
        ap = self._activity()
        if ap is not None:
            ap.update_plan(snapshot, ascii_only=self._ascii_only)

    def _reload_workers(self, *, force: bool = False) -> None:
        if self._workers_model is None:
            return
        if not self.screen_stack:
            return
        if not force and not self._workers_model.has_changed():
            return
        rows = self._workers_model.snapshot()
        ap = self._activity()
        if ap is not None:
            ap.update_workers(rows, ascii_only=self._ascii_only)
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
        ap = self._activity()
        if ap is not None:
            ap.update_runs(rows)
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

    def on_resize(self, event) -> None:
        # Re-apply on resize so percentage units re-resolve cleanly.
        self._apply_layout()

    def _apply_layout(self) -> None:
        """Apply the user's chosen split direction + ratio to the live widgets.

        Direction "horizontal" → queue on top, tabs below (top/bottom split).
        Direction "vertical"   → queue on left, tabs on right (left/right split).
        Width / height percentages come from ``self._layout_prefs.split_percent``
        (queue's share); the detail-tabs pane gets the remainder.

        Uses ``fr`` units so the 1-cell ``SplitterHandle`` between the two
        panes stays at a fixed size and the queue/tabs split the remaining
        space at the user's chosen ratio.
        """
        if not self.screen_stack:
            return
        try:
            main = self._default_query_id("#main")
            table = self._default_query(QueueTable)
            tabs = self._default_query(TabbedDetailPane)
            splitter = self._default_query(SplitterHandle)
        except Exception:
            return

        prefs = self._layout_prefs
        queue_share = max(MIN_SPLIT_PERCENT, min(MAX_SPLIT_PERCENT, int(prefs.split_percent)))
        tabs_share = 100 - queue_share

        if prefs.direction == "vertical":
            # Side-by-side (queue left, tabs right).
            main.styles.layout = "horizontal"
            table.styles.width = f"{queue_share}fr"
            table.styles.height = "1fr"
            splitter.styles.width = 1
            splitter.styles.height = "1fr"
            tabs.styles.width = f"{tabs_share}fr"
            tabs.styles.height = "1fr"
        else:
            # Stacked (queue top, tabs below) — the default.
            main.styles.layout = "vertical"
            table.styles.height = f"{queue_share}fr"
            table.styles.width = "1fr"
            splitter.styles.height = 1
            splitter.styles.width = "1fr"
            tabs.styles.height = f"{tabs_share}fr"
            tabs.styles.width = "1fr"

        splitter.set_direction(prefs.direction)

    def _default_query_id(self, selector: str):
        """Same as _default_query but takes a CSS selector string instead of
        a widget type. Used for #main / #foo lookups during layout apply."""
        return self.screen_stack[0].query_one(selector)

    def _persist_layout_prefs(self) -> None:
        try:
            save_prefs(self._layout_prefs)
        except Exception:
            # Persistence is best-effort; never block the UI on a config write.
            pass

    def _notify_layout(self, message: str) -> None:
        self._log(message)
        self._update_footer()

    # --- layout user actions ---

    def action_toggle_layout_direction(self) -> None:
        new = toggle_direction(self._layout_prefs.direction)
        self._layout_prefs = LayoutPrefs(
            direction=new, split_percent=self._layout_prefs.split_percent
        ).normalised()
        self._apply_layout()
        self._persist_layout_prefs()
        self._notify_layout(f"(layout: {new} · {self._layout_prefs.split_percent}/100)")

    def action_shrink_queue(self) -> None:
        new_pct = max(MIN_SPLIT_PERCENT, self._layout_prefs.split_percent - ADJUST_STEP)
        if new_pct == self._layout_prefs.split_percent:
            self._notify_layout(f"(split at min {MIN_SPLIT_PERCENT}%)")
            return
        self._layout_prefs = LayoutPrefs(
            direction=self._layout_prefs.direction, split_percent=new_pct
        ).normalised()
        self._apply_layout()
        self._persist_layout_prefs()
        self._notify_layout(f"(layout: {self._layout_prefs.direction} · {new_pct}/100)")

    def action_grow_queue(self) -> None:
        new_pct = min(MAX_SPLIT_PERCENT, self._layout_prefs.split_percent + ADJUST_STEP)
        if new_pct == self._layout_prefs.split_percent:
            self._notify_layout(f"(split at max {MAX_SPLIT_PERCENT}%)")
            return
        self._layout_prefs = LayoutPrefs(
            direction=self._layout_prefs.direction, split_percent=new_pct
        ).normalised()
        self._apply_layout()
        self._persist_layout_prefs()
        self._notify_layout(f"(layout: {self._layout_prefs.direction} · {new_pct}/100)")

    def action_reset_split(self) -> None:
        self._layout_prefs = LayoutPrefs(
            direction=self._layout_prefs.direction, split_percent=50
        ).normalised()
        self._apply_layout()
        self._persist_layout_prefs()
        self._notify_layout(f"(layout: {self._layout_prefs.direction} · 50/50)")

    # --- mouse-drag splitter ---

    def on_splitter_handle_dragged(self, event: SplitterHandle.Dragged) -> None:
        """Translate a mouse-drag delta into a new split percentage.

        In horizontal layout the user drags up/down → vertical pixels move
        the boundary; in vertical layout left/right → horizontal pixels.
        The percent is recomputed as ``current ± (delta / axis_size * 100)``
        and clamped to [MIN, MAX]; layout is re-applied live so the user
        sees the panes resize in real time. Persistence to disk waits for
        :class:`SplitterHandle.Released` to avoid one write per pixel.
        """
        if not self.screen_stack:
            return
        try:
            main = self._default_query_id("#main")
        except Exception:
            return

        direction = self._layout_prefs.direction
        if direction == "horizontal":
            axis_size = main.size.height
            delta = event.delta_y
        else:
            axis_size = main.size.width
            delta = event.delta_x

        if axis_size <= 1 or delta == 0:
            return

        pct_delta = (delta / axis_size) * 100.0
        new_pct = int(round(self._layout_prefs.split_percent + pct_delta))
        new_pct = max(MIN_SPLIT_PERCENT, min(MAX_SPLIT_PERCENT, new_pct))
        if new_pct == self._layout_prefs.split_percent:
            return

        self._layout_prefs = LayoutPrefs(
            direction=direction, split_percent=new_pct
        ).normalised()
        self._apply_layout()
        self._update_footer()

    def on_splitter_handle_released(self, event: SplitterHandle.Released) -> None:  # noqa: ARG002
        """Drag ended — persist the final ratio + narrate the result."""
        self._persist_layout_prefs()
        self._notify_layout(
            f"(layout: {self._layout_prefs.direction} · "
            f"{self._layout_prefs.split_percent}/{100 - self._layout_prefs.split_percent})"
        )

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
            self._log("(no row selected)")
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

    # --- stage tab handling ---

    def on_tabbed_content_tab_activated(self, event) -> None:
        """Sync the active stage tab to the queue filter when the stage-tabs
        TabbedContent fires TabActivated."""
        tab_id = str(event.tab.id) if event.tab else ""
        if not tab_id.startswith("stage-"):
            return
        self._apply_stage_filter(tab_id)

    def _apply_stage_filter(self, tab_id: str) -> None:
        """Set the active stage filter and reload the queue table."""
        self._active_stage_tab = tab_id
        self._reload(force=True)

    def action_cycle_stage_tab_next(self) -> None:
        """Advance to the next stage tab."""
        idx = _STAGE_TAB_IDS.index(self._active_stage_tab) if self._active_stage_tab in _STAGE_TAB_IDS else 0
        next_id = _STAGE_TAB_IDS[(idx + 1) % len(_STAGE_TAB_IDS)]
        self._set_stage_tab(next_id)

    def action_cycle_stage_tab_prev(self) -> None:
        """Go back to the previous stage tab."""
        idx = _STAGE_TAB_IDS.index(self._active_stage_tab) if self._active_stage_tab in _STAGE_TAB_IDS else 0
        prev_id = _STAGE_TAB_IDS[(idx - 1) % len(_STAGE_TAB_IDS)]
        self._set_stage_tab(prev_id)

    def _set_stage_tab(self, tab_id: str) -> None:
        """Activate a stage tab by ID, both in the widget and in the filter."""
        self._active_stage_tab = tab_id
        if not self.screen_stack:
            return
        try:
            tc = self._default_query_id("#stage-tabs")
            tc.active = tab_id
        except Exception:
            pass
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
        self._log(f"(theme: {new_theme})")

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
        self._default_query(HeaderBar).update_runner(self._current_agent)

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
            self._log(f"(can't add PR — {busy} already running)")
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
        adk = self._resolve_adk_bin()
        cmd: list[str] = [str(adk), "pr-queue", "add", text, "-y"]
        if self._queue_path is not None:
            cmd += ["--queue", str(self._queue_path)]
        self._log(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self._log(f"(error: {exc})")
            return
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            self._log(line.decode(errors="replace").rstrip("\n"))
        rc = await proc.wait()
        self._log(f"(pr-queue add exited rc={rc})")
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
            self._log("(Sync all already running — wait or quit and restart)")
            return
        if busy is not None:
            self._log(f"(can't start Sync all — {busy} already running)")
            return
        self._sync_task = asyncio.create_task(self._run_sync())
        self._sync_task.add_done_callback(self._on_sync_task_done)

    def action_sync_pr(self) -> None:
        pr_url = self._selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        busy = self._busy_label()
        if busy is not None:
            self._log(f"(can't start Sync PR — {busy} already running)")
            return
        self._work_task = asyncio.create_task(self._work_sync_pr(pr_url))
        self._work_task.add_done_callback(self._on_work_task_done)

    def action_sync_review_pr(self) -> None:
        pr_url = self._selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        busy = self._busy_label()
        if busy is not None:
            self._log(
                f"(can't start Sync + Review — {busy} already running)"
            )
            return
        self._work_task = asyncio.create_task(self._work_sync_review_pr(pr_url))
        self._work_task.add_done_callback(self._on_work_task_done)
        self._update_footer()

    def action_sync_review_all(self) -> None:
        busy = self._busy_label()
        if busy is not None:
            self._log(
                f"(can't start Sync + Review all — {busy} already running)"
            )
            return
        self._work_task = asyncio.create_task(self._work_sync_review_all())
        self._work_task.add_done_callback(self._on_work_task_done)
        self._update_footer()

    async def _work_sync_pr(self, pr_url: str) -> None:
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
            self._log(f"(Sync PR crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    async def _work_sync_review_pr(self, pr_url: str) -> None:
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
                self._log(f"(skipping review — row not ready: {pr_url})")
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
            self._log(f"(Sync + Review crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    async def _work_sync_review_all(self) -> None:
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
                self._log("(Sync + Review all — no eligible rows after sync)")
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
            self._log(f"(Sync + Review all done — {len(urls)} row(s))")
            if outcomes:
                from tui.screens.recap_screen import RecapScreen
                self.push_screen(RecapScreen(outcomes=outcomes, ascii_only=self._ascii_only))
        except BaseException as exc:
            self._log(f"(Sync + Review all crashed: {exc!r})")
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
                self._log(f"(work queue crashed: {exc!r})")
            except Exception:
                pass
        self._work_task = None
        self._work_queue.set_global_mode(None)
        self._update_footer()

    def action_update_pr(self) -> None:
        self._run_selected_pr_command("update PR", ["pr-queue", "update"])

    def action_refresh_context(self) -> None:
        self._run_selected_pr_command("refresh context", ["pr", "context-refresh"])

    def action_refresh_meta(self) -> None:
        """Refresh PR metadata + comments via `adk pr sync` — no review.

        Writes pr.json / pr-comments.json / diff.patch in the PR's task dir
        and updates the queue row's head_sha / comment activity. Cheap, safe
        to run on any selection."""
        self._run_selected_pr_command("refresh meta", ["pr", "sync"])

    def action_update_index(self) -> None:
        self._run_selected_pr_command("update index", ["pr-task", "prepare"])

    def action_merge_status(self) -> None:
        # --refresh re-pulls PR meta + comments from origin so the verdict
        # reflects live state, not the cached pr.json from the last review.
        self._run_selected_info_pr_command(
            "merge status", ["pr", "merge-status", "--refresh"]
        )

    def action_open_links(self) -> None:
        self._run_selected_pr_command("open PR", ["pr", "open"])

    def action_open_slack(self) -> None:
        self._run_selected_pr_command("open Slack", ["pr", "open", "--target", "slack"])

    def action_rereview(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        self._start_review_for_url(pr_url, force=True)

    def action_refresh_cascade(self) -> None:
        """Full refresh cascade: sync → re-index (if head changed) → re-review.

        Each phase is only triggered when necessary:
        - sync always runs first.
        - re-index only if head_sha changed since last index.
        - re-review only if re-indexed or comment_review is needed.
        Individual u/I/v bindings remain available for targeted use."""
        pr_url = self._selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        busy = self._busy_label()
        if busy is not None:
            self._log(f"(can't start refresh cascade — {busy} already running)")
            return
        self._work_task = asyncio.create_task(self._work_refresh_cascade(pr_url))
        self._work_task.add_done_callback(self._on_work_task_done)

    async def _work_refresh_cascade(self, pr_url: str) -> None:
        """Orchestrate sync → index → review for a single PR."""
        self._work_queue.set_global_mode("refresh-cascade")
        self._work_queue.set(pr_url, "running", "cascade:sync")
        self._reload(force=True)
        try:
            # Phase 1: sync metadata.
            rc = await self._run_adk_command("sync", ["pr", "sync", pr_url])
            if rc != 0:
                self._work_queue.set(pr_url, "failed", "cascade:sync", message=f"rc={rc}")
                return
            # Re-read queue row after sync to see if head changed.
            self._reload(force=True)
            row = self._rows_by_url.get(pr_url)
            head_sha = row.head_sha if row is not None else None
            last_indexed = getattr(row, "last_indexed_head_sha", None) if row is not None else None
            head_changed = head_sha is not None and head_sha != last_indexed

            if head_changed:
                # Phase 2: re-index.
                self._work_queue.set(pr_url, "running", "cascade:index")
                self._reload(force=True)
                rc = await self._run_adk_command("prepare index", ["pr-task", "prepare", pr_url])
                if rc != 0:
                    self._work_queue.set(pr_url, "failed", "cascade:index", message=f"rc={rc}")
                    return
                self._reload(force=True)

            # Phase 3: review if head was re-indexed or row needs re-review.
            needs_review = head_changed or (row is not None and row.ready_for_review)
            if needs_review:
                self._work_queue.set(pr_url, "running", "cascade:review")
                self._reload(force=True)
                result = await self._run_review(pr_url)
                outcome = result.get("outcome", "failed")
                self._work_queue.set(
                    pr_url,
                    "done" if outcome == "ok" else "failed",
                    "cascade:review",
                    message=str(result.get("last_line") or outcome)[:40],
                )
            else:
                self._work_queue.set(pr_url, "done", "cascade", message="up-to-date")
        except BaseException as exc:
            self._work_queue.set(pr_url, "failed", "cascade", message=repr(exc))
            self._log(f"(refresh cascade crashed: {exc!r})")
        finally:
            self._work_queue.set_global_mode(None)
            self._update_footer()
            self._reload(force=True)

    @work
    async def action_merge_pr(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        await self._confirm_and_merge(pr_url)

    def action_show_logs(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        worker = self._workers_by_url.get(pr_url)
        log_path = worker.log_path if worker is not None else None
        label = "active worker"
        if not log_path:
            log_path = self._latest_result_log_for_pr(pr_url)
            label = "latest review result"
        if not log_path:
            self._log(f"(no log found for {pr_url})")
            return
        self._write_log_tail(log_path, label=label, max_lines=120)

    def action_show_run_logs(self) -> None:
        if not self._run_rows:
            self._log("(no run logs found)")
            return
        run = self._run_rows[0]
        self._log(f"(run logs: {run.run_id})")

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
            self._log("(latest run has no log paths yet)")

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
            self._log(f"(review already running for {pr_url})")
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
                self._log(f"(review crashed: {exc!r})")
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
                self._log(f"(sync crashed: {exc!r})")
            except Exception:
                pass
            self._sync_proc = None
        self._update_footer()

    def _run_selected_pr_command(self, label: str, prefix: list[str]) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        self._run_pr_command(label, prefix, pr_url)

    def _run_pr_command(self, label: str, prefix: list[str], pr_url: str) -> None:
        task = asyncio.create_task(self._run_adk_command(label, [*prefix, pr_url]))
        task.add_done_callback(lambda t: self._on_background_action_done(label, t))

    def _run_info_pr_command(self, label: str, prefix: list[str], pr_url: str) -> None:
        """Like _run_pr_command but routes output to an InfoScreen instead of ActivityPane log."""
        task = asyncio.create_task(self._run_info_adk_command(label, [*prefix, pr_url]))
        task.add_done_callback(lambda t: self._on_background_action_done(label, t))

    def _run_selected_info_pr_command(self, label: str, prefix: list[str]) -> None:
        """Like _run_selected_pr_command but routes output to an InfoScreen."""
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        self._run_info_pr_command(label, prefix, pr_url)

    def _on_background_action_done(self, label: str, task: asyncio.Task) -> None:
        try:
            exc = task.exception()
        except (asyncio.CancelledError, asyncio.InvalidStateError):
            return
        if exc is not None:
            try:
                self._log(f"({label} crashed: {exc!r})")
            except Exception:
                pass

    async def _run_adk_command(self, label: str, args: list[str]) -> int:
        adk = self._resolve_adk_bin()
        if self._queue_path is not None and args and args[0] in {"pr-queue", "pr"}:
            cmd = [str(adk), args[0], "--queue", str(self._queue_path), *args[1:]]
        elif self._queue_path is not None and args[:2] == ["pr-task", "prepare"]:
            cmd = [str(adk), *args, "--queue", str(self._queue_path)]
        else:
            cmd = [str(adk), *args]
        self._log(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self._log(f"({label} error: {exc})")
            return 2
        assert proc.stdout is not None
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            self._log(line.decode(errors="replace").rstrip("\n"))
        rc = await proc.wait()
        self._log(f"({label} exited rc={rc})")
        self._reload(force=True)
        self._reload_runs(force=True)
        self._reload_workers(force=True)
        return rc

    async def _run_info_adk_command(self, label: str, args: list[str]) -> int:
        """Like _run_adk_command, but collects output and displays it in an InfoScreen.

        The Activity log still receives the command line and the exit-code line so
        the activity record is preserved.  The actual command output goes to a
        dedicated modal panel the user can review at their own pace.
        """
        from tui.screens.info_screen import InfoScreen

        adk = self._resolve_adk_bin()
        if self._queue_path is not None and args and args[0] in {"pr-queue", "pr"}:
            cmd = [str(adk), args[0], "--queue", str(self._queue_path), *args[1:]]
        elif self._queue_path is not None and args[:2] == ["pr-task", "prepare"]:
            cmd = [str(adk), *args, "--queue", str(self._queue_path)]
        else:
            cmd = [str(adk), *args]
        self._log(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self._log(f"({label} error: {exc})")
            return 2
        assert proc.stdout is not None
        output_lines: list[str] = []
        while True:
            line = await proc.stdout.readline()
            if not line:
                break
            output_lines.append(line.decode(errors="replace").rstrip("\n"))
        rc = await proc.wait()
        self._log(f"({label} exited rc={rc})")
        self._reload(force=True)
        self._reload_runs(force=True)
        self._reload_workers(force=True)
        self.push_screen(InfoScreen(title=label, content="\n".join(output_lines), rc=rc))
        return rc

    async def _run_sync(self) -> None:
        queue_arg: list[str] = []
        if self._queue_path is not None:
            queue_arg = ["--queue", str(self._queue_path)]
        adk = self._resolve_adk_bin()
        cmd = [str(adk), "pr-sync", *queue_arg]
        self._log(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
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
            self._log(f"(error: {exc})")
            self._sync_proc = None
            self._update_footer()
            return
        self._update_footer()
        assert self._sync_proc.stdout is not None
        while True:
            line = await self._sync_proc.stdout.readline()
            if not line:
                break
            self._log(line.decode(errors="replace").rstrip("\n"))
        rc = await self._sync_proc.wait()
        self._log(f"(pr-sync exited rc={rc})")
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
        # P2.5: fallback for TUI-spawned reviews where no RunRow was written.
        try:
            from tui.model.queue_model import _PR_REVIEW_ROOT
            import sys as _sys
            _scripts = Path(__file__).resolve().parents[1] / "skills" / "adk-cli" / "scripts"
            if str(_scripts) not in _sys.path:
                _sys.path.insert(0, str(_scripts))
            import queue_io as _queue_io
            _host, _owner, repo, number = _queue_io.dedupe_key(pr_url)
            log_path = _PR_REVIEW_ROOT / f"{repo}_pr-{number}" / "review.log"
            if log_path.exists():
                return str(log_path)
        except Exception:
            pass
        return None

    def _write_log_tail(self, log_path: str, *, label: str, max_lines: int) -> None:
        path = Path(log_path).expanduser()
        if not path.exists():
            self._log(f"(log missing: {path})")
            return
        try:
            lines: deque[str] = deque(maxlen=max_lines)
            with path.open("r", encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    lines.append(line.rstrip("\n"))
        except OSError as exc:
            self._log(f"(log read error: {path}: {exc})")
            return
        self._log(f"(log: {label} — {path} — last {len(lines)} lines)")
        if not lines:
            self._log("(log is empty)")
            return
        for line in lines:
            self._log(line)

    def _resolve_worker_script(self) -> Path:
        if self._worker_script is not None:
            return self._worker_script
        return Path(__file__).resolve().parent / "worker.py"

    async def _run_review(self, pr_url: str, *, extra_worker_args: list[str] | None = None) -> dict:
        """Run one worker. Returns an outcome dict the batch driver collects
        for the end-of-run recap: `{pr_url, rc, last_line, outcome}` where
        outcome is `"ok"` (rc=0), `"failed"` (rc!=0), or `"spawn-error"` (the
        subprocess never started)."""
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
        self._log(f"$ {' '.join(shlex.quote(c) for c in cmd)}")
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
        except (FileNotFoundError, PermissionError, OSError) as exc:
            self._log(f"(error: {exc})")
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
                self._log(text)
                if text:
                    last_line = text
            rc = await proc.wait()
            self._log(f"(worker exited rc={rc})")
            return {"pr_url": pr_url, "rc": rc, "last_line": last_line,
                    "outcome": "ok" if rc == 0 else "failed"}
        finally:
            self._review_workers.pop(pr_url, None)
            self._update_footer()
            self._reload(force=True)

    # --- tab selection actions ---

    def action_select_tab_overview(self) -> None:
        self._select_detail_tab("tab-overview")

    def action_select_tab_review(self) -> None:
        self._select_detail_tab("tab-review")

    def action_select_tab_comments(self) -> None:
        self._select_detail_tab("tab-comments")

    def action_select_tab_diff(self) -> None:
        self._select_detail_tab("tab-diff")

    def action_select_tab_activity(self) -> None:
        self._select_detail_tab("tab-activity")

    # Maps each tab id → the VerticalScroll / ScrollableContainer that owns
    # its primary scroll state. Used by PageUp/PageDown to scroll the active
    # tab regardless of which widget inside it has focus.
    _TAB_SCROLL_ID = {
        "tab-overview": "#overview-scroll",
        "tab-review":   "#review-scroll",
        "tab-comments": "#comments-scroll",
        "tab-diff":     "#diff-scroll",  # right-pane diff content
    }

    # Maps each tab id → the selector that should receive focus when the
    # user switches to the tab. For most tabs that's the scroll container
    # (so arrows + page-keys scroll content). For Diff the file list takes
    # focus so arrow keys browse files; PageUp/PageDown still scroll the
    # right-side content via the _TAB_SCROLL_ID lookup above.
    _TAB_FOCUS_ID = {
        "tab-overview": "#overview-scroll",
        "tab-review":   "#review-scroll",
        "tab-comments": "#comments-scroll",
        "tab-diff":     "#diff-files-list",
    }

    def _select_detail_tab(self, tab_id: str) -> None:
        if not self.screen_stack:
            return
        pane = self._default_query(TabbedDetailPane)
        pane.select_tab(tab_id)
        # Focus the right widget for the tab so the user can interact
        # immediately (arrows + page-keys do the right thing).
        focus_selector = self._TAB_FOCUS_ID.get(tab_id)
        if focus_selector is None:
            return
        try:
            self._default_query_id(focus_selector).focus()
        except Exception:
            pass

    def _active_tab_scroll(self):
        """Return the VerticalScroll for the currently-active detail tab, or None."""
        if not self.screen_stack:
            return None
        try:
            pane = self._default_query(TabbedDetailPane)
            tabs = pane.query_one("#detail-tabs")
            active = getattr(tabs, "active", None) or "tab-overview"
        except Exception:
            return None
        selector = self._TAB_SCROLL_ID.get(active)
        if selector is None:
            return None
        try:
            return self._default_query_id(selector)
        except Exception:
            return None

    def action_scroll_tab_down(self) -> None:
        scroll = self._active_tab_scroll()
        if scroll is not None:
            scroll.scroll_page_down(animate=False)

    def action_scroll_tab_up(self) -> None:
        scroll = self._active_tab_scroll()
        if scroll is not None:
            scroll.scroll_page_up(animate=False)

    def action_scroll_tab_line_down(self) -> None:
        scroll = self._active_tab_scroll()
        if scroll is not None:
            scroll.scroll_down(animate=False)

    def _jump_comment(self, *, forward: bool) -> None:
        """Scroll the Comments tab to the next/previous comment divider.

        Each comment is separated by a markdown ``---`` rule, which Textual
        renders as a ``MarkdownHorizontalRule`` widget. We locate the rule
        nearest to (and on the requested side of) the current scroll offset
        and align the viewport so the next comment header lands at the top.
        Falls back to PageDown / PageUp when no rules are present (no
        comments, or active tab isn't a markdown tab).
        """
        scroll = self._active_tab_scroll()
        if scroll is None:
            return
        try:
            from textual.widgets._markdown import MarkdownHorizontalRule
        except Exception:
            MarkdownHorizontalRule = None  # type: ignore[assignment]
        rules: list = []
        if MarkdownHorizontalRule is not None:
            try:
                rules = list(scroll.query(MarkdownHorizontalRule))
            except Exception:
                rules = []
        if not rules:
            (scroll.scroll_page_down if forward else scroll.scroll_page_up)(animate=False)
            return

        positions: list[int] = []
        for rule in rules:
            try:
                # virtual_region is the widget's offset inside the scrollable
                # content; that's what we compare against scroll_y.
                positions.append(int(rule.virtual_region.y))
            except Exception:
                continue
        positions.sort()
        if not positions:
            (scroll.scroll_page_down if forward else scroll.scroll_page_up)(animate=False)
            return

        current = int(scroll.scroll_y)
        if forward:
            target = next((y for y in positions if y > current + 1), positions[-1])
        else:
            preceding = [y for y in positions if y < current - 1]
            target = preceding[-1] if preceding else positions[0]
        scroll.scroll_to(y=max(0, target - 1), animate=False)

    def action_next_comment(self) -> None:
        self._jump_comment(forward=True)

    def action_prev_comment(self) -> None:
        self._jump_comment(forward=False)

    def action_focus_next_pane(self) -> None:
        """Cycle focus: QueueTable → TabbedDetailPane → QueueTable."""
        if not self.screen_stack:
            return
        focused = self.focused
        queue = self._default_query(QueueTable)
        detail = self._default_query(TabbedDetailPane)
        if focused is queue or (focused is not None and focused in queue.query("*")):
            detail.focus()
        else:
            queue.focus()

    # --- approve action ---

    @work
    async def action_approve_pr(self) -> None:
        table = self.query_one(QueueTable)
        pr_url = table.selected_pr_url()
        if not pr_url:
            self._log("(no row selected)")
            return
        row = self._rows_by_url.get(pr_url)
        label = f"{row.repo}#{row.number}" if row is not None else pr_url
        from tui.screens.confirm_screen import ConfirmScreen
        ok = await self.push_screen_wait(ConfirmScreen(
            f"Approve this PR on its host platform?\n\n{label}\n{pr_url}\n\n"
            "This posts an approval via the platform API. Not done in auto mode.",
            yes_label="approve",
            no_label="cancel",
        ))
        if not ok:
            return
        self._run_pr_command("approve PR", ["pr", "approve", "--yes"], pr_url)

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
