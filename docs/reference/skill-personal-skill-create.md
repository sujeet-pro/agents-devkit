---
title: 'personal-skill-create'
description: '|'
skill_name: personal-skill-create
category: task
---
# personal-skill-create — scaffold user-composed skill

## When to use

- User: "I want a skill that combines X + Y + Z."
- User has a recurring multi-step task that calls several adk skills.
- User wants to capture a repeatable workflow as a named slash-command.

## When NOT to use

- Authoring a skill inside this plugin (use the templates by hand).
- One-off task that doesn't repeat (just run the skills directly).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<skill-name>` | yes | kebab-case, no `adk-` prefix; will become `.claude/skills/<name>/` |
| `<purpose>` | yes | One paragraph |
| `<composes>` | yes | List of `@adk:*` skills + `agents/<role>.md` subagents to call |
| `<install-target>` | optional | `claude` (default) / `cursor` / `agents` (generic) |

## Workflow

1. Phase 1 validator. Skill name kebab-case + not colliding with existing.
2. Read each composed skill's SKILL.md (extract input/output contract).
3. Generate `<install-target>/skills/<name>/SKILL.md` with:
   - Frontmatter (`name`, `description` derived from purpose, `metadata.modes: [auto]`).
   - "When to use" / "When NOT to use" sections.
   - "Workflow" section with each composed skill called in order, with input/output mapping.
   - "Output" section pointing to a `.temp/task-<slug>/personal-<name>/` folder.
4. Generate `references/how-it-works.md` with a mermaid sequence diagram of the composed calls.
5. Generate stub references via the standard set (persona, validator, etc.).
6. (Don't propagate `interaction-contract.md` — the personal skill should rely on whatever runtime it's installed into).
7. Phase 4 validator. Smoke-test by listing it (Claude: `/reload-plugins` then check `/help`; Cursor: re-open chat).

## Output

```
<install-target>/skills/<skill-name>/
├── SKILL.md
└── references/
    ├── how-it-works.md
    ├── workflow.md
    ├── persona.md
    ├── ...
```

Plus a one-paragraph instructions file at `.temp/personal-skill-<skill-name>-readme.md` describing how to test it.

## Mode

`auto` only.

## Anti-patterns

- Embedding plugin-internal logic in a personal skill — always REFERENCE adk skills, never copy them.
- Naming with `adk-` prefix (only this plugin's skills use that).
- Hard-coding paths that won't work outside the user's machine.
- Skipping the smoke test.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Scaffold flow + composition pattern |
| `references/modes.md` | auto only |
| `references/persona.md` | The skill scaffolder |
| `references/workflow.md` | Detailed steps |
| `references/clarifying-questions.md` | Name, purpose, composition list |
| `references/output-format.md` | Where the new skill lands |
| `references/artifact-format.md` | Standard skill folder shape |
| `references/validator.md` | Frontmatter validity + smoke test |
| `references/anti-patterns.md` | What NOT to do |
| `references/composition-template.md` | Sequence-diagram + input/output mapping example |
| `references/examples.md` | 3 worked examples (PR digest, weekly audit, on-call summary) |
| `references/interaction-contract.md` | Synced from canonical |
