from __future__ import annotations

import re

from textual.widgets import Static

from tui.model.workers_model import WorkerRow


class WorkersPane(Static):
    def __init__(self) -> None:
        super().__init__("(no active workers)", markup=False)

    def update_workers(self, rows: list[WorkerRow], *, ascii_only: bool = False) -> None:
        # Stale rows are hidden by default (the user only sees live workers).
        live = [r for r in rows if not r.is_stale]
        if not live:
            self.update("(no active workers)")
            return
        header = f"Workers ({len(live)} active)"
        body = [_format_row(r, ascii_only=ascii_only) for r in live]
        self.update("\n".join([header, *body]))


def _format_row(row: WorkerRow, *, ascii_only: bool) -> str:
    pr_short = _shorten(row.pr_url)
    age = _format_age(row.age_s)
    glyph = "⚙↻" if not ascii_only else "~"
    return f"  {glyph}  {pr_short}  ·  {row.task_type}/{row.current_phase}  ·  {row.agent}  ·  {age}"


def _shorten(pr_url: str) -> str:
    # https://github.com/acme/foo/pull/42 → acme/foo#42
    # https://bitbucket.org/o/r/pull-requests/5 → o/r#5
    m = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    m = re.search(r"bitbucket\.org/([^/]+)/([^/]+)/pull-requests/(\d+)", pr_url)
    if m:
        return f"{m.group(1)}/{m.group(2)}#{m.group(3)}"
    return pr_url


def _format_age(seconds: float) -> str:
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = int(seconds // 60)
    if minutes < 60:
        return f"{minutes}m"
    hours = int(minutes // 60)
    if hours < 24:
        return f"{hours}h"
    return f"{int(hours // 24)}d"
