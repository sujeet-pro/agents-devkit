#!/usr/bin/env python3
"""
Approach Selection TUI — DevKit Framework (Phase 2)
=====================================================

Two-pane terminal UI for choosing between implementation approaches.
Left pane shows the approach list with recommended markers; right pane
shows the selected approach's full detail with pros/cons/effort/risk.

Usage:  python3 approach_select.py <session_dir>
Input:  <session_dir>/approaches.json
Output: <session_dir>/approach_result.json

approaches.json schema:
  {
    "title": "Approach Selection: Feature Name",
    "context": "Brief context about what we're deciding",
    "approaches": [
      {
        "id": "a1",
        "name": "Approach name",
        "summary": "2-3 sentence description",
        "pros": ["Pro 1", "Pro 2"],
        "cons": ["Con 1"],
        "effort": "~2 hours",
        "risk": "Low|Medium|High",
        "recommended": true
      }
    ]
  }

approach_result.json schema:
  {
    "action": "selected|mixed|discuss|cancelled",
    "chosen_id": "a1",
    "rationale": "User's text if mixed, empty otherwise"
  }

Keys:
  1/2/3  Select approach     m  Mix approaches
  d      Discuss more        q  Cancel
"""

import json
import subprocess
import sys
from pathlib import Path

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
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import (
    Footer,
    Header,
    Label,
    ListItem,
    ListView,
    Markdown,
    Static,
)

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from base import EditModal, load_json, save_json
else:
    from .base import EditModal, load_json, save_json

# ── Risk coloring ────────────────────────────────────────────────────
RISK_COLORS = {
    "Low":    "green",
    "Medium": "yellow",
    "High":   "red",
}


# ── Approach Selection App ───────────────────────────────────────────
class ApproachSelectApp(App):
    """Two-pane TUI for selecting an implementation approach."""

    TITLE = "Approach Selection"

    CSS = """
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

    BINDINGS = [
        Binding("1", "select_1", "Select 1", show=True),
        Binding("2", "select_2", "Select 2", show=True),
        Binding("3", "select_3", "Select 3", show=True),
        Binding("m", "mix", "Mix", show=True),
        Binding("d", "discuss", "Discuss", show=True),
        Binding("q", "cancel", "Cancel", show=True),
    ]

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir
        data = load_json(session_dir / "approaches.json")
        self.session_title: str = data.get("title", "Approach Selection")
        self.context: str = data.get("context", "")
        self.approaches: list[dict] = data.get("approaches", [])
        self._idx: int = 0

    # ── Layout ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            list_items = [
                ListItem(Label(self._label(i), classes="il"), id=f"a{i}")
                for i in range(len(self.approaches))
            ]
            lv = ListView(*list_items, id="list-pane")
            lv.border_title = f"Approaches ({len(self.approaches)})"
            yield lv

            pane = VerticalScroll(Markdown(""), id="detail-pane")
            pane.border_title = "Detail"
            yield pane

        yield Static(self._status_text(), id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.session_title
        if self.approaches:
            self._show_detail(0)

    # ── Rendering helpers ─────────────────────────────────────────────
    def _label(self, i: int) -> str:
        """Render an approach label with recommended marker."""
        ap = self.approaches[i]
        star = " [green]★[/green]" if ap.get("recommended") else ""
        risk = ap.get("risk", "")
        r_col = RISK_COLORS.get(risk, "default")
        risk_tag = f" [{r_col}]\\[{risk}][/{r_col}]" if risk else ""
        name = ap.get("name", "Unnamed")[:40]
        return f"{i + 1}. {name}{star}{risk_tag}"

    def _status_text(self) -> str:
        """Render the bottom status bar."""
        hint = ""
        if self.context:
            hint = f"  {self.context[:70]}"
        return f" 1-{len(self.approaches)} = Select  |  m = Mix  |  d = Discuss  |  q = Cancel{hint}"

    def _show_detail(self, i: int) -> None:
        """Update the detail pane with full approach information."""
        ap = self.approaches[i]
        parts: list[str] = []

        # Title
        name = ap.get("name", "Unnamed")
        rec = " (recommended)" if ap.get("recommended") else ""
        parts.append(f"## {name}{rec}\n")

        # Summary
        summary = ap.get("summary", "")
        if summary:
            parts.append(f"{summary}\n")

        # Pros
        pros = ap.get("pros", [])
        if pros:
            parts.append("### Pros\n")
            for p in pros:
                parts.append(f"- {p}")
            parts.append("")

        # Cons
        cons = ap.get("cons", [])
        if cons:
            parts.append("### Cons\n")
            for c in cons:
                parts.append(f"- {c}")
            parts.append("")

        # Effort & Risk
        effort = ap.get("effort", "")
        risk = ap.get("risk", "")
        meta_parts: list[str] = []
        if effort:
            meta_parts.append(f"**Effort:** {effort}")
        if risk:
            meta_parts.append(f"**Risk:** {risk}")
        if meta_parts:
            parts.append("---\n")
            parts.append(" | ".join(meta_parts))
            parts.append("")

        body = "\n".join(parts)
        pane = self.query_one("#detail-pane", VerticalScroll)
        pane.query_one(Markdown).update(body)
        pane.border_title = f"Detail — {name[:55]}"
        pane.scroll_home(animate=False)

    # ── Events ────────────────────────────────────────────────────────
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id and event.item.id.startswith("a"):
            self._idx = int(event.item.id[1:])
            self._show_detail(self._idx)

    # ── Actions ───────────────────────────────────────────────────────
    def _write_result(self, action: str, chosen_id: str = "",
                      rationale: str = "") -> None:
        """Write approach_result.json and exit."""
        save_json(
            self.session_dir / "approach_result.json",
            {"action": action, "chosen_id": chosen_id, "rationale": rationale},
        )
        self.exit()

    def _select_approach(self, idx: int) -> None:
        """Select approach by zero-based index."""
        if 0 <= idx < len(self.approaches):
            ap = self.approaches[idx]
            self._write_result("selected", ap.get("id", f"a{idx + 1}"))
        else:
            self.notify(
                f"No approach #{idx + 1} (only {len(self.approaches)} available)",
                severity="warning",
            )

    def action_select_1(self) -> None:
        self._select_approach(0)

    def action_select_2(self) -> None:
        self._select_approach(1)

    def action_select_3(self) -> None:
        self._select_approach(2)

    def action_discuss(self) -> None:
        self._write_result("discuss")

    def action_cancel(self) -> None:
        self._write_result("cancelled")

    def action_mix(self) -> None:
        def on_result(text: str) -> None:
            if text:
                self._write_result("mixed", rationale=text)

        self.push_screen(
            EditModal(
                title="Mix Approaches",
                prompt="Describe how to combine the approaches:",
                placeholder="e.g., use approach 1's auth but approach 2's caching...",
            ),
            on_result,
        )


# ── CLI entry point ───────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  session_dir must contain approaches.json")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not (session_dir / "approaches.json").exists():
        print(f"Error: {session_dir / 'approaches.json'} not found")
        sys.exit(1)

    data = load_json(session_dir / "approaches.json")
    if not data.get("approaches"):
        print("No approaches to select from.")
        save_json(
            session_dir / "approach_result.json",
            {"action": "cancelled", "chosen_id": "", "rationale": "No approaches provided"},
        )
        sys.exit(0)

    ApproachSelectApp(session_dir).run()


if __name__ == "__main__":
    main()
