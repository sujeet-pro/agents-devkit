#!/usr/bin/env python3
"""
Scaffold a new ADK skill with the correct directory structure, frontmatter,
persona, workflow, preflight script, and shared references.

Usage:
    python3 scaffold.py <skill-name> [options]

Options:
    --area <area>           Functional area (default: development)
    --tier full|lightweight Workflow tier (default: full)
    --mcp <server>          MCP server dependency
    --source <path>         Path to shared references to copy
    --target <path>         Parent directory for the new skill (default: skills/ in repo root)

Examples:
    python3 scaffold.py my-tool
    python3 scaffold.py my-tool --area review --tier lightweight
    python3 scaffold.py my-tool --mcp github
    python3 scaffold.py my-tool --source /path/to/shared-refs --target /path/to/skills
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

VALID_AREAS = [
    "development",
    "documentation",
    "review",
    "planning",
    "integration",
    "testing",
    "research",
]

VALID_TIERS = ["full", "lightweight"]

TIER_TO_FAMILY = {
    "full": "standard-task",
    "lightweight": "quick-action",
}


def validate_name(name: str) -> str:
    """Validate and normalize the skill name to kebab-case without the adk- prefix."""
    # Strip adk- prefix if the user included it
    if name.startswith("adk-"):
        name = name[4:]

    if not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
        print(
            f"Error: '{name}' is not valid kebab-case. "
            "Use lowercase letters, digits, and hyphens (e.g. 'my-tool', 'review-pr')."
        )
        raise SystemExit(1)

    return name


def find_repo_root() -> Path | None:
    """Walk up from this script to find the repo root containing a skills/ directory."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "skills").is_dir() and (parent / "CLAUDE.md").exists():
            return parent
    return None


def generate_skill_md(name: str, area: str, tier: str, mcp: str | None) -> str:
    """Generate the SKILL.md content with proper frontmatter and body."""
    family = TIER_TO_FAMILY[tier]
    full_name = f"adk-{name}"
    title = " ".join(word.capitalize() for word in name.split("-"))

    # Build tools list
    tools = "Read, Write, Edit, Glob, Grep, Bash"

    # Build dependencies block
    deps_lines = ["dependencies:"]
    deps_lines.append("  commands: [git, python3]")
    if mcp:
        deps_lines.append(f"  mcp-servers: [{mcp}]")
    deps_block = "\n".join(deps_lines)

    # Build compatibility line
    if mcp:
        compat = f"Self-contained published skill for npx skills. Works best when git, python3, and the {mcp} MCP server are available."
    else:
        compat = "Self-contained published skill for npx skills. Works best when git and python3 are available."

    # Argument hint
    arg_hint = "<task> [--help]"

    body = f"""---
name: {full_name}
description: <describe what this skill does>. Use when <scenario>.
compatibility: {compat}
user-invocable: true
argument-hint: "{arg_hint}"
workflow-tier: {tier}
maturity: experimental
workflow-family: {family}
tools: [{tools}]
metadata:
  area: {area}
{deps_block}
---

# ADK {title}

## Overview
<Describe what this skill does and why it exists.>

## When To Use
- <positive use case>
- <positive use case>
- not for <anti-pattern>
- not for <anti-pattern>

## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/research-protocol.md`
- `references/_shared/output-format.md`
- `references/workflow.md`
- `references/persona.md`

## Parameters
| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What to do |
| `--help` | flag | off | Show the skill and stop |

## Workflow
1. confirm the task, scope, and constraints
2. read only the sources needed
3. plan before making changes
4. execute the work
5. validate results
6. report what was done and remaining risk

## Validation
- run the smallest relevant check first
- if a claim cannot be verified, say so explicitly
- do not claim success without evidence

## Output
- summary of what was done
- changed files or artifacts
- remaining risk or follow-up
- ask whether more detail is needed

## Related Skills
- `adk-build`
"""
    return body


