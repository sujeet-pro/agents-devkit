#!/usr/bin/env python3
"""
Plan Approval TUI — DevKit Framework (Phase 3)
================================================

Two-pane terminal UI for reviewing and approving an implementation plan.
Left pane shows a tree view of waves with nested tasks and status icons;
right pane shows the selected task's full detail.

Usage:  python3 plan_approve.py <session_dir>
Input:  <session_dir>/plan.json
Output: <session_dir>/plan_result.json

plan.json schema:
  {
    "title": "Implementation Plan: Feature Name",
    "waves": [
      {
        "id": "w1",
        "name": "Wave 1 (parallel)",
        "tasks": [
          {
            "id": "t1",
            "description": "Create auth middleware",
            "files": ["src/middleware/auth.ts"],
            "verification": "npm test -- --grep auth",
            "effort": "~30min",
            "team": "implementer"
          }
        ]
      }
    ]
  }

plan_result.json schema:
  {
    "action": "approved|modified|cancelled",
    "added_tasks": [{"description": "...", "after_wave": "w1"}],
    "removed_tasks": ["t3"]
  }

Keys:
  ↑/↓    Navigate         Enter  Approve plan
  a      Add task          r      Remove selected task
  q      Cancel
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


# ── Plan Approval App ────────────────────────────────────────────────
class PlanApproveApp(App):
    """Two-pane TUI for reviewing and approving an implementation plan."""

    TITLE = "Plan Approval"

    CSS = """
    #main {
        height: 1fr;
    }
    #list-pane {
        width: 1fr;
        min-width: 36;
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
        Binding("enter", "approve", "Approve", show=True),
        Binding("a", "add_task", "Add Task", show=True),
        Binding("r", "remove_task", "Remove", show=True),
        Binding("q", "cancel", "Cancel", show=True),
    ]

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir
        data = load_json(session_dir / "plan.json")
        self.session_title: str = data.get("title", "Implementation Plan")
        self.waves: list[dict] = data.get("waves", [])
        # Build flat list of (wave_idx, task_idx | None) for navigation
        self._entries: list[tuple[int, int | None]] = []
        # Track modifications
        self._added_tasks: list[dict] = []
        self._removed_tasks: list[str] = []
        self._build_entries()
        self._idx: int = 0

    def _build_entries(self) -> None:
        """Build a flat list of navigable entries from the wave/task hierarchy."""
        self._entries = []
        for wi, wave in enumerate(self.waves):
            self._entries.append((wi, None))  # wave header
            for ti in range(len(wave.get("tasks", []))):
                task = wave["tasks"][ti]
                if task.get("id") not in self._removed_tasks:
                    self._entries.append((wi, ti))

    # ── Layout ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            list_items = [
                ListItem(Label(self._label(i), classes="il"), id=f"p{i}")
                for i in range(len(self._entries))
            ]
            lv = ListView(*list_items, id="list-pane")
            total_tasks = sum(
                len(w.get("tasks", [])) for w in self.waves
            ) - len(self._removed_tasks)
            lv.border_title = f"Plan ({len(self.waves)} waves, {total_tasks} tasks)"
            yield lv

            pane = VerticalScroll(Markdown(""), id="detail-pane")
            pane.border_title = "Detail"
            yield pane

        yield Static(self._status_text(), id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.session_title
        if self._entries:
            self._show_detail(0)

    # ── Rendering helpers ─────────────────────────────────────────────
    def _label(self, i: int) -> str:
        """Render a list entry label (wave header or indented task)."""
        wi, ti = self._entries[i]
        wave = self.waves[wi]
        if ti is None:
            # Wave header
            name = wave.get("name", f"Wave {wi + 1}")
            task_count = sum(
                1 for t in wave.get("tasks", [])
                if t.get("id") not in self._removed_tasks
            )
            return f"[bold]{name}[/bold] ({task_count} tasks)"
        else:
            # Task entry
            task = wave["tasks"][ti]
            desc = task.get("description", "Untitled")[:42]
            effort = task.get("effort", "")
            effort_tag = f" [dim]({effort})[/dim]" if effort else ""
            return f"  ○ {desc}{effort_tag}"

    def _status_text(self) -> str:
        """Render the bottom status bar."""
        mods = []
        if self._added_tasks:
            mods.append(f"[green]+{len(self._added_tasks)} added[/]")
        if self._removed_tasks:
            mods.append(f"[red]-{len(self._removed_tasks)} removed[/]")
        mod_str = "  |  ".join(mods) if mods else "No modifications"
        return f" Enter = Approve  |  a = Add  |  r = Remove  |  q = Cancel  |  {mod_str}"

    def _show_detail(self, i: int) -> None:
        """Update the detail pane with task or wave details."""
        wi, ti = self._entries[i]
        wave = self.waves[wi]

        if ti is None:
            # Wave overview
            parts: list[str] = []
            name = wave.get("name", f"Wave {wi + 1}")
            parts.append(f"## {name}\n")
            tasks = [
                t for t in wave.get("tasks", [])
                if t.get("id") not in self._removed_tasks
            ]
            if tasks:
                parts.append(f"**{len(tasks)} tasks:**\n")
                for t in tasks:
                    desc = t.get("description", "Untitled")
                    effort = t.get("effort", "")
                    line = f"- {desc}"
                    if effort:
                        line += f" ({effort})"
                    parts.append(line)
            else:
                parts.append("*No tasks in this wave.*")
            body = "\n".join(parts)
            title = name
        else:
            # Task detail
            task = wave["tasks"][ti]
            parts = []
            desc = task.get("description", "Untitled")
            parts.append(f"## {desc}\n")

            # Files
            files = task.get("files", [])
            if files:
                parts.append("**Files:**\n")
                for f in files:
                    parts.append(f"- `{f}`")
                parts.append("")

            # Verification
            verification = task.get("verification", "")
            if verification:
                parts.append(f"**Verification:** `{verification}`\n")

            # Metadata
            meta_parts: list[str] = []
            if task.get("effort"):
                meta_parts.append(f"**Effort:** {task['effort']}")
            if task.get("team"):
                meta_parts.append(f"**Team:** {task['team']}")
            if meta_parts:
                parts.append(" | ".join(meta_parts))
                parts.append("")

            # Wave context
            wave_name = wave.get("name", f"Wave {wi + 1}")
            parts.append(f"---\n*Part of {wave_name}*")

            body = "\n".join(parts)
            title = desc

        pane = self.query_one("#detail-pane", VerticalScroll)
        pane.query_one(Markdown).update(body)
        pane.border_title = f"Detail — {title[:55]}"
        pane.scroll_home(animate=False)

    def _refresh_ui(self) -> None:
        """Rebuild entries and refresh list labels, status bar, and detail pane."""
        # We need to rebuild the list since entries may have changed
        self._build_entries()
        lv = self.query_one("#list-pane", ListView)

        # Update existing labels or handle count mismatch
        list_items = lv.query(ListItem)
        current_count = len(list_items)
        new_count = len(self._entries)

        # Refresh labels for entries that still exist
        for i in range(min(current_count, new_count)):
            list_items[i].query_one(Label).update(self._label(i))

        self.query_one("#status-bar", Static).update(self._status_text())
        if self._entries and self._idx < len(self._entries):
            self._show_detail(self._idx)

    # ── Events ────────────────────────────────────────────────────────
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id and event.item.id.startswith("p"):
            self._idx = int(event.item.id[1:])
            if self._idx < len(self._entries):
                self._show_detail(self._idx)

    # ── Actions ───────────────────────────────────────────────────────
    def _write_result(self, action: str) -> None:
        """Write plan_result.json and exit."""
        save_json(
            self.session_dir / "plan_result.json",
            {
                "action": action,
                "added_tasks": self._added_tasks,
                "removed_tasks": self._removed_tasks,
            },
        )
        self.exit()

    def action_approve(self) -> None:
        action = "modified" if (self._added_tasks or self._removed_tasks) else "approved"
        self._write_result(action)

    def action_cancel(self) -> None:
        self._write_result("cancelled")

    def action_remove_task(self) -> None:
        """Remove the currently selected task."""
        if not self._entries or self._idx >= len(self._entries):
            return
        wi, ti = self._entries[self._idx]
        if ti is None:
            self.notify("Cannot remove a wave — select a specific task", severity="warning")
            return
        task = self.waves[wi]["tasks"][ti]
        task_id = task.get("id", "")
        if task_id and task_id not in self._removed_tasks:
            self._removed_tasks.append(task_id)
            self.notify(f"✗ Removed: {task.get('description', task_id)[:40]}", severity="warning")
            self._refresh_ui()

    def action_add_task(self) -> None:
        """Add a new task via modal."""
        # Determine which wave to add after
        if self._entries and self._idx < len(self._entries):
            wi, _ = self._entries[self._idx]
            wave_id = self.waves[wi].get("id", f"w{wi + 1}")
        else:
            wave_id = self.waves[0].get("id", "w1") if self.waves else "w1"

        def on_result(text: str) -> None:
            if text:
                self._added_tasks.append({"description": text, "after_wave": wave_id})
                self.notify(f"+ Added task after {wave_id}", severity="information")
                self._refresh_ui()

        self.push_screen(
            EditModal(
                title=f"Add Task (after {wave_id})",
                prompt="Describe the new task:",
                placeholder="e.g., Add integration tests for the auth flow...",
            ),
            on_result,
        )


# ── CLI entry point ───────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  session_dir must contain plan.json")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not (session_dir / "plan.json").exists():
        print(f"Error: {session_dir / 'plan.json'} not found")
        sys.exit(1)

    data = load_json(session_dir / "plan.json")
    if not data.get("waves"):
        print("No waves in plan.")
        save_json(
            session_dir / "plan_result.json",
            {"action": "cancelled", "added_tasks": [], "removed_tasks": []},
        )
        sys.exit(0)

    PlanApproveApp(session_dir).run()


if __name__ == "__main__":
    main()
