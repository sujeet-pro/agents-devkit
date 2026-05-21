from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import Static

if TYPE_CHECKING:
    from tui.model.queue_model import QueueRow


class DetailPane(Static):
    def __init__(self) -> None:
        super().__init__("(no row selected)", markup=False)

    def show(self, row: QueueRow | None) -> None:
        if row is None:
            self.update("(no row selected)")
            return

        head = row.head_sha or "—"
        head_short = head[:8] if head != "—" else "—"
        target = row.target_branch or "—"
        title = row.title or "(no title fetched)"
        author = row.author or "—"
        prep = row.prep_status or "—"
        lock = row.taken_at or "free"
        slack = row.slack_permalink or "—"
        last_reviewed = row.last_reviewed_at or "—"

        same_head = ""
        if (
            row.last_reviewed_head_sha is not None
            and row.head_sha is not None
            and row.last_reviewed_head_sha == row.head_sha
        ):
            same_head = " (same head)"

        lines = [
            f"{row.repo}#{row.number}",
            f"Title:   {title}",
            f"Author:  {author}",
            f"Branch:  {head_short} → {target}",
            f"Status:  {row.status}  ·  prep: {prep}",
            f"Lock:    {lock}",
            f"Slack:   {slack}",
            f"Last reviewed: {last_reviewed}{same_head}",
        ]
        self.update("\n".join(lines))
