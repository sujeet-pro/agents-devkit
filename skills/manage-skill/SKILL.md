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

# Create Skill

Use the shared DevKit references:

- `skills/_references/agentic-teams.md`
- `skills/_references/review-pipeline.md`
- `skills/_references/source-routing.md`
- `skills/_references/output-formats.md`
- `skills/_references/preflight-validations.md`
- `skills/_references/guidelines/README.md`

## Rules

- Default to software-development use cases.
- Check first whether an existing DevKit skill should be extended or reused before creating a near-duplicate.
- Keep naming consistent with prefix groups: `review-*` (comment/artifact review), `write-*` (direct drafting), `audit-*` (audits), `research-*` (research), `diagram-*` (diagrams), `plan-*` (planning), `dev-*` (dev process), `pr-*` (PR authoring), `agent-*` (orchestration), `manage-*` (DevKit management), `publish-*` (publishing), `design-*` (design).
- Keep families consistent: related skills must share the same prefix.
- Use multiple child agents in parallel whenever the skill performs non-trivial work.
- Prefer source-native MCP integrations over ad hoc shell glue.
- If the skill depends on MCPs or external tools, require a preflight check before the main workflow starts.
- Inline operational logic in the skill; do not require helper scripts to make the workflow understandable.
- Prefer open-source or free dependencies.
- Prefer Mermaid, Excalidraw, or draw.io for new diagrams; use `/devkit:diagram-graphviz` only for existing DOT assets.
- Mention adjacent skills when a caller may need to route there instead.
- Test new skills against realistic engineering scenarios before publishing.

## Creation Team

Run in parallel:

- one pass to inspect similar DevKit skills
- one pass to research external patterns or official docs
- one editorial pass to keep the skill concise and discoverable
