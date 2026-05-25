from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

WorkStatus = Literal["queued", "running", "done", "failed", "skipped"]
WorkAction = Literal["sync", "sync+review", "review"]


@dataclass(frozen=True)
class PrWorkState:
    status: WorkStatus
    action: WorkAction
    message: str = ""


class WorkQueueModel:
    """Per-PR work state for the simplified TUI queue (one PR at a time)."""

    def __init__(self) -> None:
        self._states: dict[str, PrWorkState] = {}
        self._global_mode: str | None = None

    def set_global_mode(self, mode: str | None) -> None:
        self._global_mode = mode

    @property
    def global_mode(self) -> str | None:
        return self._global_mode

    def set(
        self,
        pr_url: str,
        status: WorkStatus,
        action: WorkAction,
        *,
        message: str = "",
    ) -> None:
        self._states[pr_url] = PrWorkState(status=status, action=action, message=message)

    def get(self, pr_url: str) -> PrWorkState | None:
        return self._states.get(pr_url)

    def all_states(self) -> dict[str, PrWorkState]:
        return dict(self._states)

    def clear(self) -> None:
        self._states.clear()
        self._global_mode = None

    def format_cell(self, pr_url: str) -> str | None:
        state = self._states.get(pr_url)
        if state is None:
            return None
        return format_work_cell(state)


def format_work_cell(state: PrWorkState) -> str:
    label = {
        "queued": "queued",
        "running": "running",
        "done": "done",
        "failed": "failed",
        "skipped": "skipped",
    }[state.status]
    text = f"{label} ({state.action})"
    if state.message:
        text = f"{text}: {state.message}"
    return text[:26]