def generate_persona(name: str) -> str:
    """Generate the persona.md content."""
    title = " ".join(word.capitalize() for word in name.split("-"))
    return f"""# {title} Persona

## Mission
- <One sentence describing what this persona delivers.>

## Scope
- <area of responsibility 1>
- <area of responsibility 2>
- <area of responsibility 3>

## Hard Rules
- validate before claiming completion
- preserve existing user work
- prefer simple and readable solutions
- use repo-native commands when available

## Evidence Expectations
- <what counts as proof of success>
- explicit note when validation could not run

## Output Style
- changed files or artifacts
- validation results
- remaining risk
- ask whether more detail is needed
"""


def generate_workflow(name: str, tier: str) -> str:
    """Generate the workflow.md content."""
    title = " ".join(word.capitalize() for word in name.split("-"))

    if tier == "lightweight":
        return f"""# ADK {title} Workflow

## Default Flow
1. confirm the task and scope
2. execute the work
3. validate the result
4. report what was done

## Validation Rules
- run the smallest relevant check first
- if a claim cannot be verified, say so explicitly
"""
    else:
        return f"""# ADK {title} Workflow

## Default Flow
1. confirm the task, scope, constraints, and validation target
2. read only the local code and sources needed
3. write or refine a short plan before making non-trivial changes
4. execute the smallest correct change
5. run repo-native validation before claiming success
6. report changed files, validation, and remaining risk in concise bullets

## Validation Rules
- run the smallest relevant check first
- if a claim cannot be verified, say so explicitly
- do not claim success without fresh evidence
"""


def generate_preflight(mcp: str | None) -> str:
    """Generate the preflight.py content."""
    if mcp:
        return '''#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\\s*\\[([^\\]]*)\\]", text)
    if not match:
        return []
    return [item.strip().strip("'\\"") for item in match.group(1).split(",") if item.strip()]


def read_mcp_servers(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"mcp-servers:\\s*\\[([^\\]]*)\\]", text)
    if not match:
        return []
    return [item.strip().strip("'\\"") for item in match.group(1).split(",") if item.strip()]


def check_mcp_server(name: str) -> bool:
    for config_path in [Path.home() / ".claude.json", Path("mcp-config.json")]:
        if config_path.exists():
            try:
                data = json.loads(config_path.read_text(encoding="utf-8"))
                if name in data.get("mcpServers", {}):
                    return True
            except (json.JSONDecodeError, KeyError):
                continue
    return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    missing = []

    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            missing.append(command)

    for server in read_mcp_servers(skill_dir):
        if check_mcp_server(server):
            print(f"ok mcp:{server}")
        else:
            print(f"missing mcp:{server}")
            missing.append(f"mcp:{server}")

    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
'''
    else:
        return '''#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\\s*\\[([^\\]]*)\\]", text)
    if not match:
        return []
    return [item.strip().strip("'\\"") for item in match.group(1).split(",") if item.strip()]


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 preflight.py <skill-dir>")
        raise SystemExit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    missing = []
    for command in read_required_commands(skill_dir):
        if shutil.which(command):
            print(f"ok {command}")
        else:
            print(f"missing {command}")
            missing.append(command)

    raise SystemExit(1 if missing else 0)


if __name__ == "__main__":
    main()
'''


def copy_shared_references(source: Path, target: Path) -> list[str]:
    """Copy shared reference files to the target _shared directory."""
    copied = []
    if not source.is_dir():
        print(f"Warning: shared references source not found at {source}")
        return copied

    target.mkdir(parents=True, exist_ok=True)
    for src_file in sorted(source.iterdir()):
        if src_file.is_file() and src_file.suffix == ".md":
            dst = target / src_file.name
            shutil.copy2(src_file, dst)
            copied.append(src_file.name)

    return copied


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a new ADK skill directory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scaffold.py my-tool
  python3 scaffold.py my-tool --area review --tier lightweight
  python3 scaffold.py my-tool --mcp github
