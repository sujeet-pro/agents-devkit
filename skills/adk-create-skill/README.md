# adk-create-skill

Scaffold a new ADK skill with proper structure, frontmatter, persona, workflow, and preflight checks.

## Quick Start

```bash
npx adk-create-skill my-tool --area development
```

## What This Skill Does

Meta-skill for scaffolding new ADK skills. Generates the complete directory structure including SKILL.md with proper frontmatter, persona, workflow, preflight script, and shared references. Validates naming conventions, checks for conflicts with existing skills, and provides a clear list of next steps for customization.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<skill-name>` | kebab-case string | required | Name for the new skill (without `adk-` prefix) |
| `--area` | `development`, `documentation`, `review`, `planning`, `integration`, `testing`, `research` | `development` | Functional area for skill metadata |
| `--tier` | `full`, `lightweight` | `full` | Workflow tier |
| `--mcp` | server name | none | MCP server dependency to include |
| `--auto` | flag | off | Skip confirmations and scaffold with defaults |
| `--help` | flag | off | Show the skill reference and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | CLI command | yes |
| `python3` | CLI command | yes |

## Skill Layout

```
skills/adk-create-skill/
  SKILL.md                              # Skill definition and frontmatter
  README.md                             # This file
  scripts/
    preflight.py                        # Pre-flight dependency checks
    scaffold.py                         # Skill scaffolding generator
  references/
    persona.md                          # Skill-specific persona
    workflow.md                         # Skill-specific workflow detail
    skill-template.md                   # Template reference for generated skills
    _shared/
      ai-guidelines-overview.md         # Shared ADK guidance
      constitution.md                   # Shared constitution
      output-format.md                  # Shared output format
      research-protocol.md              # Shared research protocol
```

## Workflow

1. Confirm skill name, area, tier, and optional MCP dependency.
2. Validate the name: must be kebab-case, must not conflict with an existing skill in `skills/`.
3. Run `python3 scripts/scaffold.py` with the appropriate arguments to generate the directory structure.
4. Review each generated file for correctness.
5. Customize the generated SKILL.md body, persona, and workflow for the specific skill's purpose.
6. Run preflight on the generated skill to validate dependencies.
7. Report what was created and list next steps for customization.

### What Gets Generated

| File | Purpose |
| --- | --- |
| `skills/adk-<name>/SKILL.md` | Main skill definition with frontmatter and sections |
| `skills/adk-<name>/scripts/preflight.py` | Pre-flight dependency validation script |
| `skills/adk-<name>/references/_shared/` | Copied shared guidance files |
| `skills/adk-<name>/references/persona.md` | Skill-specific persona definition |
| `skills/adk-<name>/references/workflow.md` | Skill-specific workflow steps |

## Interaction Protocol

- **Confirm skill name and area** -- before scaffolding, confirm the skill name, area, tier, and any MCP dependency.
- **Present generated structure for review** -- after scaffolding, list every generated file and its purpose.
- **Validate naming conventions** -- reject names that violate kebab-case or conflict with existing skills; explain why.
- **Show frontmatter summary** -- display the generated frontmatter for confirmation before finalizing.
- **List next steps** -- provide a clear list of what the user should customize next.

### Naming Conventions

- All skill directories use the `adk-` prefix: `skills/adk-<name>/`
- Names are kebab-case: lowercase letters, digits, and hyphens only
- Group by workflow family: `quick-action`, `standard-task`, `complex-build`
- Choose descriptive verbs: `build`, `review`, `migrate`, `audit`, `plan`, `research`

## Output Format

- List of generated files with paths
- Generated frontmatter summary
- Next steps for customization
- Remaining work (persona tuning, workflow detailing, testing)

## Examples

Scaffold a basic skill:
```
/adk-create-skill my-tool --area development
```

Scaffold an MCP-dependent skill:
```
/adk-create-skill slack-connector --area integration --mcp slack
```

Scaffold a lightweight skill:
```
/adk-create-skill quick-lint --area audits-quality --tier lightweight
```

## What Success Looks Like

- [ ] Skill name and area are confirmed before scaffolding
- [ ] Name passes kebab-case validation and does not conflict
- [ ] All required files are generated (SKILL.md, preflight, persona, workflow, shared refs)
- [ ] Frontmatter is valid YAML with all required fields
- [ ] Generated preflight script passes when run
- [ ] Next steps for customization are clearly listed
- [ ] MCP dependency is included in frontmatter when `--mcp` is specified
