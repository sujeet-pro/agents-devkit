"""TUI preferences — split direction and ratio.

The TUI lets the user choose how the queue / detail-tabs surface is split:

  * direction: "horizontal" (top/bottom, two stacked bands) or "vertical"
                (left/right, two side-by-side columns)
  * split_percent: how much of the terminal goes to the queue (1-99).
                   The detail-tabs surface gets the remainder.

Resolution order (highest priority first):

  1. ``$ADK_CONFIG_HOME/tui-prefs.json`` — runtime overrides written by the
     TUI when the user presses ``\\``, ``[``, ``]``, or ``=``.
  2. ``$ADK_CONFIG_HOME/adk-cli.json5`` under the ``tui:`` key — defaults
     the user can pin by hand for cross-machine config.
  3. Hardcoded defaults: ``horizontal`` direction, ``50`` percent.

Why a sidecar? Writing back to ``adk-cli.json5`` would lose comments and
trailing-comma JSON5 idioms. The sidecar keeps the hand-edited config file
untouched while still letting runtime tweaks persist.
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

_LIB_DIR = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_config_home  # noqa: E402


Direction = str  # "horizontal" | "vertical"
CommentsFilter = Literal["open", "all"]

DEFAULT_DIRECTION: Direction = "horizontal"
DEFAULT_SPLIT_PERCENT: int = 50
MIN_SPLIT_PERCENT: int = 15
MAX_SPLIT_PERCENT: int = 85
ADJUST_STEP: int = 5
DEFAULT_COMMENTS_FILTER: CommentsFilter = "open"


@dataclass
class LayoutPrefs:
    direction: Direction = DEFAULT_DIRECTION
    split_percent: int = DEFAULT_SPLIT_PERCENT
    comments_filter: CommentsFilter = DEFAULT_COMMENTS_FILTER

    def normalised(self) -> "LayoutPrefs":
        direction = self.direction if self.direction in ("horizontal", "vertical") else DEFAULT_DIRECTION
        sp = max(MIN_SPLIT_PERCENT, min(MAX_SPLIT_PERCENT, int(self.split_percent)))
        cf: CommentsFilter = self.comments_filter if self.comments_filter in ("open", "all") else DEFAULT_COMMENTS_FILTER
        return LayoutPrefs(direction=direction, split_percent=sp, comments_filter=cf)


def _prefs_path() -> Path:
    return adk_config_home() / "tui-prefs.json"


def _read_adk_cli_tui_section() -> dict:
    """Read the ``tui:`` section from adk-cli.json5 if present."""
    try:
        scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from config_io import get_adk_cli  # type: ignore  # noqa: E402

        node = get_adk_cli("tui", default={})
        return node if isinstance(node, dict) else {}
    except Exception:
        return {}


def _read_sidecar() -> dict:
    path = _prefs_path()
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return raw if isinstance(raw, dict) else {}


def load_prefs() -> LayoutPrefs:
    """Resolve the effective layout prefs, sidecar > adk-cli.json5 > defaults."""
    cli = _read_adk_cli_tui_section()
    sc = _read_sidecar()

    direction = (
        sc.get("layout")
        or sc.get("direction")
        or cli.get("layout")
        or cli.get("direction")
        or DEFAULT_DIRECTION
    )
    split_percent = (
        sc.get("split_percent")
        or cli.get("split_percent")
        or DEFAULT_SPLIT_PERCENT
    )
    try:
        split_percent = int(split_percent)
    except (TypeError, ValueError):
        split_percent = DEFAULT_SPLIT_PERCENT

    comments_filter = (
        sc.get("comments_filter")
        or cli.get("comments_filter")
        or DEFAULT_COMMENTS_FILTER
    )

    return LayoutPrefs(
        direction=direction,
        split_percent=split_percent,
        comments_filter=comments_filter,
    ).normalised()


def save_prefs(prefs: LayoutPrefs) -> None:
    """Persist the user's layout choice to the sidecar (best-effort)."""
    norm = prefs.normalised()
    path = _prefs_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        existing = _read_sidecar()
        existing["layout"] = norm.direction
        existing["split_percent"] = norm.split_percent
        existing["comments_filter"] = norm.comments_filter
        path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    except OSError:
        pass


def toggle_direction(direction: Direction) -> Direction:
    return "vertical" if direction == "horizontal" else "horizontal"
