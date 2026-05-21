from __future__ import annotations

from textual.widgets import Static

from tui.model.sync_plan_model import SyncPlanSnapshot

_ICONS = {
    "pending":  ("…",  "[--]"),
    "running":  ("⚡", "[..]"),
    "ok":       ("✓",  "[ok]"),
    "warn":     ("⚠",  "[wn]"),
    "failed":   ("✗",  "[fl]"),
    "skipped":  ("↷",  "[sk]"),
}


class SyncPlanPane(Static):
    def __init__(self) -> None:
        super().__init__("(no sync run yet — press `s` to start)", markup=False)

    def update_snapshot(self, snapshot: SyncPlanSnapshot | None, *, ascii_only: bool = False) -> None:
        if snapshot is None:
            self.update("(no sync run yet — press `s` to start)")
            return
        header = _format_header(snapshot)
        body = [_format_step(s, ascii_only=ascii_only) for s in snapshot.steps]
        self.update("\n".join([header, *body]))


def _format_header(snap: SyncPlanSnapshot) -> str:
    done = sum(1 for s in snap.steps if s.status in ("ok", "warn", "failed", "skipped"))
    total = len(snap.steps)
    if snap.completed_at is not None:
        outcome = "✓ done" if (snap.rc or 0) == 0 else "✗ done (with failures)"
        return f"Sync plan ({outcome} · {done}/{total} steps)"
    return f"Sync plan (running · {done}/{total} steps)"


def _format_step(step, *, ascii_only: bool) -> str:
    icon = _ICONS.get(step.status, _ICONS["pending"])[1 if ascii_only else 0]
    return f"  {icon}  {step.name}"
