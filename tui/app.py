from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal

from tui.widgets.detail_pane import DetailPane
from tui.widgets.footer_bar import FooterBar
from tui.widgets.header_bar import HeaderBar
from tui.widgets.help_screen import HelpScreen
from tui.widgets.queue_table import QueueTable

if TYPE_CHECKING:
    from tui.model.queue_model import FilterMode, QueueModel, QueueRow, SortMode


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
    ) -> None:
        super().__init__()
        self._queue_path = queue_path
        self._ascii_only = ascii_only
        self.poll_interval = poll_interval
        self._filter_mode: FilterMode = "all"
        self._sort_mode: SortMode = "fifo"
        self._model: QueueModel | None = None
        self._rows_by_url: dict[str, QueueRow] = {}

    def compose(self) -> ComposeResult:
        yield HeaderBar()
        with Horizontal(id="main"):
            yield QueueTable()
            yield DetailPane()
        yield FooterBar()

    async def on_mount(self) -> None:
        from tui.model.queue_model import QueueModel

        self._model = QueueModel(queue_path=self._queue_path)
        self.query_one(FooterBar).update_status(self._filter_mode, self._sort_mode)
        self._reload(force=True)
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

    def _maybe_reload(self) -> None:
        if self._model is None:
            return
        if self._model.has_changed():
            self._reload(force=True)

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
