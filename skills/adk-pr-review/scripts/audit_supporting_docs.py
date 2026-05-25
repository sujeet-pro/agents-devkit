#!/usr/bin/env python3
"""Audit whether PR-review findings cite fetched supporting docs."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parents[3] / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_skill_home  # noqa: E402


def _task_dirs(root: Path) -> list[Path]:
    if (root / "pr-review").exists():
        return [root]
    if not root.exists():
        return []
    return sorted(p for p in root.iterdir() if (p / "pr-review").exists())


def _doc_refs(blob: dict) -> list[str]:
    refs: list[str] = []
    for finding in blob.get("findings") or []:
        for ev in finding.get("evidence") or []:
            ref = str(ev.get("ref") or "")
            if ref.startswith("docs/") or "/docs/" in ref:
                refs.append(ref)
    summary = str(blob.get("summary") or "")
    if "docs/" in summary:
        refs.append("summary")
    return refs


def audit_task(task_dir: Path) -> dict:
    docs_idx_path = task_dir / "docs" / "index.json"
    findings_path = task_dir / "pr-review" / "findings-final.json"
    if not findings_path.exists():
        return {"task_dir": str(task_dir), "status": "skipped", "reason": "missing findings-final.json"}

    docs_idx = json.loads(docs_idx_path.read_text(encoding="utf-8")) if docs_idx_path.exists() else {"results": []}
    fetched = [r for r in docs_idx.get("results", []) if str(r.get("status")) == "fetched"]
    findings = json.loads(findings_path.read_text(encoding="utf-8"))
    refs = _doc_refs(findings)
    required = bool(fetched and findings.get("recommendation") == "approve")
    ok = (not required) or bool(refs)
    return {
        "task_dir": str(task_dir),
        "status": "ok" if ok else "missing-doc-reference",
        "fetched_docs": len(fetched),
        "doc_refs": refs,
        "recommendation": findings.get("recommendation"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Audit supporting-doc references in PR-review findings")
    ap.add_argument("--root", default=str(adk_skill_home("pr-review")))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    results = [audit_task(td) for td in _task_dirs(Path(args.root).expanduser())]
    failed = [r for r in results if r.get("status") == "missing-doc-reference"]
    out = {"count": len(results), "failed": len(failed), "results": results}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"{len(results)} task(s) checked · {len(failed)} missing doc references")
        for r in failed:
            print(f"  - {r['task_dir']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
