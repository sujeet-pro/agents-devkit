"""Tests for supporting-doc evidence audit."""
from __future__ import annotations

import json
from pathlib import Path

import audit_supporting_docs


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj), encoding="utf-8")


def test_approve_with_fetched_docs_requires_doc_reference(tmp_path):
    task = tmp_path / "repo_pr-1"
    _write_json(task / "docs" / "index.json", {
        "results": [{"status": "fetched", "path": "docs/confluence/ABC.md"}],
    })
    _write_json(task / "pr-review" / "findings-final.json", {
        "recommendation": "approve",
        "summary": "No issues.",
        "findings": [],
    })

    out = audit_supporting_docs.audit_task(task)

    assert out["status"] == "missing-doc-reference"


def test_summary_doc_reference_satisfies_audit(tmp_path):
    task = tmp_path / "repo_pr-1"
    _write_json(task / "docs" / "index.json", {
        "results": [{"status": "fetched", "path": "docs/confluence/ABC.md"}],
    })
    _write_json(task / "pr-review" / "findings-final.json", {
        "recommendation": "approve",
        "summary": "Docs matched the PR body: docs/confluence/ABC.md",
        "findings": [],
    })

    out = audit_supporting_docs.audit_task(task)

    assert out["status"] == "ok"
