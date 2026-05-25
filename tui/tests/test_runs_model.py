from __future__ import annotations

import json
from pathlib import Path

from tui.model.runs_model import RunsModel


def test_runs_model_reads_recent_runs(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    runs.mkdir()
    (runs / "r1.json").write_text(json.dumps({
        "version": 1,
        "run_id": "r1",
        "task_type": "pr-review-all",
        "status": "running",
        "started_by": "cli",
        "runner": "cursor",
        "parallel": 4,
        "selected": 3,
        "started_at": "2026-05-25T08:00:00Z",
        "updated_at": "2026-05-25T08:01:00Z",
        "run_dir": "/tmp/run",
        "steps": [{"name": "pr-sync", "status": "running", "log_path": "/tmp/pr-sync.log"}],
        "results": [{"pr_url": "https://github.com/acme/foo/pull/1", "log": "/tmp/pr.log"}],
        "artifacts": {"report": "/tmp/report.md"},
        "workers": ["w1"],
        "links": {"report": "file:///tmp/report.md"},
    }))

    rows = RunsModel(runs_dir=runs).snapshot()

    assert len(rows) == 1
    assert rows[0].run_id == "r1"
    assert rows[0].task_type == "pr-review-all"
    assert rows[0].selected == 3
    assert rows[0].links["report"] == "file:///tmp/report.md"
    assert rows[0].run_dir == "/tmp/run"
    assert rows[0].steps[0]["log_path"] == "/tmp/pr-sync.log"
    assert rows[0].results[0]["log"] == "/tmp/pr.log"
    assert rows[0].artifacts["report"] == "/tmp/report.md"
