#!/usr/bin/env python3
"""
Generate skills-manifest.json from all SKILL.md frontmatter.

Usage:
    python3 scripts/generate-skills-manifest.py
    python3 scripts/generate-skills-manifest.py --check  # verify manifest is up to date
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MANIFEST_PATH = ROOT / "skills-manifest.json"
PLUGIN_JSON = ROOT / ".claude-plugin" / "plugin.json"

sys.path.insert(0, str(ROOT / "templates" / "skill" / "scripts"))
from preflight import parse_frontmatter  # noqa: E402

CATEGORY_MAP = {
    "helper": "guideline",
    "orchestrator": "routing",
    "full": "task",
    "abbreviated": "task",
}


def get_plugin_version() -> str:
    if PLUGIN_JSON.exists():
        data = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
        return data.get("version", "0.0.0")
    return "0.0.0"


def extract_area(description: str) -> str:
    """Extract area tag from description like 'adk - [full] [review] ...'"""
    match = re.search(r"\]\s*\[(\w[\w-]*)\]", description)
    return match.group(1) if match else ""


def build_manifest() -> dict:
    version = get_plugin_version()
    skills = []

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        fm = parse_frontmatter(str(skill_dir))
        if not fm:
            continue

        name = fm.get("name", skill_dir.name)
        description = fm.get("description", "")
        tier = fm.get("workflow-tier", "")
        family = fm.get("workflow-family", "")
        maturity = fm.get("maturity", "stable")
        user_invocable = fm.get("user-invocable", False)
        area = extract_area(description)
        category = CATEGORY_MAP.get(tier, tier)

        clean_desc = re.sub(r"^adk\s*-\s*(\[.*?\]\s*)*", "", description).strip()

        entry = {
            "name": name,
            "description": clean_desc,
            "category": category,
            "tier": tier,
            "maturity": maturity,
            "user_invocable": user_invocable,
            "invocation": {
                "plugin": f"/adk:{skill_dir.name}",
                "skills_sh": f"/{skill_dir.name}",
            },
        }

        if area:
            entry["area"] = area
        if family:
            entry["family"] = family

        has_stages = (skill_dir / "stages").is_dir() and any(
            (skill_dir / "stages").iterdir()
        )
        has_refs = (skill_dir / "references").is_dir() and any(
            f
            for f in (skill_dir / "references").iterdir()
            if f.name not in {"help-format.md", "project-guidelines.md", "inline-interaction.md"}
        )

        if has_stages:
            entry["has_stages"] = True
        if has_refs:
            entry["has_references"] = True

        skills.append(entry)

    return {
        "version": version,
        "generated": str(date.today()),
        "skill_count": len(skills),
        "categories": {
            "task": sum(1 for s in skills if s["category"] == "task"),
            "guideline": sum(1 for s in skills if s["category"] == "guideline"),
            "routing": sum(1 for s in skills if s["category"] == "routing"),
        },
        "skills": skills,
    }


def main():
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
        else:
            print("✗ skills-manifest.json is out of date. Regenerate with:")
            print("  python3 scripts/generate-skills-manifest.py")
            sys.exit(1)

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"✓ Generated skills-manifest.json ({manifest['skill_count']} skills)")


if __name__ == "__main__":
    main()
