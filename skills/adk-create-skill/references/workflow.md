# ADK Create Skill Workflow

## Default Flow
1. confirm skill name, area, and tier with the user
2. validate the name: kebab-case, no conflicts with existing `skills/adk-*` directories
3. run `python3 scripts/scaffold.py <name> --area <area> --tier <tier> --source <path-to-shared-refs>` to generate the full directory structure
4. copy shared references from the canonical source into `references/_shared/`
5. generate SKILL.md with appropriate frontmatter, reading order, parameters, workflow outline, and related skills
6. generate persona.md with a role tailored to the skill's purpose
7. generate workflow.md with skill-specific steps matching the chosen tier
8. generate preflight.py that checks all declared dependencies
9. validate the generated structure: all required files exist, frontmatter is parseable, name follows conventions
10. report what was created and list next steps

## MCP Skill Flow
When `--mcp <server>` is provided:
1. follow the default flow above
2. add `mcp-servers: [<server>]` to the dependencies block in frontmatter
3. generate an enhanced preflight.py that checks MCP server configuration in addition to commands
4. add MCP-specific notes to the generated workflow

## Validation Checklist
- `skills/adk-<name>/SKILL.md` exists and has valid frontmatter
- `skills/adk-<name>/scripts/preflight.py` exists and is executable
- `skills/adk-<name>/references/_shared/` contains all four shared files
- `skills/adk-<name>/references/persona.md` exists
- `skills/adk-<name>/references/workflow.md` exists
- skill name matches `adk-<name>` with kebab-case `<name>`
- no pre-existing skill directory was overwritten without confirmation
