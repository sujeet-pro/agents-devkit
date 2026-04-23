# `build-api` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Confirm + inventory + draft contract + audit + implement + validate + report end-to-end. Approval gates active unless `--auto`. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.
