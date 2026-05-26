from __future__ import annotations

from textual.widgets import Static


class QueueActionBar(Static):
    """One-row bar showing queue-wide keybind chips.

    Sits below QueueTable, above SplitterHandle.
    """

    def __init__(self) -> None:
        super().__init__("", markup=True)
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
        sync_label = (
            "[u]S[/u]ync all (running…)" if self._sync_running else "[u]S[/u]ync all"
        )
        work_label = (
            "[u]R[/u]eview all (running…)" if self._work_running else "[u]R[/u]eview all"
        )
        parts = [
            sync_label,
            work_label,
            "[+] Add PR",
            "[u]b[/u]rowse repos",
            "·",
            f"[u]f[/u]ilter:{self._filter_mode}",
            f"[K] sort:{self._sort_mode}",
            "[j/k] nav",
            "[tab] pane",
        ]
        if self._runner:
            parts.extend(["·", f"[u]t[/u] runner:{self._runner}"])
        self.update("  ".join(parts))
