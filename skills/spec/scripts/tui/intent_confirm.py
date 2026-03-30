#!/usr/bin/env python3
"""
Intent Confirmation TUI — DevKit Framework (Phase 0)
======================================================

Single-pane scrollable view for confirming the agent's understanding of the
user's goal before proceeding with skill execution.

Usage:  python3 intent_confirm.py <session_dir>
Input:  <session_dir>/intent.json
Output: <session_dir>/intent_result.json

intent.json schema:
  {
    "summary": "One-line restatement of user's goal",
    "reasoning": ["Bullet 1", "Bullet 2"],
    "skills": [{"name": "/review", "rationale": "...", "params": "--mode interactive"}],
    "tools_mcps": [{"name": "GitHub MCP", "status": "configured|missing|optional"}],
    "complexity": "Medium",
    "complexity_rationale": "4 files, minor architectural decision",
    "pe_check": "Optional PE check text or null"
  }

intent_result.json schema:
  {
    "action": "approved|modified|simplify|cancelled",
    "modifications": "User's edit text if modified, empty otherwise"
  }

Keys:
  Enter  Approve       e  Edit (modify understanding)
  s      Simplify      q  Cancel
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
from textual.containers import VerticalScroll
from textual.widgets import Footer, Header, Markdown, Static

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from base import EditModal, load_json, save_json
else:
    from .base import EditModal, load_json, save_json

# ── Tool/MCP status icons ────────────────────────────────────────────
TOOL_ICONS = {
    "configured": "✓",
    "missing":    "✗",
    "optional":   "○",
}
TOOL_COLORS = {
    "configured": "green",
    "missing":    "red",
    "optional":   "dim",
}

COMPLEXITY_COLORS = {
    "Trivial": "dim",
    "Small":   "green",
    "Medium":  "yellow",
    "Large":   "red",
}


# ── Intent Confirmation App ──────────────────────────────────────────
class IntentConfirmApp(App):
    """Single-pane TUI for confirming agent intent before execution."""

    TITLE = "Intent Confirmation"

    CSS = """
    #content-pane {
        height: 1fr;
        border: round $accent;
        border-title-align: left;
        padding: 1 2;
    }
    #status-bar {
        height: 1;
        background: $primary-background;
        padding: 0 2;
    }
    """

    BINDINGS = [
        Binding("enter", "approve", "Approve", show=True),
        Binding("e", "edit", "Edit", show=True),
        Binding("s", "simplify", "Simplify", show=True),
        Binding("q", "cancel", "Cancel", show=True),
    ]

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir
        self.data = load_json(session_dir / "intent.json")

    # ── Layout ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header()
        pane = VerticalScroll(Markdown(""), id="content-pane")
        pane.border_title = "Intent"
        yield pane
        yield Static(
            " Enter = Approve  |  e = Edit  |  s = Simplify  |  q = Cancel",
            id="status-bar",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.data.get("summary", "Intent Review")[:60]
        self._render_content()

    # ── Rendering ─────────────────────────────────────────────────────
    def _render_content(self) -> None:
        """Build the full markdown view from intent data."""
        d = self.data
        parts: list[str] = []

        # Understanding
        parts.append("## Understanding\n")
        parts.append(f"{d.get('summary', 'No summary provided.')}\n")

        # My Thinking
        reasoning = d.get("reasoning", [])
        if reasoning:
            parts.append("## My Thinking\n")
            for bullet in reasoning:
                parts.append(f"- {bullet}")
            parts.append("")

        # Skills & Tools
        skills = d.get("skills", [])
        tools = d.get("tools_mcps", [])
        if skills or tools:
            parts.append("## Skills & Tools\n")
            if skills:
                parts.append("**Skills:**\n")
                for sk in skills:
                    name = sk.get("name", "?")
                    rationale = sk.get("rationale", "")
                    params = sk.get("params", "")
                    line = f"- `{name}`"
                    if params:
                        line += f" `{params}`"
                    if rationale:
                        line += f" -- {rationale}"
                    parts.append(line)
                parts.append("")
            if tools:
                parts.append("**Tools / MCPs:**\n")
                for tool in tools:
                    name = tool.get("name", "?")
                    status = tool.get("status", "optional")
                    icon = TOOL_ICONS.get(status, "?")
                    parts.append(f"- {icon} **{name}** ({status})")
                parts.append("")

        # Complexity
        complexity = d.get("complexity", "")
        rationale = d.get("complexity_rationale", "")
        if complexity:
            parts.append("## Complexity\n")
            parts.append(f"**{complexity}**")
            if rationale:
                parts.append(f" -- {rationale}")
            parts.append("")

        # PE Check
        pe_check = d.get("pe_check")
        if pe_check:
            parts.append("## PE Check\n")
            parts.append(f"{pe_check}\n")

        body = "\n".join(parts)
        pane = self.query_one("#content-pane", VerticalScroll)
        pane.query_one(Markdown).update(body)

    # ── Actions ───────────────────────────────────────────────────────
    def _write_result(self, action: str, modifications: str = "") -> None:
        """Write intent_result.json and exit."""
        save_json(
            self.session_dir / "intent_result.json",
            {"action": action, "modifications": modifications},
        )
        self.exit()

    def action_approve(self) -> None:
        self._write_result("approved")

    def action_simplify(self) -> None:
        self._write_result("simplify")

    def action_cancel(self) -> None:
        self._write_result("cancelled")

    def action_edit(self) -> None:
        def on_result(text: str) -> None:
            if text:
                self._write_result("modified", text)

        self.push_screen(
            EditModal(
                title="Modify Understanding",
                prompt="How should the understanding be adjusted?",
                placeholder="e.g., also include tests, skip the migration step...",
            ),
            on_result,
        )


# ── CLI entry point ───────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  session_dir must contain intent.json")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not (session_dir / "intent.json").exists():
        print(f"Error: {session_dir / 'intent.json'} not found")
        sys.exit(1)

    IntentConfirmApp(session_dir).run()


if __name__ == "__main__":
    main()
