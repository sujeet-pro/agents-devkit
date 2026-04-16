# Skill Template Reference

Canonical templates for each file in a generated ADK skill. The scaffold script uses these patterns when generating new skills.

---

## Frontmatter Template

```yaml
---
name: adk-<name>
description: <One-line description starting with a verb. Use when <scenario>.>
compatibility: Self-contained published skill for npx skills. Works best when <tools/deps> are available.
user-invocable: true
argument-hint: "<args> [--help]"
workflow-tier: full|lightweight
maturity: experimental
workflow-family: standard-task|complex-build|quick-action
tools: [Read, Write, Edit, Glob, Grep, Bash]
metadata:
  area: <development|documentation|review|planning|integration|testing|research>
dependencies:
  commands: [git, python3]
  mcp-servers: [<server-name>]    # only if MCP-dependent
---
```

### Field Reference
| Field | Required | Notes |
| --- | --- | --- |
| `name` | yes | Must match directory name: `adk-<kebab-case>` |
| `description` | yes | One line. Start with a verb. Include "Use when..." |
| `compatibility` | yes | Always starts with "Self-contained published skill for npx skills." |
| `user-invocable` | yes | `true` for task skills, `false` for helper/guideline skills |
| `argument-hint` | yes | Show required args and common flags |
| `workflow-tier` | yes | `full` for multi-step, `lightweight` for quick actions |
| `maturity` | yes | New skills always start as `experimental` |
| `workflow-family` | yes | `standard-task`, `complex-build`, or `quick-action` |
| `tools` | yes | List of tools the skill needs |
| `metadata.area` | yes | Functional area for categorization |
| `dependencies.commands` | yes | CLI tools that must be installed |
| `dependencies.mcp-servers` | no | Only for MCP-dependent skills |

---

## SKILL.md Body Template

```markdown
# ADK <Title>

## Overview
<1-2 sentences describing what the skill does and why.>

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
1. confirm the task and scope
2. read relevant sources
3. execute the work
4. validate results
5. report what was done

## Validation
- run the smallest relevant check
- if a claim cannot be verified, say so explicitly

## Output
- summary of what was done
- changed files or artifacts
- remaining risk or follow-up

## Related Skills
- `adk-build`
```

---

## persona.md Template

```markdown
# <Role> Persona

## Mission
- <One sentence: what this persona delivers.>

## Scope
- <area 1>
- <area 2>
- <area 3>

## Hard Rules
- <rule 1>
- <rule 2>
- <rule 3>

## Evidence Expectations
- <what counts as proof of success>
- <what counts as proof of success>

## Output Style
- <format bullet 1>
- <format bullet 2>
- ask whether more detail is needed
```

---

## workflow.md Template

```markdown
# ADK <Name> Workflow

## Default Flow
1. confirm the task, scope, and constraints
2. read only the sources needed
3. plan before making changes
4. execute the smallest correct change
5. validate before claiming success
6. report changed files and remaining risk

## Validation Rules
- run the smallest relevant check first
- if a claim cannot be verified, say so explicitly
- do not claim success without evidence
```

---

## preflight.py Template (Standard)

```python
#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


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
```

---

## preflight.py Template (MCP-Aware)

```python
#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path


def read_required_commands(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"commands:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


def read_mcp_servers(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    match = re.search(r"mcp-servers:\s*\[([^\]]*)\]", text)
    if not match:
        return []
    return [item.strip().strip("'\"") for item in match.group(1).split(",") if item.strip()]


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
```
