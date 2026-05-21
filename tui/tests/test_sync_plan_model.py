from __future__ import annotations

import json
import os
import time
from pathlib import Path

from tui.model.sync_plan_model import SyncPlanModel, SyncPlanSnapshot


def test_snapshot_returns_none_when_missing(fake_plan_path: Path) -> None:
    model = SyncPlanModel(plan_path=fake_plan_path)
    assert not fake_plan_path.exists()
    assert model.snapshot() is None


def test_has_changed_true_initially_when_missing(fake_plan_path: Path) -> None:
    model = SyncPlanModel(plan_path=fake_plan_path)
    # First call: no prior mtime → treat as "changed" so the pane gets the
    # initial "(no sync run yet)" render.
    assert model.has_changed() is True


def test_snapshot_parses_valid_plan(sync_plan_in_progress: Path) -> None:
    model = SyncPlanModel(plan_path=sync_plan_in_progress)
    snap = model.snapshot()
    assert isinstance(snap, SyncPlanSnapshot)
    assert snap.queue == "/tmp/q.json5"
    assert snap.completed_at is None
    assert snap.rc is None
    assert len(snap.steps) == 8
    assert snap.steps[0].name == "pr-scan"
    assert snap.steps[0].status == "ok"
    assert snap.steps[2].status == "running"
    assert snap.steps[3].status == "pending"


def test_snapshot_returns_none_on_corrupt_json(fake_plan_path: Path) -> None:
    fake_plan_path.write_text("{ this is not json")
    model = SyncPlanModel(plan_path=fake_plan_path)
    # No exception leaks out.
    assert model.snapshot() is None


def test_snapshot_returns_none_on_wrong_version(fake_plan_path: Path) -> None:
    fake_plan_path.write_text(json.dumps({"version": 999, "steps": []}))
    model = SyncPlanModel(plan_path=fake_plan_path)
    assert model.snapshot() is None


def test_has_changed_false_after_snapshot_if_mtime_unchanged(
    sync_plan_in_progress: Path,
) -> None:
    model = SyncPlanModel(plan_path=sync_plan_in_progress)
    model.snapshot()
    assert model.has_changed() is False


def test_has_changed_true_after_mtime_bump(sync_plan_in_progress: Path) -> None:
    model = SyncPlanModel(plan_path=sync_plan_in_progress)
    model.snapshot()
    assert model.has_changed() is False
    new_mtime = sync_plan_in_progress.stat().st_mtime + 5
    os.utime(sync_plan_in_progress, (new_mtime, new_mtime))
    assert model.has_changed() is True


def test_snapshot_handles_missing_optional_fields(fake_plan_path: Path) -> None:
    """A plan with only `version` + `steps` should still parse — defaults fill
    in the rest. Resilience requirement from SPEC §2."""
    fake_plan_path.write_text(
        json.dumps({"version": 1, "steps": [
            {"name": "x"},
        ]})
    )
    model = SyncPlanModel(plan_path=fake_plan_path)
    snap = model.snapshot()
    assert snap is not None
    assert len(snap.steps) == 1
    assert snap.steps[0].name == "x"
    assert snap.steps[0].status == "pending"
