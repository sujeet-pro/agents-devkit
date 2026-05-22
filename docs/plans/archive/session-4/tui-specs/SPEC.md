# adk TUI — sub-phases α + β (Session 3) — Shared Spec

This is the single source of truth for three parallel agents implementing the
α + β slice of the TUI per `docs/plans/adk-v4-overhaul.md` §10. Each agent
reads this file before writing code, sticks to its assigned file set, and
honours the interfaces declared here.

## 0. Repo root + invariants

- Repo: `/Users/sujeet/personal/agents-devkit/`
- Target Python: 3.11+ (matches the rest of adk).
- Top-level directory: **`tui/`** at the repo root. Not under `skills/`, not under `scripts/`.
- The CLI binary `bin/adk` (no-args invocation) lazy-imports `tui.app:main`.
- Tests run from `tui/tests/` via the repo's existing `python3 -m pytest` invocation pattern.
- Style: match the rest of the repo (snake_case, type hints with `from __future__ import annotations`, no trailing commas in long arg lists, no docstring filler).

## 1. Scope (α + β only)

α — Foundation:
- Textual app launches and quits cleanly with `q`.
- 4-pane skeleton: header bar (top), queue list (left), detail pane (right), footer bar (bottom).
- Help modal opens on `?`, dismisses on `?` or `escape`.

β — Read-only queue view:
- Renders rows from `~/.agents-devkit/config/pr-queue.json5` via `queue_io.read_queue`.
- Per-row state icon (see §3.3 for the join logic).
- Detail pane updates as the user moves the cursor (arrow keys or `j/k`).
- Filter by status with `f` (cycles: all → open → ready → reviewed → terminal).
- Sort with `S` (cycles: FIFO/oldest-first → newest → repo).
- Live refresh: poll the queue file every 2 s; reload on mtime change (NOT every poll — only when mtime changed).
- Empty state when the queue file is missing or `prs:` is empty.

Out of scope this session: `s` sync (γ), `r` review (δ), worker pool, heartbeat, add-PR modal, repo screen, themes-other-than-default.

## 2. Final directory layout

```
tui/
├── __init__.py             # version string + Empty re-export (Agent A owns)
├── app.py                  # AdkApp(textual.App) + main() entry point (Agent A)
├── styles.tcss             # Textual CSS (Agent A)
├── widgets/
│   ├── __init__.py
│   ├── header_bar.py       # top header: "adk · queue: N · ready: M · platform: github"  (Agent A)
│   ├── queue_table.py      # DataTable subclass — renders rows  (Agent A)
│   ├── detail_pane.py      # right side  (Agent A)
│   ├── footer_bar.py       # bottom: keybindings + filter/sort status  (Agent A)
│   └── help_screen.py      # ModalScreen, opened on `?`  (Agent A)
├── model/
│   ├── __init__.py
│   ├── queue_model.py      # poll pr-queue.json5, expose typed rows  (Agent B)
│   └── row_state.py        # derive icon + label from a queue row  (Agent B)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── fixtures/
    │   └── sample_queue.json5
    ├── test_model.py
    ├── test_app_launch.py
    ├── test_queue_render.py
    └── test_keybindings.py
```

Agent C owns: `tui/tests/*` + `bin/adk` no-args wiring + `skills/adk-cli/scripts/requirements.txt` (add `textual>=0.86`).

## 3. Interfaces (binding for all three agents)

### 3.1 `tui.model.queue_model`

