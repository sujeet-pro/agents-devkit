#!/usr/bin/env python3
"""
Add maturity field to all SKILL.md frontmatter that doesn't already have it.

Usage:
    python3 scripts/add-maturity-field.py              # apply changes
    python3 scripts/add-maturity-field.py --dry-run     # preview only
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

DRY_RUN = "--dry-run" in sys.argv
DEFAULT_MATURITY = "stable"

updated = 0
skipped = 0

for skill_dir in sorted(SKILLS_DIR.iterdir()):
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue

    content = skill_md.read_text(encoding="utf-8")

    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        print(f"  SKIP {skill_dir.name}: no frontmatter found")
        skipped += 1
        continue

    frontmatter = fm_match.group(1)

    if re.search(r"^maturity:", frontmatter, re.MULTILINE):
        print(f"  SKIP {skill_dir.name}: already has maturity field")
        skipped += 1
        continue

    new_content = re.sub(
        r"^(workflow-tier:\s*\S+)$",
        rf"\1\nmaturity: {DEFAULT_MATURITY}",
        content,
        count=1,
        flags=re.MULTILINE,
    )

    if new_content == content:
        new_content = re.sub(
            r"^(---\s*\n(?:.*?\n))(---)",
            rf"\1maturity: {DEFAULT_MATURITY}\n\2",
            content,
            count=1,
            flags=re.DOTALL,
        )

    if new_content != content:
        if DRY_RUN:
            print(f"  WOULD ADD maturity: {DEFAULT_MATURITY} to {skill_dir.name}")
        else:
            skill_md.write_text(new_content, encoding="utf-8")
            print(f"  ADDED maturity: {DEFAULT_MATURITY} to {skill_dir.name}")
        updated += 1
    else:
        print(f"  WARN {skill_dir.name}: could not determine insertion point")

print(f"\n{'Would update' if DRY_RUN else 'Updated'}: {updated}, Skipped: {skipped}")
