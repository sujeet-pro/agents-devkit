---
title: 'verify_repo.py'
description: 'verify_repo.py — validate the adk v3 repo layout.'
script: 'verify_repo.py'
source: 'scripts/verify_repo.py'
group: 'scripts'
order: 4009
---
# verify_repo.py

verify_repo.py — validate the adk v3 repo layout.

## Source

`scripts/verify_repo.py`

## Contents

```python
#!/usr/bin/env python3
"""verify_repo.py — validate the adk v3 repo layout.

Checks:
- every skill in skills/ has SKILL.md with required frontmatter
- every adk-mcp-*.json is valid JSON with required fields
- shared/* required files exist
- decision-log schema is well-formed JSON examples
- no references to deleted v2 plugin paths anywhere

Exit 0 on clean. Exit 1 on errors. Warnings don't fail.

Usage:
  python3 scripts/verify_repo.py [--verbose]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO / "skills"
MCP_DIR = REPO / "mcp"
SHARED_DIR = REPO / "shared"
SHARED_REQUIRED = [
    "constitution.md", "advisor.md", "question-first.md", "decision-log-schema.md",
    "seed-decisions.jsonl",
]

# v2 was deleted entirely; any reference to the old plugin layout in v3 docs is stale.

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def check_skills(verbose: bool) -> None:
    if not SKILLS_DIR.exists():
        err(f"missing {SKILLS_DIR}")
        return
    expected = {
        "adk-implement", "adk-review", "adk-investigate", "adk-document",
        "adk-sync", "adk-setup", "adk-improve", "adk-explain",
    }
    found = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()}
    missing = expected - found
    if missing:
        err(f"missing skills: {sorted(missing)}")
    extra = found - expected
    if extra:
        warn(f"unexpected skill directories: {sorted(extra)}")

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            err(f"{skill_dir.name}: missing SKILL.md")
            continue
        content = skill_md.read_text(encoding="utf-8")
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not m:
            err(f"{skill_dir.name}: SKILL.md missing YAML frontmatter")
            continue
        fm = m.group(1)
        for field in ("name:", "description:"):
            if field not in fm:
                err(f"{skill_dir.name}: SKILL.md frontmatter missing `{field}`")
        if verbose:
            print(f"[skill] {skill_dir.name}: ok", file=sys.stderr)


def check_mcps(verbose: bool) -> None:
    if not MCP_DIR.exists():
        err(f"missing {MCP_DIR}")
        return
    for mcp_file in sorted(MCP_DIR.glob("adk-mcp-*.json")):
        try:
            data = json.loads(mcp_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            err(f"{mcp_file.name}: invalid JSON ({e})")
            continue
        if "name" not in data:
            err(f"{mcp_file.name}: missing `name`")
        if "description" not in data:
            warn(f"{mcp_file.name}: missing `description`")
        # Must be either http+url or command-based
        if "url" not in data and "command" not in data:
            err(f"{mcp_file.name}: must declare either `url` or `command`")
        if verbose:
            print(f"[mcp] {mcp_file.name}: ok", file=sys.stderr)


def check_shared(verbose: bool) -> None:
    if not SHARED_DIR.exists():
        err(f"missing {SHARED_DIR}")
        return
    for required in SHARED_REQUIRED:
        if not (SHARED_DIR / required).exists():
            err(f"missing shared/{required}")
    seed = SHARED_DIR / "seed-decisions.jsonl"
    if seed.exists():
        for i, line in enumerate(seed.read_text(encoding="utf-8").splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                err(f"seed-decisions.jsonl:{i}: invalid JSON ({e})")
    if verbose:
        print("[shared] checked", file=sys.stderr)


def check_stale_v2_in_v3() -> None:
    # v2 was deleted; any reference to plugins/adk-* in v3 source is now stale.
    # Skip docs/reference/ (auto-generated; legitimately embeds script source containing the patterns)
    # and node_modules/ (third-party).
    for p in REPO.rglob("*.md"):
        s = str(p)
        if ".temp/" in s or ".git/" in s or "/docs/reference/" in s or "/node_modules/" in s:
            continue
        rel = p.relative_to(REPO)
        text = p.read_text(encoding="utf-8", errors="ignore")
        for bad in ("plugins/adk-core/", "plugins/adk-code/", "plugins/adk-review/",
                    "plugins/adk-docs/", "plugins/adk-investigate/"):
            if bad in text:
                warn(f"{rel}: references deleted v2 path `{bad}`")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()

    check_shared(args.verbose)
    check_skills(args.verbose)
    check_mcps(args.verbose)
    check_stale_v2_in_v3()

    print(f"verify_repo: errors={len(errors)} warnings={len(warnings)}")
    for w in warnings:
        print(f"  warn: {w}")
    for e in errors:
        print(f"  err: {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

```
