from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueSnapshot


_PLATFORM_SHORT = {"bitbucket": "bb", "github": "gh", "mixed": "mix"}


class QueueStatusBar(Static):
    """One-row bar showing queue-wide counts + live indicators.

    Sits above QueueTable. Shows total/ready/in-review counts, per-stage
    counts, and live sync/worker indicators.
    """

    def __init__(self) -> None:
        super().__init__("", markup=False)
        self._snapshot: "QueueSnapshot | None" = None
        self._stage_counts: dict[str, int] = {}
        self._sync_running: bool = False
        self._workers_active: int = 0

    def update_state(
        self,
        snapshot: "QueueSnapshot",
        stage_counts: dict[str, int],
        *,
        sync_running: bool = False,
        workers_active: int = 0,
    ) -> None:
        self._snapshot = snapshot
        self._stage_counts = stage_counts
        self._sync_running = sync_running
        self._workers_active = workers_active
        self._refresh_text()

    def _refresh_text(self) -> None:
        snap = self._snapshot
        if snap is None:
            self.update("")
            return

        width = self.size.width if self.size.width > 0 else 120
        if width >= 100:
            platform = snap.platform_summary
            stats = f"total:{snap.total} ready:{snap.ready_count} in-review:{snap.in_review_count}/4"
        else:
            platform = _PLATFORM_SHORT.get(snap.platform_summary, snap.platform_summary[:3])
            stats = f"q:{snap.total} r:{snap.ready_count} rev:{snap.in_review_count}/4"

        sc = self._stage_counts
        if sc:
            stage_part = (
                f"Refresh:{sc.get('refresh', 0)}"
                f" Index:{sc.get('index', 0)}"
                f" Review:{sc.get('review', 0)}"
                f" Resolve:{sc.get('resolve', 0)}"
                f" Ready:{sc.get('ready', 0)}"
                f" Done:{sc.get('done', 0)}"
                "   [,/.] cycle stages"
            )
        else:
            stage_part = ""

        parts = [stats, platform]
        if stage_part:
            parts.append(stage_part)
        if self._sync_running:
            parts.append("sync running …")
        if self._workers_active > 0:
            parts.append(f"{self._workers_active} worker{'s' if self._workers_active != 1 else ''} active")

        self.update("  ·  ".join(parts))
