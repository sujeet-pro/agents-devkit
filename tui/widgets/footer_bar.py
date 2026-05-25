from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


class FooterBar(Static):
    def __init__(self) -> None:
        super().__init__("", markup=False)

    def update_status(
        self,
        filter_mode: str,
        sort_mode: str,
        *,
        sync_all_running: bool = False,
        work_running: bool = False,
        agent: str | None = None,
        runner: str | None = None,
        row: "QueueRow | None" = None,  # noqa: ARG002 — kept for call-site compat
    ) -> None:
        runner_name = runner or agent

        parts = [
            "[?] help",
            f"[f] filter:{filter_mode}",
            f"[S] sort:{sort_mode}",
            "[j/k] nav",
            "[q] quit",
            "·",
            "[1] Sync PR",
            "[2] Sync+Review",
        ]

        if sync_all_running:
            parts.append("[s] Sync all (running…)")
        else:
            parts.append("[s] Sync all")

        if work_running:
            parts.append("[A] Sync+Review all (running…)")
        else:
            parts.append("[A] Sync+Review all")

        parts.extend([
            "·",
            "[enter] actions",
            "[a] runner",
        ])

        if runner_name:
            parts.append(f"runner:{runner_name}")

        self.update("  ".join(parts))
