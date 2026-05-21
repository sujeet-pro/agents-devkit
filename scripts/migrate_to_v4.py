#!/usr/bin/env python3
"""migrate_to_v4.py — one-shot, idempotent migration of ~/.agents-devkit/ to v4 layout.

Per `docs/plans/adk-v4-overhaul.md` §8 P7:
  • PR queue is rewritten in place via queue_io's read-shim (P1 + auto-runs
    on first read by anything that consumes the queue).
  • `~/.agents-devkit/pr-reviews/`  →  `~/.agents-devkit/skill-pr-review/`
  • For each task folder, the well-known PR-review files (pr.json,
    findings.json, etc. — see _common.PR_REVIEW_FILES) move into a
    `pr-review/` subfolder.
  • `code/`, `code-index/`, `scip/`, `docs/` STAY at the top of the task
    folder.
  • Empty `~/.agents-devkit/memory/` is removed.
  • Other legacy area dirs (`investigations/`, `reviews/`, `sync/`,
    `setup/`, `explain/`) are renamed to their `skill-*` v4 names IF the
    legacy one is present AND the v4 one is absent.

Preservation contract: MOVE, never DELETE. If a destination already
exists, the source is preserved + a warning emitted (this means a
previous migration partially ran or a v4 task folder coexists with a
legacy one; manual reconciliation needed).

Usage:
  python3 scripts/migrate_to_v4.py [--dry-run] [--yes]

--dry-run shows what would happen, no side effects.
--yes confirms the live migration (default refuses to run without it,
      to prevent accidents from sourced shells).

Exit codes:
  0 — migration succeeded (or no-op)
  1 — at least one move failed (idempotent re-run may help)
  2 — refused to run (missing --yes outside dry-run)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))

# Areas to rename: (legacy_name, v4_name).
SKILL_AREA_RENAMES = [
    ("pr-reviews", "skill-pr-review"),
    ("investigations", "skill-investigate"),
    ("reviews", "skill-review"),
    ("sync", "skill-sync"),
    ("setup", "skill-setup"),
    ("explain", "skill-explain"),
    # NOT renamed: 'improve' (top-level data dir per §3 architecture),
    # 'repos' (own structure), 'config', 'memory' (handled separately).
]

# Well-known PR-review files that move into pr-review/ subfolder.
PR_REVIEW_FILES = frozenset({
    "pr.json", "pr-comments.json", "diff.patch", "precis.md",
    "findings.json", "validated-findings.json", "initial-findings.json",
    "findings-final.json", "validation-report.json",
    "triage.json", "triage-state.json",
    "posting-plan.json", "post-result.json", "comment-actions.json",
    "findings.md", "report.md",
    "state.json", "queue-context.json",
    "review.log",
})


def _emit(action: str, src: Path, dst: Path | None = None, **extra) -> dict:
    out = {"action": action, "src": str(src)}
    if dst is not None:
        out["dst"] = str(dst)
    out.update(extra)
    return out


def migrate_skill_area_dirs(*, dry_run: bool) -> list[dict]:
    """Rename each legacy area dir to its skill-<stem> v4 name."""
    out = []
    for legacy_name, v4_name in SKILL_AREA_RENAMES:
        legacy = ADK_HOME / legacy_name
        v4 = ADK_HOME / v4_name
        if not legacy.exists():
            continue
        if v4.exists():
            out.append(_emit("skip_conflict", legacy, v4,
                             reason="both legacy and v4 dir present; manual reconciliation needed"))
            continue
        if dry_run:
            out.append(_emit("would_rename_dir", legacy, v4))
            continue
        try:
            legacy.rename(v4)
            out.append(_emit("renamed_dir", legacy, v4))
        except OSError as e:
            out.append(_emit("error", legacy, v4, error=str(e)))
    return out


def migrate_task_folders(*, dry_run: bool) -> list[dict]:
    """For every task folder under skill-pr-review/, move the well-known
    PR-review files into a `pr-review/` subfolder. Files NOT in
    PR_REVIEW_FILES stay where they are (e.g. code/, code-index/, scip/,
    docs/ are subdirectories; they're not in the set so they stay top-level).

    In dry-run mode, the area-dir rename hasn't actually happened, so this
    function also looks at the legacy `pr-reviews/` root to preview what
    file moves WOULD happen post-rename.
    """
    out = []
    roots = []
    v4_root = ADK_HOME / "skill-pr-review"
    legacy_root = ADK_HOME / "pr-reviews"
    if v4_root.exists():
        roots.append(v4_root)
    if dry_run and legacy_root.exists():
        roots.append(legacy_root)
    if not roots:
        return out
    root = roots[0]
    # If both are listed (dry-run only), prefer the legacy root for the preview.
    if dry_run and legacy_root.exists():
        root = legacy_root
    for task_dir in sorted(root.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        pr_review_subdir = task_dir / "pr-review"
        moved = 0
        for fname in PR_REVIEW_FILES:
            legacy_path = task_dir / fname
            if not legacy_path.exists():
                continue
            v4_path = pr_review_subdir / fname
            if v4_path.exists():
                out.append(_emit("skip_conflict_file", legacy_path, v4_path,
                                 reason="both top-level and pr-review/ copies exist"))
                continue
            if dry_run:
                out.append(_emit("would_move_file", legacy_path, v4_path))
                moved += 1
                continue
            try:
                pr_review_subdir.mkdir(parents=True, exist_ok=True)
                legacy_path.rename(v4_path)
                out.append(_emit("moved_file", legacy_path, v4_path))
                moved += 1
            except OSError as e:
                out.append(_emit("error", legacy_path, v4_path, error=str(e)))
        if moved:
            out.append(_emit("task_summary", task_dir, moved=moved,
                             will_move=dry_run))
    return out


def remove_empty_memory(*, dry_run: bool) -> list[dict]:
    """Drop ~/.agents-devkit/memory/ ONLY if empty. Per plan §8 P2: 'memory/
    removed if empty'.
    """
    mem = ADK_HOME / "memory"
    out: list[dict] = []
    if not mem.exists():
        return out
    try:
        if any(mem.iterdir()):
            out.append(_emit("skip_non_empty", mem,
                             reason="contains user content; not removed"))
            return out
    except OSError as e:
        out.append(_emit("error", mem, error=str(e)))
        return out
    if dry_run:
        out.append(_emit("would_rmdir", mem))
        return out
    try:
        mem.rmdir()
        out.append(_emit("rmdir", mem))
    except OSError as e:
        out.append(_emit("error", mem, error=str(e)))
    return out


def verify(*, dry_run: bool) -> list[dict]:
    """Post-migration sanity check: for each skill-pr-review/<task>/ folder,
    confirm code-index/meta.json is readable (if present). Doesn't fail the
    migration; surfaces problems in the report.
    """
    out: list[dict] = []
    root = ADK_HOME / "skill-pr-review"
    if not root.exists():
        return out
    indices_ok = 0
    indices_missing = 0
    for task_dir in sorted(root.iterdir()):
        if not task_dir.is_dir() or task_dir.name.startswith("."):
            continue
        meta = task_dir / "code-index" / "meta.json"
        if meta.exists():
            try:
                blob = json.loads(meta.read_text())
                if blob.get("embed_model"):
                    indices_ok += 1
                else:
                    indices_missing += 1
                    out.append(_emit("verify_warning", meta,
                                     reason="meta.json missing embed_model"))
            except Exception as e:
                indices_missing += 1
                out.append(_emit("verify_error", meta, error=str(e)))
    if indices_ok or indices_missing:
        out.append(_emit("verify_summary", root,
                         indices_ok=indices_ok,
                         indices_missing=indices_missing))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="migrate_to_v4",
                                 description="Migrate ~/.agents-devkit/ to v4 layout. MOVE-only, idempotent.")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would happen; no side effects")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="confirm the live migration (required outside --dry-run)")
    args = ap.parse_args(argv)

    if not args.dry_run and not args.yes:
        sys.stderr.write(
            "Refusing to run without --yes (or --dry-run).\n"
            "Re-run with --dry-run to preview, or --yes to apply.\n"
        )
        return 2

    results: list[dict] = []
    results += migrate_skill_area_dirs(dry_run=args.dry_run)
    results += migrate_task_folders(dry_run=args.dry_run)
    results += remove_empty_memory(dry_run=args.dry_run)
    results += verify(dry_run=args.dry_run)

    n_errors = sum(1 for r in results if r["action"] in {"error"})
    n_done = sum(1 for r in results if r["action"] in {
        "renamed_dir", "moved_file", "rmdir"
    })
    n_would = sum(1 for r in results if r["action"].startswith("would_"))
    n_skip = sum(1 for r in results if r["action"].startswith("skip_"))

    summary = {
        "adk_home": str(ADK_HOME),
        "dry_run": args.dry_run,
        "done": n_done,
        "would_do": n_would,
        "skipped_conflicts": n_skip,
        "errors": n_errors,
        "details": results,
    }
    print(json.dumps(summary, indent=2))
    return 1 if n_errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
