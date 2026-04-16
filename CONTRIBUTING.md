# Contributing to ADK

## Quick Start

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
python3 tests/test_skills.py
npm run docs:build
```

## Architecture

- `skills/adk-*`: public installable skills
- `agent-personas/adk-*`: canonical reusable subagent personas
- `agents-claude/*.md`: Claude installable agent sources
- `agents-cursor/*.md`: Cursor installable agent sources
- `agents-codex/*.toml`: Codex installable agent sources
- `hooks/settings.json`, `hooks/hooks-cursor/hooks.json`, `hooks/hooks-codex/hooks.json`: runtime-specific hook sources
- `ai-guidelines/`: source-of-truth philosophy, research protocol, personas, update policy, and provenance
- `.claude/skills/prj-*`, `.cursor/skills/prj-*`, `.agents/skills/prj-*`: repo-only maintenance skills
- `.codex/`: compatibility-only shim

## Public Skill Rules

- public skill names must start with `adk-`
- public skills must be self-contained
- keep argument count low and memorable
- use direct, professional names
- copy shared guidance into `references/_shared/` instead of relying on separately installed helper skills
- keep task-specific workflow and persona guidance in the skill's own local files

## Project Skill Rules

- project maintenance skills live in `.claude/skills/prj-*`, `.cursor/skills/prj-*`, and `.agents/skills/prj-*`
- project maintenance skill names must start with `prj-`
- mark repo-only skills with `metadata.internal: true`
- project maintenance skills may point directly to `ai-guidelines/`
- do not expose repo-only maintenance skills as part of the default public catalog

## Shared Guidance Workflow

1. Update `ai-guidelines/` first.
2. Use `python3 ai-guidelines/scripts/refresh_adk_skills.py scope ...` to decide one-skill vs family vs full-catalog impact.
3. Use `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared` to refresh copied shared docs in public skills.
4. Regenerate the public manifest.
5. Run validation.
6. Update attribution if user-facing behavior changed.

## Adding a Public Skill

1. Start from `templates/skill/SKILL-TEMPLATE.md`.
2. Create `skills/adk-<name>/`.
3. Add `SKILL.md`, `references/workflow.md`, `references/persona.md`, and `scripts/preflight.py`.
4. Keep the skill self-contained.
5. Run the shared-copy refresh.
6. Run `python3 scripts/generate-skills-manifest.py`.
7. Run `python3 tests/test_skills.py`.
8. Run `npm run docs:build`.
9. Verify `npx skills add . --list` shows the skill.

## Adding or Updating Shared Guidance

Update these first when relevant:
- `ai-guidelines/constitution.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/research-protocol.md`
- `ai-guidelines/update-scope-policy.md`
- `ai-guidelines/personas/`
- `ai-guidelines/sources/registry.json`

## Adding or Updating Agents

1. Edit the canonical persona in `agent-personas/adk-*/AGENT.md`.
2. Update `scripts/generate_agent_projections.py` if the runtime-specific metadata should change.
3. Run `python3 scripts/generate_agent_projections.py`.
4. Run validation.

## Adding or Updating Hooks

1. Update `scripts/generate_hook_projections.py` if the shared hook behavior or runtime mapping should change.
2. Run `python3 scripts/generate_hook_projections.py`.
3. Run validation.

## Attribution

- record new inspirations in `ai-guidelines/sources/registry.json`
- update `NOTICE.md` when upstream influence becomes user-facing
- update `docs/reference/skill-INSPIRATION-MAP.md` when skill-to-source mapping changes
- do not guess license or provenance details

## Validation Commands

```bash
python3 ai-guidelines/scripts/refresh_adk_skills.py status
python3 scripts/generate_agent_projections.py --check
python3 scripts/generate_hook_projections.py --check
python3 scripts/generate-skills-manifest.py --check
python3 tests/test_skills.py
python3 tests/test_agents.py
python3 tests/test_hooks.py
npm run docs:build
npx skills add . --list
```
