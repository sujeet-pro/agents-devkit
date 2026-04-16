---
title: Guidelines Reference
description: Coding, documentation, and architecture guidelines auto-loaded by skills
order: 4
---

# Guidelines Reference

ADK no longer ships separate guideline skills. Shared guidance now lives in `ai-guidelines/`, and published skills copy the shared documents they need into `references/_shared/`.

## Canonical Shared Guidance

**Location:** `ai-guidelines/`

These files define the repo's shared source of truth:

| File | Focus |
|-----------|-------|
| `README.md` | overview of the shared guidance model |
| `constitution.md` | non-negotiable operating rules |
| `brainstorming-workflow.md` | ambiguity-reduction and design-closure flow |
| `research-protocol.md` | repo-first, evidence-first research method |
| `output-format.md` | shared response shape and severity rules |
| `skill-architecture.md` | public skill, persona, hook, and workflow layout |
| `update-scope-policy.md` | how to decide refresh scope after shared changes |
| `sources/registry.json` | provenance for externally informed behavior |

## Copied Into Public Skills

**Location:** `skills/adk-*/references/_shared/`

Published skills stay self-contained by copying the shared documents they need into each skill directory.

Common copied files:

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/research-protocol.md`
- `references/_shared/output-format.md`

The mapping is defined in `ai-guidelines/shared-files-map.json`, and refreshed with:

```bash
python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared
```

## Skill-Local Guidance

**Location:** `skills/adk-*/references/`

Each published skill also owns local references that are specific to that skill's job:

- `references/workflow.md` for the task-specific process
- `references/persona.md` for the task-specific voice and evidence bar
- optional extra references such as templates, review formats, or spec helpers

## How Guidelines Are Used

1. Shared guidance is authored once in `ai-guidelines/`.
2. Public skills copy the shared files they need into `references/_shared/`.
3. Project-only maintenance skills under `.claude/skills/`, `.cursor/skills/`, and `.agents/skills/` reference `ai-guidelines/` directly instead of duplicating long text.
4. Canonical agent personas live in `agent-personas/`, and runtime-specific agent installs are generated from them into `agents-claude/`, `agents-cursor/`, and `agents-codex/`.

This model keeps published skills self-contained while preserving one canonical source of truth for shared behavior.
