---
title: 'mode-contract'
description: 'Documents the universal `--mode auto | review | fix` switch every applicable adk skill must support, and the orthogonal `--auto` flag that skips approval gates.'
artifact_kind: skill
skill_name: mode-contract
category: standalone
---
# mode-contract

Documents the universal `--mode auto | review | fix` switch every applicable adk skill must support, and the orthogonal `--auto` flag that skips approval gates. Reference-only — never auto-invoked. Read this when you are authoring a new skill or trying to understand which mode to pass to an existing one.

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-mode-contract` form via `agents-skills/`.

```text
/adk:mode-contract            # interactive run (Claude Code)
/adk:mode-contract --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-mode-contract` (resolved through the
`agents-skills/adk-mode-contract/` symlink).

## Source

Direct from `skills/mode-contract/SKILL.md` — this page is auto-generated.

Single source of truth for the mode switch shared across the adk skill family.

## The three modes

```
--mode auto     # default. Brainstorm + plan + execute end-to-end.
--mode review   # produce findings only. Write a review.md or post comments. Never edits source.
--mode fix      # auto-apply the skill's own findings, then validate.
```

## Orthogonal flag

```
--auto          # skip approval gates between phases. Picks documented (default) at every fork. Still validates.
```

`--mode` and `--auto` compose. `--mode fix --auto` is "auto-apply findings AND skip approval gates". `--mode review` defaults to interactive (you usually want to discuss findings before acting).

## Per-skill declaration

Every skill declares which modes it supports in frontmatter:

```yaml
metadata:
  modes: [auto, review, fix]   # all three
  modes: [auto]                # auto-only (most plan/discovery skills)
  modes: [review, fix]         # no autonomous mode (most audit / review skills)
```

## Mode semantics by skill family

| Skill family | `auto` | `review` | `fix` |
| --- | --- | --- | --- |
| `auto`, `requirements`, `scoping`, `context-gather`, `plan-*`, `temp-folder`, `mode-contract` | yes (only mode) | n/a | n/a |
| `frontend-design`, `frontend-mockup`, `docs-write`, `visualize-*`, `doc-site-*`, `setup`, `adopt-ai-in-repo`, `personal-skill-create` | yes (only mode) | n/a | n/a |
| `build-*`, `frontend-feature`, `frontend-react-csr`, `cicd-fix` | yes | n/a | yes (synonym in these — they always apply) |
| `review-pr`, `review-local`, `review-feedback`, `review-doc`, `audit-repo`, `audit-site`, `audit-pr`, `validate-browser` | yes | yes (default) | yes (apply own findings) |
| `publish-*`, `cicd-monitor`, `observability-*`, `analytics-*` | yes | n/a | n/a |

## Conventions for skill authors

1. Default mode for review/audit skills is `review`. Default for everything else is `auto`.
2. `--mode fix` for a review/audit skill must validate after applying. Re-run the same skill's `--mode review` to confirm zero findings remain.
3. `--mode fix` is forbidden in skills that touch other people's accounts, billing, or production. The skill must reject the flag with a clear error.
4. Surface the mode in the skill's status banner: `[adk:<skill>] mode=<auto|review|fix> auto-flag=<on|off>`.
5. When a skill's frontmatter declares no `modes`, `auto` is implied as the only mode.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Decision tree: which mode for which job |
| `references/modes.md` | Self-reference (this skill is THE mode contract) |
| `references/persona.md` | Reference-only persona |
| `references/workflow.md` | How another skill authors handle modes |
| `references/clarifying-questions.md` | (none) |
| `references/output-format.md` | (n/a) |
| `references/artifact-format.md` | (n/a) |
| `references/validator.md` | Validate a skill's mode declaration |
| `references/anti-patterns.md` | What NOT to do with modes |
| `references/examples.md` | Example invocations |
| `references/interaction-contract.md` | Synced from canonical |


## Related skills

- [`adopt-ai-in-repo`](./skill-adopt-ai-in-repo.md) — `@adk:adopt-ai-in-repo` (a.k.a. `adk-adopt-ai-in-repo`)
- [`audit-pr`](./skill-audit-pr.md) — `@adk:audit-pr` (a.k.a. `adk-audit-pr`)
- [`audit-repo`](./skill-audit-repo.md) — `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- [`audit-site`](./skill-audit-site.md) — `@adk:audit-site` (a.k.a. `adk-audit-site`)
- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`cicd-fix`](./skill-cicd-fix.md) — `@adk:cicd-fix` (a.k.a. `adk-cicd-fix`)
- [`cicd-monitor`](./skill-cicd-monitor.md) — `@adk:cicd-monitor` (a.k.a. `adk-cicd-monitor`)
- [`context-gather`](./skill-context-gather.md) — `@adk:context-gather` (a.k.a. `adk-context-gather`)
- [`docs-write`](./skill-docs-write.md) — `@adk:docs-write` (a.k.a. `adk-docs-write`)
- [`frontend-design`](./skill-frontend-design.md) — `@adk:frontend-design` (a.k.a. `adk-frontend-design`)
- [`frontend-feature`](./skill-frontend-feature.md) — `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`)
- [`frontend-mockup`](./skill-frontend-mockup.md) — `@adk:frontend-mockup` (a.k.a. `adk-frontend-mockup`)
- [`frontend-react-csr`](./skill-frontend-react-csr.md) — `@adk:frontend-react-csr` (a.k.a. `adk-frontend-react-csr`)
- [`personal-skill-create`](./skill-personal-skill-create.md) — `@adk:personal-skill-create` (a.k.a. `adk-personal-skill-create`)
- [`requirements`](./skill-requirements.md) — `@adk:requirements` (a.k.a. `adk-requirements`)
- [`review`](./skill-review.md) — `@adk:review` (a.k.a. `adk-review`)
- [`review-doc`](./skill-review-doc.md) — `@adk:review-doc` (a.k.a. `adk-review-doc`)
- [`review-feedback`](./skill-review-feedback.md) — `@adk:review-feedback` (a.k.a. `adk-review-feedback`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
- [`scoping`](./skill-scoping.md) — `@adk:scoping` (a.k.a. `adk-scoping`)
- [`setup`](./skill-setup.md) — `@adk:setup` (a.k.a. `adk-setup`)
- [`temp-folder`](./skill-temp-folder.md) — `@adk:temp-folder` (a.k.a. `adk-temp-folder`)
- [`validate-browser`](./skill-validate-browser.md) — `@adk:validate-browser` (a.k.a. `adk-validate-browser`)
