# `docs-review` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Brainstorm + plan + execute end-to-end. Approval gates active unless `--auto`. |
| `review` | Produce findings only. Write `review.md` or post comments. Never edits source. |
| `fix` | Auto-apply this skill's own findings, then re-validate by re-running `--mode review`. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.
