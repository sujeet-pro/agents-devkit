from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


class PRStatusBar(Static):
    """One-row bar showing the selected PR's headline.

    Sits below SplitterHandle, above TabbedDetailPane. Gives the user a
    persistent identifier for which PR they are reading — useful when the
    active tab is Diff or Comments and the queue is scrolled out of view.
    """

    def __init__(self) -> None:
        super().__init__("(no PR selected — pick one above)", markup=False)

    def update_pr(self, row: "QueueRow | None") -> None:
        if row is None:
            self.update("(no PR selected — pick one above)")
            return

        sha = (row.head_sha or "")[:7]
        base = row.target_branch or "main"
        label = f"{row.repo}#{row.number}"
        head_part = f"head {sha} → {base}" if sha else f"→ {base}"

        from tui.model.pr_status import derive_task_status
        status = derive_task_status(row, None)

        def _g(ts: "str | None") -> str:
            return "✓" if ts else "·"

        stages = (
            f"S={_g(row.last_synced_at)}"
            f" I={_g(row.last_indexed_at)}"
            f" R={_g(row.last_reviewed_at)}"
            f" V={_g(row.last_validated_at)}"
            f" P={_g(row.last_posted_at)}"
        )

        self.update(f"{label} · {head_part} · {status}   |  {stages}")
