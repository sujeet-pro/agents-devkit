from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import skill_preflight


def test_preflight_reports_optional_cli_degraded(monkeypatch):
    monkeypatch.setattr(skill_preflight.shutil, "which", lambda name: None)

    result = skill_preflight.preflight("adk-pr-review", runner="inherit")

    assert result["status"] in {"blocked", "degraded"}
    optional = [c for c in result["cli"] if c["name"].startswith("scip-")]
    assert optional
    assert all(c["fallback"] for c in optional)


def test_preflight_inherit_runner_never_requires_binary():
    result = skill_preflight.preflight("adk-pr-review", runner="inherit")

    assert result["runner"]["mode"] == "inherit"
    assert result["runner"]["available"] is True
