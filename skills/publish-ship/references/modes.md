# `publish-ship` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Confirm + checklist + flag + rollout + rollback + monitoring + approval + handoff + first-hour plan + report end-to-end. Approval gates active unless `--auto`. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.

**Note:** "BLOCKER" pre-flight items always stop the launch even under `--auto`. Launching with a BLOCKER requires the user to explicitly resolve it; the skill cannot auto-resolve safety items.

See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.
