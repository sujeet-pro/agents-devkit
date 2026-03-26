---
name: manage-skill
description: Create or update DevKit skills for software engineering workflows using shared child-agent, MCP, and output contracts
user_invocable: true
arguments:
  - name: name
    description: "Skill name in kebab-case"
    required: true
  - name: description
    description: "Brief description of the skill"
    required: true
  - name: type
    description: "Skill type: review, docs, research, diagram, implementation, integration"
    required: false
---

# Create or Update Skill

Use the shared DevKit references:

- `skills/_references/agentic-teams.md`
- `skills/_references/review-pipeline.md`
- `skills/_references/source-routing.md`
- `skills/_references/output-formats.md`
- `skills/_references/preflight-validations.md`
- `skills/_references/guidelines/README.md`

## Preflight

Before creating or updating a skill, run:

`zsh scripts/check-skill-deps.zsh manage-skill`

Check whether a skill with the given name already exists. If it does, load the existing SKILL.md for revision instead of creating from scratch.

## Required Child Agents

Run at least these child agents in parallel:

- **Pattern inspector**: reads 2-3 similar DevKit skills in the same prefix family to extract structural patterns, frontmatter conventions, child-agent shapes, and output formats. Produces a pattern brief with must-have sections and conventions for the skill type.
- **Research agent** (`research-agent`): researches external patterns, official docs, and community best practices for the skill's domain. Identifies tools, MCPs, or APIs the skill should leverage. Produces an external patterns brief.
- **Editorial agent** (`doc-reviewer`): reviews the drafted skill for conciseness, discoverability, consistency with the prefix family, and adherence to DevKit conventions. Checks that the description starts with "Use when...", child agents are properly defined, and the skill is self-contained.

## Workflow

1. **Check existing skills.** Search for skills with the same name or overlapping descriptions to avoid near-duplicates.
2. **Inspect patterns.** Launch the pattern inspector to read similar skills.
3. **Research.** Launch the research agent for external patterns.
4. **Draft skill.** Write the SKILL.md with these required sections:
   - YAML frontmatter (name, description, user_invocable, arguments)
   - Shared contracts reference
   - Preflight section
   - Guideline Loading (when applicable)
   - Required Child Agents with explicit roles
   - Numbered Workflow steps
   - Output specification
   - Adjacent Skills
5. **Review.** Launch the editorial agent to check quality and consistency.
6. **Write file.** Save to `skills/<name>/SKILL.md`.

## Rules

- Default to software-development use cases.
- Check whether an existing skill should be extended before creating a near-duplicate.
- Keep naming consistent with prefix groups: `review-*`, `write-*`, `audit-*`, `research-*`, `diagram-*`, `plan-*`, `dev-*`, `pr-*`, `agent-*`, `manage-*`, `publish-*`, `design-*`.
- Keep families consistent: related skills must share the same prefix.
- Use multiple child agents in parallel for non-trivial skills.
- Prefer source-native MCP integrations over ad hoc shell glue.
- If the skill depends on MCPs or external tools, require a preflight check.
- Inline operational logic in the skill; do not require helper scripts.
- Prefer open-source or free dependencies.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.
- Mention adjacent skills when a caller may need to route there instead.

## Output

A complete SKILL.md file at `skills/<name>/SKILL.md` that follows DevKit conventions and passes the editorial review.

## Adjacent Skills

- `/devkit:manage-improve` for auditing all skills at once
- `/devkit:manage-update` for pulling upstream skill updates
- `/devkit:manage-setup` for checking tool dependencies
