#!/usr/bin/env python3
"""
Generalized Review TUI — DevKit Framework
===========================================

Multi-pane terminal UI for accept/reject/edit review workflows. Supports
multiple metadata display modes via a "mode" field in items.json:

  - "code":    file, line, priority, principle, confidence, source
  - "doc":     section, priority, category
  - "audit":   file, severity, category, cwe
  - default:   show all metadata fields as key-value pairs

Generalized replacement for the legacy standalone review TUIs; imports
shared classes from base.py.

Usage:  python3 review.py <session_dir>
Input:  <session_dir>/items.json
Output: <session_dir>/results.json

items.json schema:
  {
    "title": "Review: PR #123",
    "mode": "code",
    "items": [
      {
        "id":       "unique-id",
        "title":    "Short title for list view",
        "body":     "Full markdown content for detail view",
        "metadata": { ... mode-specific fields ... }
      }
    ]
  }

results.json schema:
  {
    "results": [
      {"id": "unique-id", "action": "accepted|rejected|edit|pending", "prompt": "..."}
    ],
    "summary": {"total": N, "accepted": N, "rejected": N, "edit": N, "pending": N}
  }

Keys:
  ↑/↓   Navigate       a  Accept       r  Reject
  e      Edit (prompt)  u  Undo         d  Done (exit)
  q      Quit (save & exit even if pending)
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
    from base import ICONS, EditModal, load_json, save_json
else:
    from .base import ICONS, EditModal, load_json, save_json

# ── Mode-specific constants ──────────────────────────────────────────
PRIORITY_COLORS = {
    "Blocker":     "red",
    "Critical":    "red",
    "Should Have": "yellow",
    "May Have":    "default",
    "Nitpick":     "default",
    "Question":    "cyan",
}

CATEGORY_COLORS = {
    "accuracy":     "red",
    "clarity":      "yellow",
    "structure":    "cyan",
    "style":        "default",
    "completeness": "magenta",
}

SEVERITY_COLORS = {
    "Critical": "red",
    "High":     "red",
    "Medium":   "yellow",
    "Low":      "green",
    "Info":     "cyan",
}

# Define which metadata keys to show as the tag in the list, per mode
MODE_TAG_FIELD = {
    "code":  "priority",
    "doc":   "category",
    "audit": "severity",
}

MODE_TAG_COLORS = {
    "code":  PRIORITY_COLORS,
    "doc":   CATEGORY_COLORS,
    "audit": SEVERITY_COLORS,
}

# Define the ordered metadata fields to display in detail pane, per mode
MODE_DETAIL_FIELDS: dict[str, list[tuple[str, str]]] = {
    "code": [
        ("file", "File"),
        ("line", "Line"),
        ("priority", "Priority"),
        ("principle", "Principle"),
        ("confidence", "Confidence"),
        ("source", "Source"),
    ],
    "doc": [
        ("section", "Section"),
        ("priority", "Priority"),
        ("category", "Category"),
    ],
    "audit": [
        ("file", "File"),
        ("severity", "Severity"),
        ("category", "Category"),
        ("cwe", "CWE"),
    ],
}


# ── Generalized Review App ───────────────────────────────────────────
class ReviewApp(App):
    """Multi-pane interactive review TUI with mode-aware metadata display."""

    TITLE = "Review"

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
        Binding("a", "mark_accept", "Accept", show=True),
        Binding("r", "mark_reject", "Reject", show=True),
        Binding("e", "mark_edit", "Edit", show=True),
        Binding("u", "mark_undo", "Undo", show=True),
        Binding("d", "finish", "Done", show=True),
        Binding("q", "quit_app", "Quit", show=True),
    ]

    def __init__(self, session_dir: Path) -> None:
        super().__init__()
        self.session_dir = session_dir
        data = load_json(session_dir / "items.json")
        self.session_title: str = data.get("title", "Review")
        self.mode: str = data.get("mode", "")
        self.items: list[dict] = [
            {
                "id": d.get("id", f"item-{i}"),
                "title": d.get("title", "Untitled"),
                "body": d.get("body", ""),
                "meta": d.get("metadata", {}),
                "status": "pending",
                "prompt": "",
            }
            for i, d in enumerate(data.get("items", []))
        ]
        self._idx: int = 0

    # ── Layout ────────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="main"):
            list_items = [
                ListItem(Label(self._label(i), classes="il"), id=f"i{i}")
                for i in range(len(self.items))
            ]
            lv = ListView(*list_items, id="list-pane")
            mode_label = f" [{self.mode}]" if self.mode else ""
            lv.border_title = f"Items ({len(self.items)}){mode_label}"
            yield lv

            pane = VerticalScroll(Markdown(""), id="detail-pane")
            pane.border_title = "Detail"
            yield pane

        yield Static(self._status_text(), id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.session_title
        if self.items:
            self._show_detail(0)

    # ── Rendering helpers ─────────────────────────────────────────────
    def _label(self, i: int) -> str:
        """Render a list item label with status icon and mode-appropriate tag."""
        it = self.items[i]
        sym, col = ICONS[it["status"]]

        # Determine the tag field and color map based on mode
        tag_field = MODE_TAG_FIELD.get(self.mode, "")
        tag_colors = MODE_TAG_COLORS.get(self.mode, {})

        tag = ""
        if tag_field:
            val = it["meta"].get(tag_field, "")
            if val:
                t_col = tag_colors.get(val, "default")
                if t_col == "default":
                    tag = f"\\[{val}] "
                else:
                    tag = f"[{t_col}]\\[{val}][/{t_col}] "
        elif not self.mode:
            # Default mode: show first non-empty metadata value as tag
            for key, val in it["meta"].items():
                if val:
                    tag = f"\\[{val}] " if isinstance(val, str) else ""
                    break

        title = it["title"][:45]
        return f"[{col}]{sym}[/{col}] {i + 1}. {tag}{title}"

    def _status_text(self) -> str:
        """Render the bottom status bar with counts."""
        c = {"pending": 0, "accepted": 0, "rejected": 0, "edit": 0}
        for it in self.items:
            c[it["status"]] += 1
        return (
            f" Total: {len(self.items)}  |  "
            f"[green]✓ {c['accepted']}[/]  |  "
            f"[red]✗ {c['rejected']}[/]  |  "
            f"[cyan]✎ {c['edit']}[/]  |  "
            f"[yellow]● {c['pending']}[/]"
        )

    def _show_detail(self, i: int) -> None:
        """Update the detail pane with mode-appropriate metadata + markdown body."""
        it = self.items[i]
        parts: list[str] = []

        if self.mode in MODE_DETAIL_FIELDS:
            # Mode-specific ordered fields
            for key, label in MODE_DETAIL_FIELDS[self.mode]:
                val = it["meta"].get(key)
                if val is None or val == "":
                    continue
                if key == "file":
                    loc = str(val)
                    line = it["meta"].get("line")
                    if line:
                        loc += f":{line}"
                    parts.append(f"**{label}:** `{loc}`")
                elif key == "line":
                    # Already handled with file
                    continue
                elif key == "confidence":
                    parts.append(f"**{label}:** {val}/100")
                else:
                    parts.append(f"**{label}:** {val}")
        else:
            # Default mode: show all metadata as key-value pairs
            for key, val in it["meta"].items():
                if val is not None and val != "":
                    parts.append(f"**{key.replace('_', ' ').title()}:** {val}")

        # Status (always shown)
        sym, _ = ICONS[it["status"]]
        parts.append(f"**Status:** {sym} {it['status'].title()}")
        if it["status"] == "edit" and it["prompt"]:
            parts.append(f"**Edit prompt:** _{it['prompt']}_")

        header = " | ".join(parts)
        full_body = f"{header}\n\n---\n\n{it['body']}"

        pane = self.query_one("#detail-pane", VerticalScroll)
        pane.query_one(Markdown).update(full_body)
        pane.border_title = f"Detail — {it['title'][:55]}"
        pane.scroll_home(animate=False)

    def _refresh_ui(self) -> None:
        """Refresh all list labels, status bar, and detail pane."""
        for i in range(len(self.items)):
            self.query_one(f"#i{i}", ListItem).query_one(Label).update(self._label(i))
        self.query_one("#status-bar", Static).update(self._status_text())
        self._show_detail(self._idx)

    def _advance_to_next_pending(self) -> None:
        """Move the list highlight to the next pending item (wraps around)."""
        lv = self.query_one("#list-pane", ListView)
        for offset in range(1, len(self.items) + 1):
            nxt = (self._idx + offset) % len(self.items)
            if self.items[nxt]["status"] == "pending":
                lv.index = nxt
                return

    # ── Events ────────────────────────────────────────────────────────
    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.id and event.item.id.startswith("i"):
            self._idx = int(event.item.id[1:])
            self._show_detail(self._idx)

    # ── Actions ───────────────────────────────────────────────────────
    def _set_status(self, status: str, prompt: str = "") -> None:
        """Mark the current item and refresh UI."""
        self.items[self._idx]["status"] = status
        self.items[self._idx]["prompt"] = prompt
        self._refresh_ui()
        self._advance_to_next_pending()

    def action_mark_accept(self) -> None:
        self._set_status("accepted")
        self.notify("✓ Accepted", severity="information")

    def action_mark_reject(self) -> None:
        self._set_status("rejected")
        self.notify("✗ Rejected", severity="warning")

    def action_mark_edit(self) -> None:
        title = self.items[self._idx]["title"]

        def on_result(prompt: str) -> None:
            if prompt:
                self._set_status("edit", prompt)
                self.notify("✎ Marked for edit", severity="information")

        self.push_screen(
            EditModal(
                title=title,
                prompt="How should this item be changed?",
                placeholder="e.g., soften tone, add code example, focus on impact...",
            ),
            on_result,
        )

    def action_mark_undo(self) -> None:
        self._set_status("pending")
        self.notify("↩ Reset to pending")

    def action_finish(self) -> None:
        pending = sum(1 for it in self.items if it["status"] == "pending")
        if pending:
            self.notify(
                f"{pending} item{'s' if pending != 1 else ''} still pending",
                severity="warning",
            )
            return
        self._save_results()
        self.exit()

    def action_quit_app(self) -> None:
        self._save_results()
        self.exit()

    # ── Persistence ───────────────────────────────────────────────────
    def _save_results(self) -> None:
        """Write results.json to the session directory."""
        results = []
        counts = {"pending": 0, "accepted": 0, "rejected": 0, "edit": 0}
        for it in self.items:
            entry: dict = {"id": it["id"], "action": it["status"]}
            if it["status"] == "edit":
                entry["prompt"] = it["prompt"]
            results.append(entry)
            counts[it["status"]] += 1

        output = {
            "results": results,
            "summary": {"total": len(self.items), **counts},
        }
        save_json(self.session_dir / "results.json", output)


# ── CLI entry point ───────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <session_dir>")
        print("  session_dir must contain items.json")
        sys.exit(1)

    session_dir = Path(sys.argv[1])
    if not (session_dir / "items.json").exists():
        print(f"Error: {session_dir / 'items.json'} not found")
        sys.exit(1)

    data = load_json(session_dir / "items.json")
    if not data.get("items"):
        print("No items to review.")
        save_json(
            session_dir / "results.json",
            {
                "results": [],
                "summary": {
                    "total": 0, "accepted": 0, "rejected": 0,
                    "edit": 0, "pending": 0,
                },
            },
        )
        sys.exit(0)

    ReviewApp(session_dir).run()


if __name__ == "__main__":
    main()
