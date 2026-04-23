# `build-security` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Confirm + classify + reproduce + scan + plan + implement + test + validate + report. Approval gates active unless `--auto`. |
| `fix` | Same as `auto` but no approval gate (fully unattended). Intended for CI / `--auto` chains. **The "Ask first" tier still triggers a gate even under `fix` — security posture changes always need a human.** |

`--auto` is orthogonal and skips the *non-security* approval gates regardless of `--mode`. The "Never do" tier always refuses.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.