```python
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

FilterMode = Literal["all", "open", "ready", "reviewed", "terminal"]
SortMode = Literal["fifo", "newest", "repo"]

@dataclass(frozen=True)
class QueueRow:
    pr_url: str                       # canonical URL key
    host: str                         # "github" | "bitbucket"
    repo: str                         # "owner/repo" (github) | "workspace/slug" (bitbucket)
    number: int                       # PR number
    title: str | None                 # may be None for un-fetched rows
    author: str | None                # ditto
    target_branch: str | None
    head_sha: str | None
    status: str                       # raw queue status (pending/in_review/reviewed/comments/approved/merged/closed/error/reminded)
    prep_status: str | None           # None | pending | preparing | ready | failed | skipped | waiting_for_base
    prep_error: str | None
    taken_at: str | None              # ISO8601 if locked
    last_checked_at: str | None
    last_reviewed_at: str | None
    last_reviewed_head_sha: str | None
    ready_for_review: bool            # derived via queue_io.ready_for_review
    slack_permalink: str | None       # convenience

@dataclass
class QueueSnapshot:
    rows: list[QueueRow]              # already filtered + sorted
    total: int                        # total count across all statuses, regardless of filter
    ready_count: int                  # rows where ready_for_review is True
    in_review_count: int              # rows where taken_at is fresh (not expired)
    platform_summary: str             # "github" | "bitbucket" | "github+bitbucket" | "empty"
    queue_path: Path
    mtime: float                      # last seen mtime
    missing: bool                     # True if queue file does not exist

class QueueModel:
    """Wraps queue_io.read_queue + ready_for_review + filter/sort.

    Args:
      queue_path: defaults to queue_io.DEFAULT_QUEUE_PATH.
      now_fn: injectable clock (defaults to datetime.now(tz=UTC)). Tests use this.
    """

    def __init__(
        self,
        queue_path: Path | None = None,
        *,
        now_fn: Callable[[], "datetime"] | None = None,
    ) -> None: ...

    def snapshot(self, *, filter_mode: FilterMode = "all", sort_mode: SortMode = "fifo") -> QueueSnapshot: ...

    def has_changed(self) -> bool:
        """True iff the queue file's mtime has changed since the last snapshot()
        OR the file appeared / disappeared since the last call. Cheap (stat only).
        """
```

Notes for Agent B:
- The bitbucket/github discriminator and `owner/repo` come from `queue_io.dedupe_key(pr_url) → (host, repo, pr_number)`. Use that helper directly; do NOT roll your own URL parsing.
- Use `queue_io.ready_for_review(entry, now=…)` for `ready_for_review`. Don't re-implement the predicate.
- For `title` / `author`: not stored in the queue today. Read from the row dict's `title` and `author` keys if present (some rows have them), otherwise None. Do NOT fetch from the network.
- `in_review_count`: a row counts as in-review when `_is_locked` returns True. That helper is private to queue_io; re-derive the check locally: `taken_at parses AND now - taken_at < TAKEN_LOCK_MAX_AGE_SECONDS`. Re-import `TAKEN_LOCK_MAX_AGE_SECONDS` from `queue_io`.
- Sort modes:
  - `fifo` = oldest first by `last_checked_at` (None sorts last). This matches `_pick_order_key`'s contract.
  - `newest` = newest first by `last_checked_at`.
  - `repo` = group by `host:repo`, then `number ascending`.
- Filter modes:
  - `all` → everything.
  - `open` → status not in {merged, closed}.
  - `ready` → `ready_for_review is True`.
  - `reviewed` → status in {reviewed, approved, comments, reminded}.
  - `terminal` → status in {merged, closed}.
- `platform_summary`: "github" iff every row's host is github; "bitbucket" iff every row's host is bitbucket; "github+bitbucket" if mixed; "empty" if no rows.

### 3.2 `tui.model.row_state`

