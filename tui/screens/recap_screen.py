"""End-of-run recap modal — pushed after `R` (batch) finishes.

Shows per-row outcomes (ok / failed / skipped / spawn-error / crashed) with
the last log line of context. Dismissed with `escape` or `enter`.
"""
from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static


_OUTCOME_GLYPHS: dict[str, tuple[str, str]] = {
    # outcome → (unicode, ascii)
    "ok":          ("✓", "[ok]"),
    "failed":      ("✗", "[fl]"),
    "skipped":     ("↷", "[sk]"),
    "spawn-error": ("⚠", "[sp]"),
    "crashed":     ("☠", "[cr]"),
}


class RecapScreen(ModalScreen[None]):
    BINDINGS = [
        Binding("escape", "dismiss", show=False),
        Binding("enter", "dismiss", show=False),
        Binding("q", "dismiss", show=False),
    ]

    DEFAULT_CSS = """
    RecapScreen {
        align: center middle;
    }
    RecapScreen > Container {
        width: 80;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    RecapScreen Static {
        width: 100%;
    }
    """

    def __init__(self, outcomes: list[dict], *, ascii_only: bool = False) -> None:
        super().__init__()
        self._outcomes = list(outcomes)
        self._ascii_only = ascii_only

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(self._format_text(), markup=False)

    def _format_text(self) -> str:
        if not self._outcomes:
            return "Batch recap — 0 rows\n\n(press escape to close)"
        total = len(self._outcomes)
        n_ok = sum(1 for o in self._outcomes if o.get("outcome") == "ok")
        n_failed = sum(1 for o in self._outcomes if o.get("outcome") == "failed")
        n_skipped = sum(1 for o in self._outcomes if o.get("outcome") == "skipped")
        n_other = total - n_ok - n_failed - n_skipped
        header = (
            f"Batch recap — {total} rows "
            f"({n_ok} ok, {n_failed} failed, {n_skipped} skipped"
            + (f", {n_other} other" if n_other else "")
            + ")"
        )
        body_lines: list[str] = []
        for o in self._outcomes:
            outcome = str(o.get("outcome", "unknown"))
            glyphs = _OUTCOME_GLYPHS.get(outcome, ("•", "[--]"))
            glyph = glyphs[1] if self._ascii_only else glyphs[0]
            pr_url = str(o.get("pr_url", "—"))
            short = _shorten(pr_url)
            rc = o.get("rc")
            rc_label = f"rc={rc}" if rc is not None else "—"
            last = (o.get("last_line") or "").strip()
            if len(last) > 60:
                last = last[:57] + "…"
            body_lines.append(f"  {glyph}  {short:30s}  {rc_label:6s}  {last}")
        footer = "\n(press escape / enter / q to close)"
        return "\n".join([header, "", *body_lines, footer])


def _shorten(pr_url: str) -> str:
    import re
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    m = re.search(r"bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    return pr_url
