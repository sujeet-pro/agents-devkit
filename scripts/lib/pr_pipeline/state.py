"""pr_pipeline/state.py — per-PR state machine.

PRState travels through the six stages:
  import → sync → index → review → validate → post

Each stage call records a StageResult. terminal() is True when the PR has
reached "post" (ok/skipped) or any stage has failed.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

StageStatus = Literal["pending", "running", "ok", "failed", "skipped"]
StageName = Literal["import", "sync", "index", "review", "validate", "post"]

_STAGE_ORDER: list[StageName] = ["import", "sync", "index", "review", "validate", "post"]


@dataclass
class StageResult:
    stage: StageName
    status: StageStatus
    reason: str = ""
    elapsed_s: float = 0.0
    artifacts: dict = field(default_factory=dict)


@dataclass
class PRState:
    pr_url: str
    repo: str
    pr_number: int
    task_dir: Path
    current_stage: StageName = "import"
    results: dict = field(default_factory=dict)  # StageName -> StageResult

    def advance(self, result: StageResult) -> None:
        """Record a completed stage result and advance current_stage to the next."""
        self.results[result.stage] = result
        if result.status in ("ok", "skipped"):
            idx = _STAGE_ORDER.index(result.stage)
            if idx + 1 < len(_STAGE_ORDER):
                self.current_stage = _STAGE_ORDER[idx + 1]
            else:
                # All stages done — current_stage stays at "post"
                self.current_stage = "post"
        # On failure we leave current_stage pointing at the failed stage so
        # callers can report which stage failed.

    def terminal(self) -> bool:
        """True when the PR is done: either all stages succeeded/skipped,
        or any stage failed."""
        for stage in _STAGE_ORDER:
            r = self.results.get(stage)
            if r is None:
                return False
            if r.status == "failed":
                return True
            if r.status in ("ok", "skipped"):
                continue
        # All stages have a terminal result (ok/skipped) — done.
        return True

    def failed(self) -> bool:
        return any(
            r.status == "failed" for r in self.results.values()
        )

    def last_result(self) -> Optional[StageResult]:
        for stage in reversed(_STAGE_ORDER):
            r = self.results.get(stage)
            if r is not None:
                return r
        return None
