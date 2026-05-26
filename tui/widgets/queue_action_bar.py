from __future__ import annotations

from textual.widgets import Static


class QueueActionBar(Static):
    """One-row bar showing queue-wide keybind chips.

    Sits below QueueTable, above SplitterHandle.
    """

    def __init__(self) -> None:
        super().__init__("", markup=False)
        self._filter_mode: str = "all"
        self._sort_mode: str = "queue"
        self._sync_running: bool = False
        self._work_running: bool = False
        self._runner: str | None = None

    def update_state(
        self,
        filter_mode: str,
        sort_mode: str,
        *,
        sync_running: bool = False,
        work_running: bool = False,
        runner: str | None = None,
    ) -> None:
        self._filter_mode = filter_mode
        self._sort_mode = sort_mode
        self._sync_running = sync_running
        self._work_running = work_running
        self._runner = runner
        self._refresh_text()

    def _refresh_text(self) -> None:
        sync_label = "[s]Sync all (running…)" if self._sync_running else "[s]Sync all"
        work_label = "[A]Sync+Rev all (running…)" if self._work_running else "[A]Sync+Rev all"
        parts = [
            sync_label,
            work_label,
            "[+]Add PR",
            "[b]Repos",
            "·",
            f"[f]filter:{self._filter_mode}",
            f"[K]sort:{self._sort_mode}",
            "[j/k]nav",
            "[tab]pane",
        ]
        if self._runner:
            parts.extend(["·", f"[r]runner:{self._runner}"])
        self.update("  ".join(parts))
