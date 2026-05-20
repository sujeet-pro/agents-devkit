# feature-flow-tracing — flags, experiments, dynamic configs

When the diff introduces or modifies a code path gated by a feature flag, experiment, or dynamic config, the reviewer must trace the **full flow** before deciding the change is safe. The `feature-flow` finding dimension captures gaps in that flow.

## What we trace

For each gate / experiment / config reference in the diff:

| Element | Where to find it | What to verify |
|---|---|---|
| **Flag definition** | `adk-mcp-statsig.Get_Gate_Details_by_ID` (or `..._Experiment_..._Dynamic_Config_...`) | The gate exists. Its current rollout state. Its targeting rules. |
| **Code reference (on path)** | `scripts/query_index.py --feature-flag <name>` (greps the diff + worktree) | Every `if (flag.X)` / `if useGate("X")` / `getConfig("X")` call site, in both the new code and the surrounding files. |
| **Kill switch** | A way to disable the new path WITHOUT a deploy. Usually the same flag's "off" branch. | The "off" branch returns the prior behavior (graceful), not an error or no-op. |
| **Fallback** | The behavior when the flag is unreachable (Statsig outage). | The code defaults to a safe value, not `false` if `false` breaks the user. |
| **Observability** | Logs / metrics / traces tagged with the flag's value | At least one signal that lets you see "this user got the flag = X branch". |
| **Test coverage** | Unit / integration tests | Both the on-path and the off-path are tested. |
| **Cleanup plan** | Statsig audit log / Jira ticket / PR description | Either the flag is permanent (a kill switch), or there's a stated cleanup date / ticket. |

## When the dimension fires

The reviewer emits a `feature-flow` finding when **any** of these hold:

- Flag is referenced in the diff but the gate doesn't exist in Statsig (typo, deleted gate, wrong workspace).
- Flag is referenced but the rollout is at 100 % AND the off-branch tests fail / are missing — code that can never be turned off.
- The off-branch returns an error, not the prior behavior — the kill switch is a hard fail.
- No metric / log emits the flag's value — you can't observe rollout.
- The PR's description says "behind feature flag X" but no flag reference appears in the code (mismatch between intent and implementation).
- An experiment is referenced but no analysis plan / success metric is named in the PR body or linked doc.
- A dynamic config is read but never re-fetched (cached at boot, won't pick up config changes).

## How to run the trace

`scripts/query_index.py --feature-flags-in-diff` parses `diff.patch`, finds every flag/experiment/config call, and emits JSON:

```json
[
  {
    "name": "checkout-redesign-v2",
    "kind": "gate",
    "call_sites": [
      {"file": "src/checkout/page.tsx", "line": 42, "added_in_diff": true},
      {"file": "src/checkout/page.tsx", "line": 88, "added_in_diff": false}
    ],
    "statsig": {
      "status": "in_review",
      "rollout_pct": 5,
      "rules": ["country == US AND user_age >= 30 days"],
      "last_modified": "2026-05-12T14:00Z",
      "owner": "checkout-team"
    },
    "kill_switch": "present",
    "fallback_value": "false",
    "observability": ["log: checkout.flag_exposure", "metric: checkout.flag_value{flag=X}"],
    "test_coverage": {"on_branch": "yes", "off_branch": "missing"},
    "issues": ["off_branch_test_missing"]
  }
]
```

The reviewer reads this and emits findings for each non-empty `issues[]`. Confidence is `high` when Statsig MCP is reachable, `med` when it's not (the script falls back to repo grep only — gate state is unknown).

## Statsig MCP availability

When `adk-mcp-statsig` is reachable, the script populates `statsig.*`. When it's not:

- `statsig` field is `null`.
- The finding includes `[statsig: skipped]` in the body.
- Confidence drops to `med` for the gate's state-related claims.
- Confidence stays `high` for the code-side claims (call sites, kill switch presence, observability).

## Dynamic config specifics

For `Get_Dynamic_Config_Details_by_ID` references in the diff:

- Check the rule set: does the code handle ALL possible values? A boolean config with a `null` rule will return `null`, not `false` — code that does `if (config.X) {…}` may behave wrong.
- Check the fetch frequency: is the config re-read each request, or cached at boot? Cached-at-boot is fine when the config is rollout-tier; not fine when it's a kill switch.

## Experiment specifics

For `Get_Experiment_Details_by_ID` references:

- Verify the experiment is in the right environment (prod vs staging vs dev).
- Verify the metric source is correct (`Get_List_of_Metric_Sources`).
- Check the targeting: does the diff add code that runs for users NOT in the experiment? That's exposure bias.

## Refusals

- Statsig MCP writes (create/update gate, start experiment) are **out of scope** for a review. Constitution §I.5. The skill never proposes a Statsig mutation.
- If the diff itself mutates Statsig via SDK admin calls (unusual), surface as a `security` finding (admin calls in product code = privilege escalation risk).
