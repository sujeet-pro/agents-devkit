from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static

_HELP_TEXT = """\
adk PR-review TUI · keyboard reference
───────────────────────────────────────────────────────────────

Selected-PR actions  (act on the highlighted PR)
  s     Sync this PR (refresh meta + comments)
  r     Review this PR
  a     Approve this PR
  m     Mergeable check for this PR
  M     Merge this PR
  u     Update / refresh cascade  (sync → re-index → re-review)
  x     Remove this PR from the queue  (does not close on host)
  o     Open this PR in the browser
  l     Show logs for this PR

All-PRs actions  (batch)
  S     Sync all PRs in the queue
  R     Review all queued PRs
  L     Show all run logs

Add / browse / runner
  +     Add a PR by URL
  b     Browse / manage configured repos
  t     Pick the agent / runner

Filter / sort / navigation
  f     Cycle filter  (which PRs are visible)
  K     Cycle sort
  j / k           Move row selection down / up
  arrows          Scroll or cycle  (queue rows / tab strip / handle)
  tab             Cycle focus between queue table and detail pane

Detail tabs
  1     Overview
  2     Review
  3     Comments
  4     Diff
  5     Activity
  , / . Cycle stage tab prev / next

Layout
  [ / ] Shrink / grow the queue half
  =     Reset split to 50/50
  (Drag the ··· drag ··· handle with the mouse to resize)

Comments tab  (only active when Comments is focused)
  o     Toggle Open / All filter
  n / N Jump to next / previous comment divider
  y     Accept the focused unposted draft
  d     Discard the focused unposted draft

Global
  enter Open the PR action menu  (less-common actions)
  ?     This help
  q     Quit
  esc   Close this help
"""


class HelpScreen(ModalScreen[None]):
    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    HelpScreen > Container {
        width: 72;
        height: auto;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    HelpScreen Static {
        width: 100%;
    }
    """

    BINDINGS = [
        Binding("question_mark", "dismiss", show=False),
        Binding("escape", "dismiss", show=False),
    ]

    def compose(self) -> ComposeResult:
        with Container():
            yield Static(_HELP_TEXT, markup=False)
