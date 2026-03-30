#!/usr/bin/env python3
"""
Progress Dashboard TUI — DevKit Framework (Phase 4)
=====================================================

Full-width live dashboard showing execution progress. Displays a tree view
of waves and tasks with status icons, elapsed times, and error details.
Auto-refreshes every 2 seconds by re-reading progress.json.

Usage:  python3 progress_dashboard.py <session_dir>
Input:  <session_dir>/progress.json  (updated by executing agent)

progress.json schema:
  {
    "title": "Executing: Feature Name",
    "started_at": "2024-01-15T10:00:00Z",
    "waves": [
      {
        "id": "w1",
        "name": "Wave 1",
        "status": "completed|running|pending",
        "tasks": [
          {
            "id": "t1",
            "description": "Create auth middleware",
            "status": "completed|running|failed|pending",
            "elapsed": "2m14s",
            "error": null
          }
        ]
      }
    ]
  }

Keys:
  q  Quit (display only, does not affect execution)
"""

import json
import subprocess
import sys
from datetime import datetime
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
    from base import load_json
else:
    from .base import load_json

# ── Status icons ─────────────────────────────────────────────────────
STATUS_ICONS = {
    "completed": ("✓", "green"),
    "running":   ("◉", "yellow"),
    "failed":    ("✗", "red"),
    "pending":   ("○", "dim"),
}


# ── Progress Dashboard App ───────────────────────────────────────────
class ProgressDashboardApp(App):
    """Full-width live dashboard for monitoring execution progress."""

    TITLE = "Progress Dashboard"

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
        Binding("q", "quit_app", "Quit", show=True),
    ]

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir
        self._progress_file = session_dir / "progress.json"
        self._data: dict = {}

    # ── Layout ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header()
        pane = VerticalScroll(Markdown(""), id="content-pane")
        pane.border_title = "Progress"
        yield pane
        yield Static("", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self._reload_and_render()
        self.set_interval(2, self._reload_and_render)

    # ── Data & Rendering ──────────────────────────────────────────────
    def _reload_and_render(self) -> None:
        """Re-read progress.json and update the display."""
        self._data = load_json(self._progress_file)
        if not self._data:
            return
        self._render_content()
        self._render_status_bar()

    def _render_content(self) -> None:
        """Build the full markdown view from progress data."""
        d = self._data
        parts: list[str] = []

        # Title
        title = d.get("title", "Execution Progress")
        parts.append(f"## {title}\n")

        # Timing
        started_at = d.get("started_at", "")
        if started_at:
            try:
                start = datetime.fromisoformat(started_at.replace("Z", "+00:00"))
                elapsed = datetime.now(start.tzinfo) - start
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                parts.append(f"**Started:** {started_at}  |  **Elapsed:** {minutes}m{seconds}s\n")
            except (ValueError, TypeError):
                parts.append(f"**Started:** {started_at}\n")

        # Waves and tasks
        waves = d.get("waves", [])
        for wave in waves:
            wave_name = wave.get("name", "Wave")
            wave_status = wave.get("status", "pending")
            w_icon, _ = STATUS_ICONS.get(wave_status, ("?", "dim"))
            parts.append(f"### {w_icon} {wave_name}\n")

            tasks = wave.get("tasks", [])
            for task in tasks:
                desc = task.get("description", "Untitled")
                status = task.get("status", "pending")
                elapsed = task.get("elapsed", "")
                error = task.get("error")
                t_icon, _ = STATUS_ICONS.get(status, ("?", "dim"))

                elapsed_str = f"  ({elapsed})" if elapsed else ""
                parts.append(f"- {t_icon} {desc}{elapsed_str}")

                if error:
                    # Show error indented below the task
                    parts.append(f"  - **Error:** {error}")

            parts.append("")

        body = "\n".join(parts)
        pane = self.query_one("#content-pane", VerticalScroll)
        pane.query_one(Markdown).update(body)
        pane.border_title = f"Progress — {d.get('title', 'Execution')[:50]}"

    def _render_status_bar(self) -> None:
        """Update the status bar with summary counts."""
        waves = self._data.get("waves", [])
        counts = {"completed": 0, "running": 0, "failed": 0, "pending": 0}
        total = 0
        for wave in waves:
            for task in wave.get("tasks", []):
                status = task.get("status", "pending")
                counts[status] = counts.get(status, 0) + 1
                total += 1

        bar = (
            f" Tasks: {total}  |  "
            f"[green]✓ {counts['completed']}[/]  |  "
            f"[yellow]◉ {counts['running']}[/]  |  "
            f"[red]✗ {counts['failed']}[/]  |  "
            f"[dim]○ {counts['pending']}[/]  |  "
            f"q = Quit  |  Auto-refresh: 2s"
        )
        self.query_one("#status-bar", Static).update(bar)

    # ── Actions ───────────────────────────────────────────────────────
    def action_quit_app(self) -> None:
        self.exit()


# ── CLI entry point ───────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  session_dir must contain progress.json")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not (session_dir / "progress.json").exists():
        print(f"Error: {session_dir / 'progress.json'} not found")
        sys.exit(1)

    ProgressDashboardApp(session_dir).run()


if __name__ == "__main__":
    main()
