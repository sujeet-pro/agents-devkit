#!/usr/bin/env python3
"""scip_runner.py — run scip-* indexers for each language present in the worktree.

Detects: scip-typescript, scip-python, scip-go, scip-java. Missing binaries → mark
not_installed in code-index/meta-scip.json and proceed.

Usage:
  python3 scip_runner.py --task-dir <path> --worktree <path> [--langs ts,py,go,java] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import which, write_json, emit_json, get_logger  # noqa: E402


LANG_BIN = {
    "ts": "scip-typescript",
    "py": "scip-python",
    "go": "scip-go",
    "java": "scip-java",
}

LANG_DETECT_GLOBS = {
    "ts": ("*.ts", "*.tsx"),
    "py": ("*.py",),
    "go": ("*.go",),
    "java": ("*.java",),
}


def detect_languages(worktree: Path) -> list[str]:
    """Return which scip-supported languages have any source files in the worktree."""
    found = []
    for lang, globs in LANG_DETECT_GLOBS.items():
        for g in globs:
            try:
                # cheap probe: stop at first hit.
                hit = next(worktree.rglob(g), None)
            except OSError:
                hit = None
            if hit:
                found.append(lang)
                break
    return found


def run_indexer(lang: str, worktree: Path, out_dir: Path, log) -> dict:
    bin_name = LANG_BIN[lang]
    if not which(bin_name):
        return {"lang": lang, "status": "not_installed", "binary": bin_name}
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "index.scip"
    cmd = {
        "ts":   [bin_name, "index", "--output", str(out_file)],
        "py":   [bin_name, "index", "--output", str(out_file), "."],
        "go":   [bin_name, "--output", str(out_file)],
        "java": [bin_name, "--output", str(out_file)],  # may need project layout
    }[lang]
    log.info("scip(%s): %s", lang, " ".join(cmd))
    started = time.time()
    try:
        cp = subprocess.run(cmd, cwd=worktree, capture_output=True, text=True, timeout=600)
    except subprocess.TimeoutExpired:
        (out_dir / "build.log").write_text("timeout after 600s\n", encoding="utf-8")
        return {"lang": lang, "status": "timeout", "binary": bin_name}
    (out_dir / "build.log").write_text(
        (cp.stdout or "") + "\n--- STDERR ---\n" + (cp.stderr or ""),
        encoding="utf-8"
    )
    if cp.returncode != 0:
        return {"lang": lang, "status": "failed", "binary": bin_name,
                "returncode": cp.returncode, "elapsed_s": round(time.time() - started, 2)}
    size = out_file.stat().st_size if out_file.exists() else 0
    return {
        "lang": lang, "status": "ok", "binary": bin_name,
        "path": str(out_file), "size_bytes": size,
        "elapsed_s": round(time.time() - started, 2),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--worktree", required=True)
    ap.add_argument("--langs", default="", help="comma-separated subset to run; default = autodetect")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    worktree = Path(args.worktree)
    log = get_logger("scip_runner", task_dir)
    scip_root = task_dir / "code-index" / "scip"
    scip_root.mkdir(parents=True, exist_ok=True)

    if args.langs:
        langs = [s.strip() for s in args.langs.split(",") if s.strip()]
    else:
        langs = detect_languages(worktree)

    results = [run_indexer(lang, worktree, scip_root / lang, log) for lang in langs]
    summary = {
        "task_dir": str(task_dir),
        "scip_root": str(scip_root),
        "languages_detected": langs,
        "results": results,
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "not_installed": sum(1 for r in results if r["status"] == "not_installed"),
        "failed": sum(1 for r in results if r["status"] not in ("ok", "not_installed")),
    }
    write_json(task_dir / "code-index" / "meta-scip.json", summary)
    if args.json:
        return emit_json(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