```python
from __future__ import annotations
from dataclasses import dataclass
from .queue_model import QueueRow

@dataclass(frozen=True)
class RowState:
    icon: str             # one of the 12 unicode glyphs below (or ASCII fallback)
    label: str            # 1-3 word label, e.g. "ready", "preparing", "merged"
    color: str            # "green" | "yellow" | "red" | "blue" | "white" | "grey" — the canvas decides how to render this

ICON_SET: dict[str, str] = {
    "queued": "🌱",
    "fetching": "🔍",
    "waiting_for_base": "⏳",
    "preparing": "⚙",
    "ready": "✓",
    "in_review": "⚙↻",
    "reviewed": "📝",
    "approved": "✅",
    "blocked": "🚫",
    "merged": "🔒",
    "closed": "🔒",
    "prep_failed": "⚠",
    "stale": "⏰",
}

ASCII_FALLBACK: dict[str, str] = {
    "queued": "*",
    "fetching": "?",
    "waiting_for_base": "_",
    "preparing": ".",
    "ready": "+",
    "in_review": "~",
    "reviewed": "#",
    "approved": "v",
    "blocked": "x",
    "merged": "X",
    "closed": "X",
    "prep_failed": "!",
    "stale": "@",
}

def derive(row: QueueRow, *, ascii_only: bool = False) -> RowState:
    """Derive a single RowState from the row. Precedence (highest first):
      merged/closed → 'merged' (closed maps to same icon),
      prep_status == failed → 'prep_failed',
      taken_at fresh → 'in_review',
      status in {approved} → 'approved',
      status in {reviewed, comments, reminded} → 'reviewed',
      prep_status == preparing → 'preparing',
      prep_status == waiting_for_base → 'waiting_for_base',
      prep_status == pending → 'queued',
      ready_for_review True → 'ready',
      fallback → 'queued'.
    """
```

The `color` field is advisory; the renderer can ignore it for now (use it later for themes).

### 3.3 `tui.widgets.queue_table.QueueTable`

A `textual.widgets.DataTable` subclass.

```python
from textual.widgets import DataTable

class QueueTable(DataTable):
    """Read-only queue list.

    Columns: ['', '#', 'repo', 'title', 'branch', 'age']
    The first column is the icon. '#' is the PR number.

    Public API:
      load(snapshot: QueueSnapshot, *, ascii_only: bool = False) -> None
          Replace all rows from the snapshot. Preserves cursor position by pr_url
          when possible (look up the previously focused pr_url after reload).
      selected_pr_url() -> str | None
          The pr_url of the currently highlighted row, or None if empty.
    """
```

DX requirements:
- Cursor type = `row`.
- `zebra_stripes = True`.
- Column widths: icon=2, #=8, repo=24, title=40, branch=18, age=8 (Textual permits content-based defaults; set explicit widths only if rendering looks ragged).
- `age` is a relative-time string: "2m", "1h", "3d", "12d" derived from `last_checked_at`.
- Empty state: when `snapshot.missing` is True OR `snapshot.rows` is empty, the table shows ONE row with text spanning ('—', '—', 'no PRs', f'(queue: {snapshot.queue_path})', '—', '—').

### 3.4 `tui.widgets.detail_pane.DetailPane`

A `textual.widgets.Static` subclass that renders rich markdown-ish text for the focused row.

```python
class DetailPane(Static):
    def show(self, row: QueueRow | None) -> None: ...
```

Layout (vertical):
```
{repo}#{number}
Title:   {title or '(no title fetched)'}
Author:  {author or '—'}
Branch:  {head[:8]} → {target_branch or '—'}
Status:  {status}  ·  prep: {prep_status or '—'}
Lock:    {taken_at or 'free'}
Slack:   {slack_permalink or '—'}
Last reviewed: {last_reviewed_at or '—'}{' (same head)' if last_reviewed_head_sha == head_sha else ''}
```

If `row is None`, render: `(no row selected)`.

### 3.5 `tui.widgets.header_bar.HeaderBar`

A `textual.widgets.Static` rendered in dock=top.

Format: `adk · queue: {total} · ready: {ready_count} · in-review: {in_review_count}/4 · platform: {platform_summary}`

`update(snapshot: QueueSnapshot) -> None` replaces the content.

### 3.6 `tui.widgets.footer_bar.FooterBar`

A `textual.widgets.Static` rendered in dock=bottom.

Format: `[?] help  [f] filter:{mode}  [S] sort:{mode}  [j/k] nav  [q] quit  ·  [s] sync (disabled)  [r] run (disabled)`

`update(filter_mode, sort_mode) -> None`.

### 3.7 `tui.widgets.help_screen.HelpScreen`

A `textual.screen.ModalScreen` that lists every binding in a centered panel:

