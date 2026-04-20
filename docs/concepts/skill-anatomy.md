---
title: Skill Anatomy
description: What every ADK skill looks like on disk and the per-skill flat references model.
order: 3
---

# Skill Anatomy

A **skill** is a single specialist playbook. `adk-build-feature` is the playbook for implementing code. `adk-review-pr` is the playbook for reviewing a PR. `adk-docs-write` is the playbook for authoring docs. Every skill follows the same shape so a coding agent can switch between them without relearning anything.

## Directory layout

A public skill lives at `skills/<name>/` and contains:

```
skills/<name>/
├── SKILL.md                    # entry point: frontmatter + thin orchestrator + managed references block
└── references/                 # FLAT — no subdirectories, no _shared/
    ├── persona.md              # the agent persona that drives this skill
    ├── workflow.md             # task-specific phase expansion
    ├── output-format.md        # response shape and severity rules
    ├── constitution.md         # subset of non-negotiables that apply
    ├── working-artifacts.md    # the .temp/ rule (where relevant)
    ├── research-protocol.md    # repo-first research method (research / audit / brainstorm)
    ├── brainstorming-workflow.md # full loop (only adk-plan-brainstorm)
    ├── review-comment-format.md  # finding format (review / audit / docs-review)
    ├── mcp-fallback.md         # preferred MCP and the manual fallback (when applicable)
    ├── anti-patterns.md        # what to avoid
    └── examples.md             # sample triggers and report shape
```

This is the contract:

- Directory name matches the frontmatter `name`.
- Public skills start with `adk-`.
- Each skill stays usable when copied out of this repository.
- `references/` is **flat**. No subdirectories, no `_shared/`, no cross-skill references by relative path.
- Every reference file is **owned by this skill** — a copy, not a symlink.

## SKILL.md frontmatter

Spec-compliant. Only these top-level keys are allowed: `name`, `description`, `compatibility`, `metadata`, `license`, `allowed-tools`.

```yaml
---
name: adk-build-feature
description: Implement a new feature, fix a bug, or enhance behavior with a short plan, scoped reads, smallest correct change, and repo-native validation. Use when the deliverable is a code change. Do not use for behavior-preserving refactors (use adk-build-refactor) or framework upgrades (use adk-build-migrate).
---
```

Field rules:

- `name` and `description` drive activation. Description is the trigger sentence the harness matches against user intent.
- `description` <= 1024 characters.
- The body is <= 500 lines (soft cap; warning only).
- Cross-skill references in the body are by **name only** (`adk-plan-brainstorm`), never relative paths into another skill folder.

## Managed references block

The bottom of each `SKILL.md` carries a managed block listing every file shipped in `references/`:

```
<!-- adk:references:start -->

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/workflow.md` | Step-by-step protocol for this skill. |
| `references/output-format.md` | Response shape and severity rules. |
| ... |

<!-- adk:references:end -->
```

The block is regenerated mechanically; everything else in `SKILL.md` is hand-authored.

## No shared guidance

There is no `ai-guidelines/`, no `references/_shared/`, no auto-propagation script. If you change `references/constitution.md` inside `adk-build-feature`, that change does not propagate to `adk-build-refactor`. This is the explicit trade-off:

- **Pro:** Each skill folder can be copied out into any other agent setup and works as-is.
- **Pro:** No "I edited the canonical file but forgot to refresh" bugs.
- **Con:** Same content lives in many places; a change with broad intent must be edited in every relevant skill by hand.

## Skill kinds

| Kind | Examples | What goes in the body |
| --- | --- | --- |
| Top router | `adk` | Intent table; routes to one of the 8 categories |
| Category router | `adk-plan`, `adk-build`, ... | Task selection table; routes to a task skill |
| Task skill | `adk-plan-brainstorm`, `adk-build-feature`, ... | The actual workflow + output format + examples |

Routers ship a minimal `references/` (`constitution.md`, `anti-patterns.md`). Task skills ship the full vocabulary that applies to them.

## Validation

Run `npm run validate` to check structure across all 37 skills. It enforces:

- Spec-compliant frontmatter only.
- Frontmatter `name` matches folder.
- Description <= 1024 chars.
- `references/` is flat (no subdirs, no `_shared/`).
- Any `references/<file>` cited inline in `SKILL.md` exists in the same folder.

## Related

- [Philosophy](./philosophy.md) — the rules every skill inherits.
- [Agents](./agents.md) — the per-provider custom subagents.
- [Public Skills reference](../reference/skills/) — the full catalog.
