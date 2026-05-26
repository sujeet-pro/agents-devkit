"""DiffPane — file-aware diff viewer for the Diff tab.

Layout (left → right):

  ┌─ files (30%) ──┬─ diff content (70%) ─────────────────────┐
  │ ▸ +10/-2 a.py  │ diff --git a/src/a.py b/src/a.py         │
  │   +1/-0 b.md   │ @@ -10,3 +10,5 @@                        │
  │   +0/-3 c.go   │ -old line                                │
  │   …            │ +new line                                │
  └────────────────┴─────────────────────────────────────────┘

- File list is a ``ListView``; arrow keys / clicks move the selection and
  the right pane re-renders. The file label shows ``+adds/-subs  path``.
- The diff content is rendered with Rich's ``Syntax`` widget using the
  ``diff`` lexer, which colors additions green, deletions red, hunk
  headers in a distinct hue, and file headers bold. It sits inside a
  ``ScrollableContainer`` so both axes scroll (long lines + many lines).
- ``show(row)`` reads ``<task_dir>/pr-review/diff.patch`` and refreshes;
  it preserves the currently-selected file across reloads when that path
  is still present.
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import ScrollableContainer, VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, ListItem, ListView, Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


_DIFF_FILE_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)$")
_HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<old>\d+)(?:,(?P<old_len>\d+))? \+(?P<new>\d+)(?:,(?P<new_len>\d+))? @@"
)

# Width of each line-number gutter column. 5 digits fits files up to 99999.
_LN_W = 5
_GUTTER_BLANK = " " * _LN_W


def _ln(num: int | None) -> str:
    """Right-justify a line number to the gutter width, or blank when None."""
    if num is None:
        return _GUTTER_BLANK
    return f"{num:>{_LN_W}}"


def _build_diff_text(file_lines: list[str]) -> Text:
    """Render a per-file diff as a Rich ``Text`` with line-number gutters,
    additions in green, deletions in red, and a ``…`` separator between
    non-contiguous hunks.

    Gutter layout per line: ``<old> <new> │ <content>``. The bar makes the
    boundary between gutter and code visible against any theme. File-header
    and hunk-header lines leave the gutter blank.
    """
    text = Text()
    old_ln: int | None = None
    new_ln: int | None = None
    saw_first_hunk = False

    for line in file_lines:
        # File-meta lines: ``diff --git``, ``index <sha>``, ``--- a/<p>``,
        # ``+++ b/<p>``. Render in bold cyan so the file boundary stands out.
        if (
            line.startswith("diff --git ")
            or line.startswith("index ")
            or line.startswith("--- ")
            or line.startswith("+++ ")
            or line.startswith("new file mode")
            or line.startswith("deleted file mode")
            or line.startswith("similarity index")
            or line.startswith("rename from")
            or line.startswith("rename to")
        ):
            text.append(f"{_GUTTER_BLANK} {_GUTTER_BLANK} │ ", style="dim")
            text.append(f"{line}\n", style="bold cyan")
            continue

        # Hunk header — restart line numbering and (if not the first hunk in
        # the file) emit a ``…`` separator to mark the gap.
        m = _HUNK_HEADER_RE.match(line)
        if m:
            if saw_first_hunk:
                text.append(
                    f"{'…':>{_LN_W}} {'…':>{_LN_W}} │ …\n",
                    style="dim",
                )
            old_ln = int(m.group("old"))
            new_ln = int(m.group("new"))
            saw_first_hunk = True
            text.append(f"{_GUTTER_BLANK} {_GUTTER_BLANK} │ ", style="dim")
            text.append(f"{line}\n", style="magenta")
            continue

        # Content lines. `\\ No newline at end of file` is a comment-style
        # tail with no line-number impact.
        if line.startswith("\\"):
            text.append(f"{_GUTTER_BLANK} {_GUTTER_BLANK} │ ", style="dim")
            text.append(f"{line}\n", style="dim italic")
            continue

        if line.startswith("+") and not line.startswith("+++"):
            text.append(f"{_ln(None)} {_ln(new_ln)} │ ", style="dim")
            text.append(f"{line}\n", style="green")
            if new_ln is not None:
                new_ln += 1
        elif line.startswith("-") and not line.startswith("---"):
            text.append(f"{_ln(old_ln)} {_ln(None)} │ ", style="dim")
            text.append(f"{line}\n", style="red")
            if old_ln is not None:
                old_ln += 1
        else:
            # Context line (starts with space, or empty).
            text.append(f"{_ln(old_ln)} {_ln(new_ln)} │ ", style="dim")
            text.append(f"{line}\n")
            if old_ln is not None:
                old_ln += 1
            if new_ln is not None:
                new_ln += 1

    return text


def _split_diff_by_file(patch: str) -> list[dict]:
    """Split a unified diff into per-file entries with ``{path, lines}``.

    A file boundary is the ``diff --git a/<path> b/<path>`` line. Content
    before the first such line (rare, but possible with non-git diffs) is
    discarded — those aren't part of any file.
    """
    files: list[dict] = []
    current: dict | None = None
    for line in patch.splitlines():
        m = _DIFF_FILE_HEADER_RE.match(line)
        if m:
            if current is not None:
                files.append(current)
            current = {"path": m.group(2), "lines": [line]}
        elif current is not None:
            current["lines"].append(line)
    if current is not None:
        files.append(current)
    return files


def _diff_stats(lines: list[str]) -> tuple[int, int]:
    """Count added / removed lines, ignoring file-header `+++` / `---` lines."""
    adds = subs = 0
    for ln in lines:
        if ln.startswith("+++") or ln.startswith("---"):
            continue
        if ln.startswith("+"):
            adds += 1
        elif ln.startswith("-"):
            subs += 1
    return adds, subs


_EMPTY_HINT = "(no diff fetched — press [x] to refresh)"
_PARSE_FAIL_HINT = "(failed to read diff.patch)"


class DiffPane(Widget):
    """Per-file diff viewer with a list + content split."""

    DEFAULT_CSS = """
    DiffPane { layout: horizontal; height: 1fr; width: 1fr; }
    DiffPane #diff-files-scroll {
        width: 30%;
        height: 1fr;
        border-right: solid $accent 50%;
    }
    DiffPane #diff-files-list { background: $surface; height: 1fr; }
    DiffPane ListItem { padding: 0 1; }
    DiffPane ListItem.--highlight { background: $accent 30%; }
    DiffPane #diff-scroll {
        width: 70%;
        height: 1fr;
        background: $surface;
    }
    DiffPane #diff-content { padding: 0 1; height: auto; width: auto; }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._files: list[dict] = []
        self._current_path: str | None = None

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="diff-files-scroll"):
            yield ListView(id="diff-files-list")
        with ScrollableContainer(id="diff-scroll"):
            yield Static(_EMPTY_HINT, id="diff-content", markup=False)

    # --- public API -------------------------------------------------------

    def show(self, row: "QueueRow | None") -> None:
        """Refresh from disk for the selected PR row."""
        if row is None:
            self._files = []
            self._render_empty(_EMPTY_HINT)
            return

        # _PR_REVIEW_ROOT is module-level in queue_model and resolves at
        # import time. We re-import each call so tests that monkey-patch
        # ADK_DATA_HOME see fresh paths without reload contortions.
        from tui.model.queue_model import _PR_REVIEW_ROOT

        path = _PR_REVIEW_ROOT / f"{row.repo}_pr-{row.number}" / "pr-review" / "diff.patch"
        if not path.exists():
            self._files = []
            self._render_empty(_EMPTY_HINT)
            return

        try:
            patch = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            self._files = []
            self._render_empty(_PARSE_FAIL_HINT)
            return

        files = _split_diff_by_file(patch)
        self._files = files
        if not files:
            self._render_empty("(diff.patch present but contained no file diffs)")
            return

        # Preserve selection across reloads when the same path is still there.
        target_idx = 0
        if self._current_path:
            for i, f in enumerate(files):
                if f["path"] == self._current_path:
                    target_idx = i
                    break
        self._refresh_file_list(target_idx)

    def focus_file_list(self) -> None:
        """Focus the left file list so arrow keys browse files."""
        try:
            self.query_one("#diff-files-list", ListView).focus()
        except Exception:
            pass

    # --- internals --------------------------------------------------------

    def _refresh_file_list(self, select_idx: int) -> None:
        try:
            list_view = self.query_one("#diff-files-list", ListView)
        except Exception:
            return
        list_view.clear()
        for f in self._files:
            adds, subs = _diff_stats(f["lines"])
            stats = f"+{adds}/-{subs}".rjust(8)
            label = Label(f"{stats}  {f['path']}", markup=False)
            list_view.append(ListItem(label))
        if 0 <= select_idx < len(self._files):
            try:
                list_view.index = select_idx
            except Exception:
                pass
            self._render_file(select_idx)

    def _render_file(self, idx: int) -> None:
        if not (0 <= idx < len(self._files)):
            return
        f = self._files[idx]
        self._current_path = f["path"]
        try:
            content = self.query_one("#diff-content", Static)
        except Exception:
            return
        text = _build_diff_text(f["lines"])
        content.update(text)

    def _render_empty(self, msg: str) -> None:
        try:
            list_view = self.query_one("#diff-files-list", ListView)
            list_view.clear()
        except Exception:
            pass
        try:
            content = self.query_one("#diff-content", Static)
            content.update(msg)
        except Exception:
            pass

    # --- ListView highlight = render the highlighted file -----------------

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        idx = event.list_view.index
        if idx is not None:
            self._render_file(idx)
