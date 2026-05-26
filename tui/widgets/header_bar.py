from __future__ import annotations

from datetime import datetime

from textual.widgets import Static


class HeaderBar(Static):
    """Slim one-row header: adk title · runner · clock (right-aligned).

    Stats and stage counts have moved to QueueStatusBar.
    """

    def __init__(self) -> None:
        super().__init__("adk", markup=False)
        self._runner: str | None = None

    def update_snapshot(self, snapshot, *, operations=None, runner=None) -> None:
        if runner is not None:
            self._runner = runner
        self._refresh()

    def update_runner(self, runner: str | None) -> None:
        self._runner = runner
        self._refresh()

    def update_stage_counts(self, counts: dict[str, int]) -> None:
        pass

    def _refresh(self) -> None:
        width = self.size.width if self.size.width > 0 else 120
        clock = datetime.now().strftime("%H:%M")

        parts = ["adk"]
        if self._runner:
            parts.append(f"runner:{self._runner}")
        left = " · ".join(parts)

        pad = max(1, width - len(left) - len(clock) - 4)
        self.update(f"{left}{' ' * pad}{clock}")
