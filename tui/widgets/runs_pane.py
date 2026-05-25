from __future__ import annotations

from textual.widgets import Static

from tui.model.runs_model import RunRow


class RunsPane(Static):
    def __init__(self) -> None:
        super().__init__("(no runs yet)", markup=False)

    def update_runs(self, rows: list[RunRow]) -> None:
        if not rows:
            self.update("(no runs yet)")
            return
        running = sum(1 for row in rows if row.status == "running")
        failed = sum(1 for row in rows if row.status == "failed")
        ok = sum(1 for row in rows if row.status == "ok")
        rendered = [f"Overall operations: {running} running · {ok} ok · {failed} failed"]
        for row in rows:
            rendered.append(_format_row(row))
        self.update("\n".join(rendered))


def _format_row(row: RunRow) -> str:
    bits = [row.status or "unknown", row.task_type or row.run_id]
    if row.selected is not None:
        bits.append(f"{row.selected} selected")
    if row.parallel is not None:
        bits.append(f"par={row.parallel}")
    if row.runner:
        bits.append(row.runner)
    if _has_logs(row):
        bits.append("logs: L")
    return "  " + "  ·  ".join(bits)


def _has_logs(row: RunRow) -> bool:
    if any(step.get("log_path") for step in row.steps):
        return True
    return any(result.get("log") for result in row.results)
