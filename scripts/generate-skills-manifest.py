#!/usr/bin/env python3
"""
Generate skills-manifest.json from published adk-* skills.

Usage:
    python3 scripts/generate-skills-manifest.py
    python3 scripts/generate-skills-manifest.py --check
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

from skill_catalog import ROOT, iter_published_skill_dirs, load_package_version

sys.path.insert(0, str(ROOT / "templates" / "skill" / "scripts"))
from preflight import parse_frontmatter  # noqa: E402


MANIFEST_PATH = ROOT / "skills-manifest.json"


def clean_description(raw: str) -> str:
    cleaned = re.sub(r"^adk\s*-\s*(\[[^\]]+\]\s*)*", "", raw).strip()
    return cleaned or raw.strip()


def infer_area(name: str) -> str:
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
    return "task"


def build_manifest() -> dict:
    skills: list[dict] = []

    for skill_dir in iter_published_skill_dirs():
        frontmatter = parse_frontmatter(str(skill_dir))
        if not frontmatter:
            continue

        name = str(frontmatter.get("name", skill_dir.name))
        description = str(frontmatter.get("description", "")).strip()
        tier = str(frontmatter.get("workflow-tier", "full"))
        family = str(frontmatter.get("workflow-family", ""))
        maturity = str(frontmatter.get("maturity", "stable"))
        user_invocable = bool(frontmatter.get("user-invocable", True))

        entry = {
            "name": name,
            "description": clean_description(description),
            "category": "task",
            "tier": tier,
            "maturity": maturity,
            "user_invocable": user_invocable,
            "path": str(skill_dir.relative_to(ROOT)),
            "invocation": {
                "default": f"/{name}",
                "npx_skills": f"/{name}",
            },
            "area": infer_area(name),
            "has_references": (skill_dir / "references").is_dir(),
            "has_scripts": (skill_dir / "scripts").is_dir(),
            "has_assets": (skill_dir / "assets").is_dir(),
        }
        if family:
            entry["family"] = family
        skills.append(entry)

    skills.sort(key=lambda item: item["name"])

    return {
        "version": load_package_version(),
        "generated": str(date.today()),
        "distribution": "npx-skills",
        "skill_count": len(skills),
        "categories": {
            "task": len(skills),
            "guideline": 0,
            "routing": 0,
        },
        "skills": skills,
    }


def main() -> None:
    check_mode = "--check" in sys.argv
    manifest = build_manifest()

    if check_mode:
        if not MANIFEST_PATH.exists():
            print("✗ skills-manifest.json does not exist. Run without --check to generate.")
            sys.exit(1)
        existing = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        existing.pop("generated", None)
        manifest.pop("generated", None)
        if existing == manifest:
            print("✓ skills-manifest.json is up to date")
            sys.exit(0)
        print("✗ skills-manifest.json is out of date. Regenerate with:")
        print("  python3 scripts/generate-skills-manifest.py")
        sys.exit(1)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"✓ Generated skills-manifest.json ({manifest['skill_count']} published skills)")


if __name__ == "__main__":
    main()
