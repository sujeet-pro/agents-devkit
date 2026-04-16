#!/usr/bin/env python3
"""
Refresh published ADK skills from ai-guidelines shared files.

Reads shared-files-map.json for the canonical mapping of common files
that get copied to every published skill's references/_shared/ directory.

Skill-specific files (persona.md, workflow.md) live directly in each
skill and are NOT managed by this script.

Usage:
    python3 ai-guidelines/scripts/refresh_adk_skills.py status
    python3 ai-guidelines/scripts/refresh_adk_skills.py scope --changed-path <path>
    python3 ai-guidelines/scripts/refresh_adk_skills.py scope --source-id <id>
    python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared [--dry-run] [--skill NAME]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
AI_GUIDELINES = ROOT / "ai-guidelines"
MAP_PATH = AI_GUIDELINES / "shared-files-map.json"
REGISTRY_PATH = AI_GUIDELINES / "sources" / "registry.json"

sys.path.insert(0, str(ROOT / "scripts"))
from skill_catalog import iter_published_skill_dirs  # noqa: E402


def load_map() -> dict:
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def get_common_mappings(file_map: dict) -> list[tuple[Path, str]]:
    """Return list of (source_path, relative_target) for common shared files."""
    return [
        (ROOT / entry["source"], entry["target"])
        for entry in file_map["common"]["mappings"]
    ]


def get_selective_mappings(file_map: dict) -> list[tuple[Path, str, set[str]]]:
    """Return list of (source_path, relative_target, skill_names) for selectively shared files."""
    result = []
    for entry in file_map.get("selective", {}).get("mappings", []):
        result.append((ROOT / entry["source"], entry["target"], set(entry["skills"])))
    return result


def get_project_surfaces(file_map: dict) -> list[str]:
    return file_map["project_surfaces"]["paths"]


def published_skill_names() -> list[str]:
    return [d.name for d in iter_published_skill_dirs()]


def normalize_repo_path(value: str) -> str:
    path = Path(value)
    if path.is_absolute():
        try:
            return str(path.relative_to(ROOT))
        except ValueError:
            return str(path)
    return str(path)


def scope_for_changed_path(changed_path: str) -> dict:
    rel = normalize_repo_path(changed_path)
    published = published_skill_names()
    file_map = load_map()
    project_surfaces = get_project_surfaces(file_map)

    common_sources = {entry["source"] for entry in file_map["common"]["mappings"]}
    if rel in common_sources:
        return {
            "scope": "all-published-and-project",
            "reason": f"{rel} is a global shared source-of-truth document.",
            "published_skills": published,
            "project_surfaces": project_surfaces,
        }

    if rel == "ai-guidelines/skill-architecture.md":
        return {
            "scope": "all-published-project-and-docs",
            "reason": "Architecture changes affect published skills, project wrappers, and docs.",
            "published_skills": published,
            "project_surfaces": project_surfaces,
            "docs_surfaces": ["README.md", "CONTRIBUTING.md", "skills-manifest.json"],
        }

    if rel == "ai-guidelines/published-skill-catalog.md":
        return {
            "scope": "catalog-and-docs",
            "reason": "Catalog changes affect published skill inventory and docs.",
            "published_skills": published,
            "docs_surfaces": ["README.md", "CONTRIBUTING.md", "skills-manifest.json"],
        }

    if rel.startswith("skills/adk-"):
        skill_name = Path(rel).parts[1]
        return {
            "scope": "single-published-skill",
            "reason": f"{skill_name} is a published skill path.",
            "published_skills": [skill_name],
            "project_surfaces": [],
        }

    if any(rel.startswith(prefix) for prefix in project_surfaces):
        return {
            "scope": "project-only",
            "reason": f"{rel} is a repo-maintenance surface.",
            "published_skills": [],
            "project_surfaces": project_surfaces,
        }

    return {
        "scope": "manual-review",
        "reason": f"No deterministic scope rule matched {rel}.",
        "published_skills": [],
        "project_surfaces": [],
    }


def scope_for_source(source_id: str) -> dict:
    registry = load_registry()
    for source in registry["sources"]:
        if source["id"] != source_id:
            continue
        return {
            "scope": "source-mapped",
            "reason": f"{source_id} maps to specific skills in the registry.",
            "published_skills": source.get("mapped_published_skills", []),
            "project_surfaces": source.get("mapped_project_surfaces", []),
        }
    raise SystemExit(f"Unknown source id: {source_id}")


def render_scope(result: dict) -> None:
    print(f"scope: {result['scope']}")
    print(f"reason: {result['reason']}")
    if result.get("published_skills"):
        print("published_skills:")
        for skill in result["published_skills"]:
            print(f"- {skill}")
    if result.get("project_surfaces"):
        print("project_surfaces:")
        for surface in result["project_surfaces"]:
            print(f"- {surface}")
    if result.get("docs_surfaces"):
        print("docs_surfaces:")
        for surface in result["docs_surfaces"]:
            print(f"- {surface}")


def _sync_file(skill_dir: Path, skill_name: str, source: Path, relative_target: str, dry_run: bool) -> bool:
    """Copy source to skill_dir/relative_target if content differs. Return True if updated."""
    target = skill_dir / relative_target
    if not source.exists():
        print(f"warn {skill_name}:{relative_target} — source missing: {source}")
        return False
    source_text = source.read_text(encoding="utf-8")
    target_text = target.read_text(encoding="utf-8") if target.exists() else None
    if target_text == source_text:
        print(f"skip {skill_name}:{relative_target}")
        return False
    print(f"{'plan' if dry_run else 'write'} {skill_name}:{relative_target}")
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return True


def copy_shared(dry_run: bool, only_skills: list[str]) -> int:
    file_map = load_map()
    common = get_common_mappings(file_map)
    selective = get_selective_mappings(file_map)
    selected = set(only_skills)
    updated = 0

    for skill_dir in iter_published_skill_dirs():
        skill_name = skill_dir.name
        if selected and skill_name not in selected:
            continue

        # Common files (all skills)
        for source, relative_target in common:
            if _sync_file(skill_dir, skill_name, source, relative_target, dry_run):
                updated += 1

        # Selective files (subset of skills)
        for source, relative_target, target_skills in selective:
            if skill_name in target_skills:
                if _sync_file(skill_dir, skill_name, source, relative_target, dry_run):
                    updated += 1

    return updated


def status() -> None:
    file_map = load_map()
    registry = load_registry()
    published = published_skill_names()
    project_surfaces = get_project_surfaces(file_map)

    print(f"mapping_version: {file_map['version']}")
    print(f"published_skills: {len(published)}")
    for skill in published:
        print(f"- {skill}")
    print(f"sources: {len(registry['sources'])}")
    print("project_surfaces:")
    for surface in project_surfaces:
        print(f"- {surface}")
    print("common_files:")
    for entry in file_map["common"]["mappings"]:
        print(f"  {entry['source']} → {entry['target']}")
    selective = file_map.get("selective", {}).get("mappings", [])
    if selective:
        print(f"selective_files: {len(selective)}")
        for entry in selective:
            print(f"  {entry['source']} → {entry['target']} ({len(entry['skills'])} skills)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh published ADK skills from ai-guidelines.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show current published skill and source status")

    scope_parser = subparsers.add_parser("scope", help="Decide one-skill vs multi-skill update scope")
    scope_group = scope_parser.add_mutually_exclusive_group(required=True)
    scope_group.add_argument("--changed-path", help="Changed repo path")
    scope_group.add_argument("--source-id", help="Registry source id")

    copy_parser = subparsers.add_parser("copy-shared", help="Copy shared ai-guidelines docs into published skills")
    copy_parser.add_argument("--dry-run", action="store_true", help="Print planned copies only")
    copy_parser.add_argument("--skill", action="append", default=[], help="Limit to one or more published skills")

    args = parser.parse_args()

    if args.command == "status":
        status()
    elif args.command == "scope":
        result = scope_for_source(args.source_id) if args.source_id else scope_for_changed_path(args.changed_path)
        render_scope(result)
    elif args.command == "copy-shared":
        updated = copy_shared(args.dry_run, args.skill)
        print(f"updated: {updated}")


if __name__ == "__main__":
    main()
