#!/usr/bin/env python3
"""
Propagate common files and preflight scripts to all skill directories.

Usage:
    python3 templates/skill/scripts/propagate.py [--dry-run] [--clean-refs]

Shared reference content (workflow, communication style, principal-engineer,
agentic-teams, output-format, interaction, preflight, review standards) is
now provided by dedicated helper skills instead of copied reference files.
This script only propagates:
  - templates/skill/common/ → skills/<skill>/references/  (e.g. help-format, project-guidelines, inline-interaction)
  - templates/skill/scripts/preflight.py → skills/<skill>/scripts/preflight.py

Use --clean-refs to remove the deprecated reference files that are now skills.
"""

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

DEPRECATED_REFS = {
    "workflow-6phase.md",
    "workflow-7phase.md",
    "communication-style.md",
    "principal-engineer.md",
    "agentic-teams.md",
    "output-formats.md",
    "output-format-modes.md",
    # inline-interaction.md lives under templates/skill/common/ and is propagated; do not delete.
    "preflight.md",
    "source-routing.md",
    "review-pipeline.md",
    "review-comment-template.md",
}


def find_project_root() -> Path:
    """Find the project root by looking for templates/skill/."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "templates" / "skill").exists():
            return current
        current = current.parent
    print("Error: Could not find project root (templates/skill/ not found)")
    sys.exit(1)


def collect_canonical_files(base_dir: Path) -> dict[str, Path]:
    """Collect all files under a directory, keyed by relative path."""
    files = {}
    if not base_dir.exists():
        return files
    for f in base_dir.rglob("*"):
        if f.is_file():
            rel = f.relative_to(base_dir)
            files[str(rel)] = f
    return files


def sync_file(src: Path, dst: Path, dry_run: bool, label: str, stats: dict) -> bool:
    """Copy src to dst if different. Returns True if changed."""
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        stats["files_skipped"] += 1
        return False
    if dry_run:
        action = "UPDATE" if dst.exists() else "ADD"
        print(f"  [{action}] {label}")
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    stats["files_changed"] += 1
    return True


def propagate(dry_run: bool = False, clean_refs: bool = False) -> None:
    root = find_project_root()
    templates_dir = root / "templates" / "skill"
    skills_dir = root / "skills"

    canonical_scripts = templates_dir / "scripts"
    canonical_common = templates_dir / "common"

    canonical_common_files = collect_canonical_files(canonical_common)
    preflight_src = canonical_scripts / "preflight.py"

    stats = {
        "skills_updated": 0,
        "files_changed": 0,
        "files_skipped": 0,
        "files_removed": 0,
    }

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if skill_dir.name.startswith("_"):
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue

        skill_refs = skill_dir / "references"
        skill_scripts = skill_dir / "scripts"
        skill_updated = False

        # Copy common files into references/
        for rel_path, src in canonical_common_files.items():
            dst = skill_refs / rel_path
            label = f"{skill_dir.name}/references/{rel_path}"
            if sync_file(src, dst, dry_run, label, stats):
                skill_updated = True

        # Update preflight.py
        if preflight_src.exists():
            label = f"{skill_dir.name}/scripts/preflight.py"
            dst = skill_scripts / "preflight.py"
            if sync_file(preflight_src, dst, dry_run, label, stats):
                skill_updated = True

        # Remove deprecated reference files (now provided by helper skills)
        if clean_refs:
            for ref_name in DEPRECATED_REFS:
                deprecated = skill_refs / ref_name
                if deprecated.exists():
                    if dry_run:
                        print(f"  [REMOVE] {skill_dir.name}/references/{ref_name}")
                    else:
                        deprecated.unlink()
                    stats["files_removed"] += 1
                    skill_updated = True

        # Remove other deprecated files
        deprecated_paths = [
            skill_scripts / "interactive_review.py",
        ]
        for deprecated in deprecated_paths:
            if deprecated.exists():
                if dry_run:
                    print(f"  [REMOVE] {skill_dir.name}/{deprecated.relative_to(skill_dir)}")
                else:
                    deprecated.unlink()
                stats["files_removed"] += 1
                skill_updated = True

        # Clean __pycache__ directories
        for pycache in skill_dir.rglob("__pycache__"):
            if pycache.is_dir():
                if dry_run:
                    print(f"  [REMOVE] {skill_dir.name}/{pycache.relative_to(skill_dir)}/")
                else:
                    shutil.rmtree(pycache)
                stats["files_removed"] += 1
                skill_updated = True

        if skill_updated:
            stats["skills_updated"] += 1

    mode = "[DRY RUN] " if dry_run else ""
    print(f"\n{mode}Propagation complete:")
    print(f"  Skills updated: {stats['skills_updated']}")
    print(f"  Files changed:  {stats['files_changed']}")
    print(f"  Files unchanged: {stats['files_skipped']}")
    print(f"  Files removed: {stats['files_removed']}")


def main():
    parser = argparse.ArgumentParser(description="Propagate common files to all skills")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying files")
    parser.add_argument("--clean-refs", action="store_true", help="Remove deprecated reference files that are now skills")
    args = parser.parse_args()
    propagate(dry_run=args.dry_run, clean_refs=args.clean_refs)


if __name__ == "__main__":
    main()
