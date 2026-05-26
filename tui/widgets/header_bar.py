from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueSnapshot


_PLATFORM_SHORT = {"bitbucket": "bb", "github": "gh", "mixed": "mix"}


class HeaderBar(Static):
    """Two-line header: queue stats · platform · ops · runner · clock (line 1)
    + stage counts (line 2).

    Adapts label width based on terminal width: narrow form drops vowels from
    'queue', 'ready', 'in-review'. The clock is always right-aligned."""

    def __init__(self) -> None:
        super().__init__("adk", markup=False)
        self._snapshot: "QueueSnapshot | None" = None
        self._operations: str | None = None
        self._runner: str | None = None
        self._stage_counts: dict[str, int] = {}

    def update_snapshot(
        self,
        snapshot: "QueueSnapshot",
        *,
        operations: str | None = None,
        runner: str | None = None,
    ) -> None:
        self._snapshot = snapshot
        self._operations = operations
        if runner is not None:
            self._runner = runner
        self._refresh()

    def update_runner(self, runner: str | None) -> None:
        self._runner = runner
        self._refresh()

    def update_stage_counts(self, counts: dict[str, int]) -> None:
        """Update the per-stage counts shown on the second header line."""
        self._stage_counts = counts
        self._refresh()

    def _refresh(self) -> None:
        snap = self._snapshot
        if snap is None:
            self.update("adk")
            return
        width = self.size.width if self.size.width > 0 else 120
        clock = datetime.now().strftime("%H:%M")

        if width >= 100:
            platform = snap.platform_summary
            stats = f"queue:{snap.total} ready:{snap.ready_count} in-review:{snap.in_review_count}/4"
        else:
            platform = _PLATFORM_SHORT.get(snap.platform_summary, snap.platform_summary[:3])
            stats = f"q:{snap.total} r:{snap.ready_count} rev:{snap.in_review_count}/4"

        parts = ["adk", stats, platform]
        if self._operations:
            parts.append(self._operations)
        if self._runner:
            parts.append(f"runner:{self._runner}")
        left = " · ".join(parts)

        # clock pinned right; subtract clock width + 4 spaces of breathing room
        pad = max(1, width - len(left) - len(clock) - 4)
        line1 = f"{left}{' ' * pad}{clock}"

        if self._stage_counts:
            sc = self._stage_counts
            stage_line = (
                f"  Refresh:{sc.get('refresh', 0)}"
                f" · Index:{sc.get('index', 0)}"
                f" · Review:{sc.get('review', 0)}"
                f" · Resolve:{sc.get('resolve', 0)}"
                f" · Ready:{sc.get('ready', 0)}"
                f" · Done:{sc.get('done', 0)}"
            )
            self.update(f"{line1}\n{stage_line}")
        else:
            self.update(line1)
