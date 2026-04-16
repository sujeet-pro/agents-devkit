#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
PACKAGE_JSON = ROOT / "package.json"

sys.path.insert(0, str(ROOT / "templates" / "skill" / "scripts"))
from preflight import parse_frontmatter  # noqa: E402


def load_package_version() -> str:
    if not PACKAGE_JSON.exists():
        return "0.0.0-dev"
    data = json.loads(PACKAGE_JSON.read_text(encoding="utf-8"))
    return str(data.get("version", "0.0.0-dev"))


def metadata_for(frontmatter: dict) -> dict:
    metadata = frontmatter.get("metadata", {})
    return metadata if isinstance(metadata, dict) else {}


def is_internal_skill(frontmatter: dict) -> bool:
    metadata = metadata_for(frontmatter)
    internal = metadata.get("internal")
    if isinstance(internal, bool):
        return internal
    return str(internal).strip().lower() in {"1", "true", "yes"}


def is_published_skill(skill_dir: Path, frontmatter: dict) -> bool:
    name = str(frontmatter.get("name", skill_dir.name))
    return name.startswith("adk-") and not is_internal_skill(frontmatter)


def iter_skill_dirs() -> list[Path]:
    return [
        skill_dir
        for skill_dir in sorted(SKILLS_DIR.iterdir())
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists()
    ]


def iter_published_skill_dirs() -> list[Path]:
    published: list[Path] = []
    for skill_dir in iter_skill_dirs():
        frontmatter = parse_frontmatter(str(skill_dir))
        if frontmatter and is_published_skill(skill_dir, frontmatter):
            published.append(skill_dir)
    return published


def infer_area_from_name(name: str) -> str:
    if name in {"adk-write-docs", "adk-review-docs"}:
        return "documentation"
    if name in {"adk-audit-repo", "adk-audit-site", "adk-test", "adk-deps"}:
        return "audits-quality"
    if name in {"adk-diagram", "adk-chart", "adk-design"}:
        return "diagrams"
    if name in {"adk-build", "adk-refactor", "adk-migrate", "adk-commit", "adk-create-skill", "adk-handoff"}:
        return "development"
    if name in {"adk-brainstorm", "adk-plan", "adk-research", "adk-spec"}:
        return "research-planning"
    if name in {"adk-github", "adk-bitbucket", "adk-confluence", "adk-google-drive"}:
        return "platform-connector"
    if name.startswith("adk-review-"):
        return "review"
    return ""
