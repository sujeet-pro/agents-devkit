from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import OptionList, Static
from textual.widgets.option_list import Option

from tui.model.queue_model import TERMINAL_STATUSES as _TERMINAL_STATUSES

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


_ALL_ACTIONS: tuple[tuple[str, str], ...] = (
    ("open-pr", "Open PR in browser"),
    ("open-slack", "Open Slack thread"),
    ("update-pr", "Update PR status"),
    ("refresh-context", "Refresh supporting docs"),
    ("update-index", "Prepare review index"),
    ("review", "Full review"),
    ("rereview", "Re-run review (force)"),
    ("show-logs", "View review log"),
    ("merge-status", "Show merge readiness"),
    ("merge", "Merge PR (guarded)"),
)

# ---------------------------------------------------------------------------
# CLI adapter boundary
# ---------------------------------------------------------------------------
# Maps TUI action IDs to the corresponding key in the dict returned by
# `skills/adk-cli/scripts/pr.py::action_availability()`.
#
# Direct import of `action_availability` is intentionally avoided:
#   - `pr.py` lives in skills/adk-cli/scripts/ and does a sys.path dance.
#   - Importing it at TUI startup would pull in queue_io, pr_scan, and other
#     heavy CLI-side deps, risking circular imports and slow startup.
#
# TUI callers that want to honour CLI gates should:
#   1. Invoke `adk pr action-availability <pr_url>` as a subprocess.
#   2. Parse the JSON output.
#   3. Pass the result to `filter_by_availability()` below, then pass the
#      result dict as `availability=` to `PrActionScreen.__init__`.
#
# See `app.py::_fetch_action_availability()` for the async pre-fetch impl.
_TUI_TO_AVAILABILITY_KEY: dict[str, str | None] = {
    "open-pr":         "open_pr",
    "open-slack":      "open_slack",
    "update-pr":       "status_update",
    "refresh-context": "global_refresh",
    "update-index":    "re_review",     # closest gate; prepare is a pre-req for re_review
    "review":          "full_review",
    "rereview":        "re_review",
    "show-logs":       "view_log",
    "merge-status":    "merge",         # no exact CLI gate; use merge gate as proxy
    "merge":           "merge",
}


def filter_by_availability(
    actions: "list[tuple[str, str]]",
    availability: "dict | None",
) -> "list[tuple[str, str]]":
    """Filter an action list using a CLI ``action_availability`` result.

    When ``availability`` is ``None`` (e.g. subprocess unavailable or not yet
    fetched), returns ``actions`` unchanged.  Otherwise removes any action
    whose corresponding CLI gate has ``available=False``.

    Usage example::

        import json, subprocess
        avail_raw = subprocess.check_output(
            ["adk", "pr", "action-availability", pr_url], text=True
        )
        avail = json.loads(avail_raw)
        actions = filter_by_availability(_build_actions(row), avail)
    """
    if availability is None:
        return list(actions)
    avail_map: dict = availability.get("actions") or {}
    result: list[tuple[str, str]] = []
    for action_id, label in actions:
        cli_key = _TUI_TO_AVAILABILITY_KEY.get(action_id)
        if cli_key is None:
            # TUI-internal action (e.g. "select"); no CLI gate → always keep.
            result.append((action_id, label))
            continue
        gate = avail_map.get(cli_key) or {}
        if gate.get("available", True):
            result.append((action_id, label))
    return result


def _availability_hint(availability: "dict | None") -> str:
    """Return a short hint appended to the modal title when availability was fetched."""
    if availability is None:
        return ""
    return "  [live gates]"


def _build_actions(row: "QueueRow | None") -> list[tuple[str, str]]:
    """Return the context-filtered action list for the given PR row.

    When row is None (nothing selected), all actions are returned so the
    modal renders something sensible.  When row is provided, actions that
    cannot apply to the current state are omitted:

    - open-slack: hidden when no Slack permalink is stored
    - update-pr / refresh-context / update-index: hidden for terminal PRs
    - review: hidden when the PR is not ready_for_review or is terminal
    - rereview: hidden for terminal PRs
    - merge / merge-status: hidden for already-terminal PRs
    """
    if row is None:
        return list(_ALL_ACTIONS)

    is_terminal = row.status in _TERMINAL_STATUSES
    has_slack = bool(row.slack_permalink)
    can_review = row.ready_for_review

    result: list[tuple[str, str]] = []
    for action_id, label in _ALL_ACTIONS:
        if action_id == "open-slack" and not has_slack:
            continue
        if action_id in {"update-pr", "refresh-context", "update-index"} and is_terminal:
            continue
        if action_id == "review" and (is_terminal or not can_review):
            continue
        if action_id == "rereview" and is_terminal:
            continue
        if action_id in {"merge", "merge-status"} and is_terminal:
            continue
        result.append((action_id, label))

    return result


class PrActionScreen(ModalScreen[str | None]):
    """Per-PR action chooser. Arrow keys pick an action; enter confirms."""

    BINDINGS = [
        Binding("escape", "cancel", show=False),
        Binding("q", "cancel", show=False),
    ]

    DEFAULT_CSS = """
    PrActionScreen {
        align: center middle;
    }
    PrActionScreen > Container {
        width: 72;
        max-width: 90%;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    PrActionScreen Static {
        width: 100%;
        padding-bottom: 1;
    }
    PrActionScreen OptionList {
        width: 100%;
        height: auto;
        max-height: 14;
    }
    """

    def __init__(
        self,
        *,
        pr_label: str,
        row: "QueueRow | None" = None,
        availability: "dict | None" = None,
    ) -> None:
        super().__init__()
        self._pr_label = pr_label
        # Apply local state filtering first, then layer CLI availability gates on top.
        local_actions = _build_actions(row)
        self._actions = filter_by_availability(local_actions, availability)
        self._availability_hint = _availability_hint(availability)

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(
                f"{self._pr_label}{self._availability_hint}\n"
                "Choose an action with ↑/↓, press enter.",
                markup=False,
            )
            yield OptionList(*[
                Option(label, id=action_id)
                for action_id, label in self._actions
            ])

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        self.dismiss(str(event.option.id))

    def action_cancel(self) -> None:
        self.dismiss(None)
