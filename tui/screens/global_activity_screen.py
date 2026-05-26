from __future__ import annotations

import sys
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import RadioButton, RadioSet, Static

_ADK_REPO_LIB = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_ADK_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_ADK_REPO_LIB))

_MAX_LOG_LINES = 2000
_TAIL_BYTES = 64 * 1024


def _adk_data_home() -> Path:
    from config import adk_data_home  # noqa: E402
    return adk_data_home()


def _read_tail(path: Path, max_lines: int = _MAX_LOG_LINES) -> list[str]:
    if not path.exists():
        return []
    try:
        size = path.stat().st_size
        with path.open("r", encoding="utf-8", errors="replace") as fh:
            if size > _TAIL_BYTES:
                fh.seek(size - _TAIL_BYTES)
                fh.readline()  # discard potentially partial line
            lines = fh.read().splitlines()
        return lines[-max_lines:]
    except OSError:
        return []


def _latest_run_dir() -> Path | None:
    """Return the most-recently-modified run dir under pr-review-all-runs/."""
    runs_root = _adk_data_home() / "logs" / "pr-review-all-runs"
    if not runs_root.is_dir():
        return None
    try:
        dirs = sorted(runs_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        return dirs[0] if dirs else None
    except OSError:
        return None


def _load_log(source: str) -> str:
    """Load log lines for the given filter source."""
    data_home = _adk_data_home()
    if source == "pipeline":
        lines = _read_tail(data_home / "logs" / "pipeline.log")
        prefix = "[pipeline] "
    elif source == "sync":
        run_dir = _latest_run_dir()
        lines = _read_tail(run_dir / "pr-sync.log") if run_dir else []
        prefix = "[sync] "
    elif source == "review-all":
        run_dir = _latest_run_dir()
        lines = _read_tail(run_dir / "report.md") if run_dir else []
        prefix = "[review-all] "
    else:
        lines = []
        prefix = ""

    if not lines:
        return f"(no {source} log found)"
    tagged = [f"{prefix}{line}" for line in lines]
    return "\n".join(tagged)


_SOURCES = ("pipeline", "sync", "review-all")


class GlobalActivityScreen(ModalScreen[None]):
    """Full-screen RichLog modal for global pipeline + sync + review-all logs.

    Open with `L`. Filter by source via radio buttons at the top.
    Close with Escape or q.
    """

    BINDINGS = [
        Binding("escape", "dismiss", show=False),
        Binding("q", "dismiss", show=False),
    ]

    DEFAULT_CSS = """
    GlobalActivityScreen {
        align: center middle;
    }
    GlobalActivityScreen > Container {
        width: 95%;
        height: 85%;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    GlobalActivityScreen .gas-title {
        text-style: bold;
        padding-bottom: 1;
        width: 100%;
    }
    GlobalActivityScreen .gas-filter {
        height: 3;
        width: 100%;
        padding-bottom: 1;
    }
    GlobalActivityScreen VerticalScroll {
        width: 100%;
        height: 1fr;
    }
    GlobalActivityScreen Static.gas-body {
        width: 100%;
    }
    GlobalActivityScreen Static.gas-footer {
        padding-top: 1;
        width: 100%;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._source: str = "pipeline"

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("Global Activity Log", classes="gas-title", markup=False)
            with RadioSet(classes="gas-filter"):
                yield RadioButton("pipeline", id="rb-pipeline", value=True)
                yield RadioButton("sync",     id="rb-sync")
                yield RadioButton("review-all", id="rb-review-all")
            with VerticalScroll():
                yield Static(
                    _load_log("pipeline"),
                    id="gas-body",
                    classes="gas-body",
                    markup=False,
                )
            yield Static(
                "(escape / q to close)",
                classes="gas-footer",
                markup=False,
            )

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        rb_id = event.pressed.id or ""
        if rb_id == "rb-pipeline":
            self._source = "pipeline"
        elif rb_id == "rb-sync":
            self._source = "sync"
        elif rb_id == "rb-review-all":
            self._source = "review-all"
        else:
            return
        self.query_one("#gas-body", Static).update(_load_log(self._source))