```
adk TUI · keys

  q              quit
  ?              this help
  f              cycle filter
  S              cycle sort
  j / down       move cursor down
  k / up         move cursor up
  g / home       jump to first row
  G / end        jump to last row
  enter          (read-only — no action yet)
  escape         close this help / clear filter
```

Press `?` or `escape` to dismiss.

### 3.8 `tui.app.AdkApp` and `main()`

```python
class AdkApp(App):
    CSS_PATH = "styles.tcss"
    BINDINGS = [...]  # see §3.9
    TITLE = "adk"

    def __init__(self, *, queue_path: Path | None = None, ascii_only: bool = False, poll_interval: float = 2.0) -> None: ...

    def compose(self) -> ComposeResult: ...
    async def on_mount(self) -> None: ...
    # action_* methods for each binding


def main(argv: list[str] | None = None) -> int:
    """Entry point. Parses --queue-path / --ascii / --poll-interval, runs AdkApp.run().
    Returns the app's exit code (0 on clean quit).
    """
```

`main` must:
- Parse args minimally with argparse (`--queue-path`, `--ascii`, `--poll-interval`).
- Catch `ImportError` for `textual` at the top and print a friendly message + install command + return 2 (but since we add textual to requirements.txt, this is belt-and-braces).
- Catch `KeyboardInterrupt` and return 130.

### 3.9 Bindings (defined on `AdkApp`)

```python
BINDINGS = [
    Binding("q", "quit", "quit"),
    Binding("?", "help", "help"),
    Binding("f", "cycle_filter", "filter"),
    Binding("S", "cycle_sort", "sort"),
    Binding("j", "cursor_down", show=False),
    Binding("k", "cursor_up", show=False),
    Binding("g", "cursor_home", show=False),
    Binding("G", "cursor_end", show=False),
    Binding("escape", "escape", show=False),
]
```

`action_cursor_*` forward to the `QueueTable`'s `action_cursor_down/up` etc. via `query_one(QueueTable)`.

`action_escape` is a no-op in α+β (closes future modals; here it only matters for the help screen, which handles its own escape).

### 3.10 `tui.styles.tcss`

Default dark theme (Textual default colours are fine). At minimum:
- Header docks top, height=1.
- Footer docks bottom, height=1.
- Main container is a horizontal split: QueueTable (2fr) left, DetailPane (1fr) right.
- DataTable header row bold.

Keep it ~30 lines. We can iterate themes later.

## 4. Tests (Agent C)

All tests live under `tui/tests/`. Use Textual's `Pilot` for async UI tests.

### 4.1 `tui/tests/fixtures/sample_queue.json5`

Hand-crafted fixture with at least 6 rows covering: a ready GH PR, a preparing GH PR, a merged GH PR, a ready Bitbucket PR, a row with `taken_at` fresh, a row with `prep_status=failed`. Use the same shape as the real queue (see §0 of this spec — agents B/C read `~/.agents-devkit/config/pr-queue.json5` for reference shape).

### 4.2 `tui/tests/conftest.py`

Provides:
- `fake_queue_path` fixture: writes the sample fixture into a tmp_path and returns the path.
- `tui_app` fixture: returns `AdkApp(queue_path=fake_queue_path, poll_interval=0.1)`.
- `frozen_now` fixture: returns a `datetime` ~ 2026-05-21T18:00:00Z so the ready_for_review predicate is deterministic against the fixture.

### 4.3 Test list

- `test_model.py`
  - `test_snapshot_parses_all_rows`
  - `test_snapshot_filter_open_excludes_merged`
  - `test_snapshot_filter_ready_is_subset`
  - `test_snapshot_sort_fifo_oldest_first`
  - `test_snapshot_sort_repo_groups`
  - `test_has_changed_after_mtime_bump`
  - `test_snapshot_empty_when_file_missing`
  - `test_ready_count_matches_helper`
  - `test_platform_summary_mixed`
- `test_app_launch.py`
  - `test_app_starts_and_quits`  (Pilot: press q, assert exited)
  - `test_app_renders_header`
  - `test_help_screen_opens_and_closes`
