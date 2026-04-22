# `cicd-fix` — modes

This skill supports the following `--mode` values (declared in SKILL.md frontmatter under `metadata.modes`):

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Brainstorm + plan + execute end-to-end. Approval gates active unless `--auto`. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.
