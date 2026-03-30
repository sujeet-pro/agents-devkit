#!/usr/bin/env python3
"""
DevKit TUI Base — Shared classes for all DevKit Textual apps.
===============================================================

Provides:
  - ICONS / CSS constants
  - load_json / save_json helpers
  - EditModal — reusable modal dialog for text input
  - DevKitApp — base App subclass with session_dir handling and JSON I/O

All concrete TUI screens inherit from DevKitApp.

Usage (standalone test):
  python3 base.py <session_dir>
  Prints JSON files found in the directory, then exits.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# ── Auto-install textual on first run ─────────────────────────────────
try:
    from textual.app import App, ComposeResult
except ImportError:
    print("First run — installing textual...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "textual>=1.0.0"]
        )
    except Exception:
        print("Failed. Please run manually: pip install 'textual>=1.0.0'")
        sys.exit(1)
    print("Done.")
    from textual.app import App, ComposeResult

from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Label

# ── Constants ─────────────────────────────────────────────────────────
ICONS = {
    "pending":  ("●", "yellow"),
    "accepted": ("✓", "green"),
    "rejected": ("✗", "red"),
    "edit":     ("✎", "cyan"),
}

PRIORITY_COLORS = {
    "Blocker":     "red",
    "Critical":    "red",
    "Should Have": "yellow",
    "May Have":    "default",
    "Nitpick":     "default",
    "Question":    "cyan",
}

STATUS_ICONS = {
    "completed": ("✓", "green"),
    "running":   ("◉", "yellow"),
    "failed":    ("✗", "red"),
    "pending":   ("○", "dim"),
}

TOOL_STATUS_ICONS = {
    "configured": ("✓", "green"),
    "missing":    ("✗", "red"),
    "optional":   ("○", "dim"),
}

RISK_COLORS = {
    "Low":    "green",
    "Medium": "yellow",
    "High":   "red",
}

# ── Shared CSS fragments ─────────────────────────────────────────────
PANE_CSS = """
#main {
    height: 1fr;
}
#list-pane {
    width: 1fr;
    min-width: 32;
    border: round $primary;
    border-title-align: left;
}
#detail-pane {
    width: 2fr;
    border: round $accent;
    border-title-align: left;
    padding: 0 1;
}
#status-bar {
    height: 1;
    background: $primary-background;
    padding: 0 2;
}
.il {
    padding: 0 1;
}
"""

MODAL_CSS = """
EditModal {
    align: center middle;
}
#dlg {
    width: 72;
    height: auto;
    max-height: 14;
    border: thick $accent;
    background: $surface;
    padding: 1 2;
}
#dlg-title {
    text-style: bold;
    margin-bottom: 1;
}
#dlg-hint {
    color: $text-muted;
    margin-top: 1;
}
"""


# ── JSON I/O helpers ─────────────────────────────────────────────────
def load_json(path: Path) -> dict:
    """Read and parse a JSON file, returning an empty dict on failure."""
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_json(path: Path, data: Any) -> None:
    """Write data as pretty-printed JSON."""
    path.write_text(json.dumps(data, indent=2))


# ── Edit prompt modal ────────────────────────────────────────────────
class EditModal(ModalScreen[str]):
    """Modal dialog for entering free-form text input."""

    CSS = MODAL_CSS

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, title: str, prompt: str = "Enter your text:",
                 placeholder: str = "Type here...") -> None:
        super().__init__()
        self._title = title
        self._prompt = prompt
        self._placeholder = placeholder

    def compose(self) -> ComposeResult:
        with Vertical(id="dlg"):
            yield Label(f"✎  {self._title[:60]}", id="dlg-title")
            yield Label(self._prompt)
            yield Input(placeholder=self._placeholder, id="dlg-input")
            yield Label("Enter = confirm  ·  Escape = cancel", id="dlg-hint")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def action_cancel(self) -> None:
        self.dismiss("")


# ── Base application ─────────────────────────────────────────────────
class DevKitApp(App):
    """Base class for all DevKit TUI applications.

    Subclasses should:
      1. Set INPUT_FILE to the expected input JSON filename.
      2. Set OUTPUT_FILE to the output JSON filename.
      3. Override compose() for their layout.
      4. Call self.load_input() to read input data.
      5. Call self.save_output(data) to write results.
    """

    INPUT_FILE: str = "input.json"
    OUTPUT_FILE: str = "output.json"

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir

    def load_input(self) -> dict:
        """Read the input JSON file from the session directory."""
        return load_json(self.session_dir / self.INPUT_FILE)

    def save_output(self, data: Any) -> None:
        """Write the output JSON file to the session directory."""
        save_json(self.session_dir / self.OUTPUT_FILE, data)


# ── CLI entry point (self-test) ──────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  Prints JSON files found in the directory.")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not session_dir.is_dir():
        print(f"Error: {session_dir} is not a directory")
        sys.exit(1)

    json_files = sorted(session_dir.glob("*.json"))
    if not json_files:
        print(f"No JSON files found in {session_dir}")
    else:
        print(f"JSON files in {session_dir}:")
        for f in json_files:
            data = load_json(f)
            keys = list(data.keys()) if isinstance(data, dict) else f"[{len(data)} items]"
            print(f"  {f.name}: {keys}")
    print("\nbase.py loaded successfully. Exports: DevKitApp, EditModal, ICONS, load_json, save_json")


if __name__ == "__main__":
    main()
