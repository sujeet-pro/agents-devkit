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
        layout_direction: str | None = None,
        split_percent: int | None = None,
    ) -> None:
        runner_name = runner or agent

        parts = [
            "[?]help",
            f"[f]filter:{filter_mode}",
            f"[K]sort:{sort_mode}",
            "[j/k]nav",
            "[tab]pane",
            "[1-5]tab",
            "[pgup/pgdn]scroll",
        ]

        if layout_direction:
            short = "h" if layout_direction == "horizontal" else "v"
            pct = split_percent if split_percent is not None else 50
            parts.append(f"[\\]split:{short}{pct}")

        parts.extend(["·", "[S]Sync PR", "[R]Sync+Rev"])

        parts.append("[s]Sync all (running…)" if sync_all_running else "[s]Sync all")
        parts.append("[A]Sync+Rev all (running…)" if work_running else "[A]Sync+Rev all")

        parts.extend([
            "·",
            "[enter]act",
            "[a]pprove",
            "[v]re-review",
            "[x]refresh",
            "[m]ergeable?",
            "[M]erge",
            "[r]unner",
            "[q]quit",
        ])

        if runner_name:
            parts.append(f"runner:{runner_name}")

        self.update("  ".join(parts))