""",
    )
    parser.add_argument(
        "name",
        help="Skill name in kebab-case (adk- prefix added automatically)",
    )
    parser.add_argument(
        "--area",
        choices=VALID_AREAS,
        default="development",
        help="Functional area (default: development)",
    )
    parser.add_argument(
        "--tier",
        choices=VALID_TIERS,
        default="full",
        help="Workflow tier (default: full)",
    )
    parser.add_argument(
        "--mcp",
        default=None,
        help="MCP server dependency (e.g. github, bitbucket)",
    )
    parser.add_argument(
        "--source",
        default=None,
        help="Path to shared references directory to copy from",
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Parent directory for the new skill (default: skills/ in repo root)",
    )

    args = parser.parse_args()

    # Validate name
    name = validate_name(args.name)
    full_name = f"adk-{name}"

    # Determine target directory
    if args.target:
        skills_parent = Path(args.target).resolve()
    else:
        repo_root = find_repo_root()
        if repo_root:
            skills_parent = repo_root / "skills"
        else:
            skills_parent = Path.cwd() / "skills"

    skill_dir = skills_parent / full_name

    # Check for conflicts
    if skill_dir.exists():
        print(f"Error: skill directory already exists at {skill_dir}")
        print("Remove it first or choose a different name.")
        raise SystemExit(1)

    # Determine shared references source
    if args.source:
        shared_source = Path(args.source).resolve()
    else:
        repo_root = find_repo_root()
        if repo_root:
            # Look for shared refs in an existing skill
            candidates = [
                repo_root / "skills" / "adk-build" / "references" / "_shared",
                repo_root / "skills" / "adk-commit" / "references" / "_shared",
            ]
            shared_source = next((c for c in candidates if c.is_dir()), None)
        else:
            shared_source = None

    print(f"Scaffolding skill: {full_name}")
    print(f"  area: {args.area}")
    print(f"  tier: {args.tier}")
    print(f"  family: {TIER_TO_FAMILY[args.tier]}")
    if args.mcp:
        print(f"  mcp: {args.mcp}")
    print()

    # Create directory structure
    created_files = []

    (skill_dir / "scripts").mkdir(parents=True, exist_ok=True)
    (skill_dir / "references" / "_shared").mkdir(parents=True, exist_ok=True)

    # Write SKILL.md
    skill_md_path = skill_dir / "SKILL.md"
    skill_md_path.write_text(generate_skill_md(name, args.area, args.tier, args.mcp), encoding="utf-8")
    created_files.append(skill_md_path)

    # Write persona.md
    persona_path = skill_dir / "references" / "persona.md"
    persona_path.write_text(generate_persona(name), encoding="utf-8")
    created_files.append(persona_path)

    # Write workflow.md
    workflow_path = skill_dir / "references" / "workflow.md"
    workflow_path.write_text(generate_workflow(name, args.tier), encoding="utf-8")
    created_files.append(workflow_path)

    # Write preflight.py
    preflight_path = skill_dir / "scripts" / "preflight.py"
    preflight_path.write_text(generate_preflight(args.mcp), encoding="utf-8")
    created_files.append(preflight_path)

    # Copy shared references
    shared_copied = []
    if shared_source:
        shared_copied = copy_shared_references(
            shared_source, skill_dir / "references" / "_shared"
        )
        for fname in shared_copied:
            created_files.append(skill_dir / "references" / "_shared" / fname)
    else:
        print("Warning: no shared references source found. references/_shared/ is empty.")
        print("  Copy shared references manually or re-run with --source <path>.")

    # Print summary
    print("Created files:")
    for f in created_files:
        print(f"  {f}")

    print()
    if shared_copied:
        print(f"Shared references copied: {', '.join(shared_copied)}")
    print()

    print("Next steps:")
    print(f"  1. Edit {skill_md_path} -- fill in description, parameters, and workflow")
    print(f"  2. Edit {persona_path} -- customize the persona for this skill's role")
    print(f"  3. Edit {workflow_path} -- detail the skill-specific workflow steps")
    print(f"  4. Run: python3 {preflight_path} {skill_dir}")
    print()
    print(f"Skill scaffolded at: {skill_dir}")


if __name__ == "__main__":
    main()