- `test_queue_render.py`
  - `test_rows_visible`
  - `test_empty_state_when_queue_missing`
  - `test_detail_pane_updates_on_cursor_move`
- `test_keybindings.py`
  - `test_f_cycles_filter`
  - `test_capital_s_cycles_sort`
  - `test_jk_moves_cursor`

Keep tests under ~250 LOC total. Don't snapshot the entire screen; assert on the widget's state instead (e.g. `app.query_one(QueueTable).row_count`, `app.query_one(HeaderBar).renderable`).

### 4.4 Running tests

Tests run as part of the existing pytest invocation:

```bash
python3 -m pytest tui/tests/ -q
```

Add NO conftest-merging tricks; `tui/tests/conftest.py` is self-contained.

## 5. Wiring `bin/adk` (Agent C)

`bin/adk` currently prints USAGE when called with no args (or some equivalent). Make it:

1. If `argv[1:]` is empty (or is exactly `--queue-path X` / `--ascii` / `--poll-interval X` / `-h` for the TUI), import `tui.app` lazily and call `tui.app.main(argv[1:])`.
2. Else dispatch as today.
3. The lazy import is at the call site so existing `adk <verb>` invocations do not pay the textual import cost.
4. Add the TUI's `adk` (no-args) entry to the top of the existing USAGE block, with one-line wording.

Edge: tab-completion `adk --help` should keep printing CLI usage, not launch the TUI. Detect this by treating `-h` or `--help` (with no other args) as "show top-level help" — the TUI's own help is `?` inside the app.

## 6. Dependencies

Append to `skills/adk-cli/scripts/requirements.txt`:

```
textual>=0.86
```

Do not pin the upper bound. Textual 8.x is current; 9.x has not landed yet.

## 7. Definition of done

Three independent checks:

1. `python3 -m pytest tui/tests/ -q` → all tests pass.
2. `python3 -m pytest skills/adk-cli/scripts/tests/ skills/adk-pr-review/scripts/tests/ -q` → still 412 passing.
3. Manual smoke (Agent C reports back): `adk` launches the TUI against the real `~/.agents-devkit/config/pr-queue.json5`, `q` exits, `?` opens help, `f` cycles filter, `S` cycles sort, arrow keys move cursor, detail pane updates.

## 8. Constraints — read this before writing code

- **Never block the event loop.** Use `set_interval` for poll-the-queue logic. Reading `queue_io.read_queue` synchronously is OK at 2s cadence — it's a small JSON5 file.
- **No network calls.** This is a read-only viewer over local state.
- **Reuse existing helpers.** `queue_io.read_queue`, `queue_io.ready_for_review`, `queue_io.dedupe_key`, `queue_io.TAKEN_LOCK_MAX_AGE_SECONDS`. Do not duplicate.
- **No mutation of queue state.** This slice never writes to the queue. Even `enter` is read-only.
- **Match repo conventions.** Type hints, `from __future__ import annotations`, no excessive comments.
- **Skill-cleanly when not implemented.** Greyed-out actions show `(disabled)` in the footer so the user knows they're coming.

## 9. Agent contracts (file ownership — strict; no cross-writes)

- **Agent A — widgets + app shell**: writes `tui/__init__.py`, `tui/app.py`, `tui/styles.tcss`, every file under `tui/widgets/`.
- **Agent B — model layer**: writes every file under `tui/model/`. Reads queue_io for the helpers.
- **Agent C — tests + integration**: writes every file under `tui/tests/` and edits `bin/adk` + `skills/adk-cli/scripts/requirements.txt`. Reads the spec for the interface contracts.

If one agent finds a problem in another's slice, it surfaces the problem in its report (does not edit the other slice). Coordination falls back to the leader (the main thread).

## 10. Reporting back

Each agent ends its run with:

- Files created / modified (path list).
- Test status (pass/fail + a count).
- Anything that didn't fit (with a one-line reason).
- Any blocker that would have required cross-agent coordination (none expected if everyone follows §9).
