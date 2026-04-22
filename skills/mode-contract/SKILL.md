---
name: mode-contract
description: |
  Documents the universal `--mode auto | review | fix` switch every applicable adk skill must support, and the orthogonal `--auto` flag that skips approval gates. Reference-only — never auto-invoked. Read this when you are authoring a new skill or trying to understand which mode to pass to an existing one.
metadata:
  category: meta
  kind: task
  modes: [auto]
  layer: 0
disable-model-invocation: true
---

# mode-contract — universal `--mode` reference

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
