---
name: publish-ship
description: |
  Run the pre-launch and launch sequence for a change about to go to production — pre-flight checklist, feature-flag wiring, staged rollout plan (off → team → small % → larger % → full), monitoring + rollback readiness, post-deploy first-hour checks, and flag-cleanup follow-up. Different from `@adk:publish-github` (a.k.a. `adk-publish-github`) which handles the PR/merge mechanics, and from `@adk:cicd-monitor` (a.k.a. `adk-cicd-monitor`) which watches CI for that PR. Use as the final gate before merging-to-main or deploying-to-prod when the change has user impact. Do not use for trivial doc-only changes (skip), urgent hotfixes during active incidents (use `@adk:build-bugfix` (a.k.a. `adk-build-bugfix`) + `@adk:cicd-monitor`), or for the actual deploy command (that's your platform's CLI / PaaS).
metadata:
  category: publish
  kind: task
  layer: 8
  modes: [auto]
---

# publish-ship — pre-launch checklist + staged rollout + rollback readiness

Standalone task skill under the `@adk:publish` (a.k.a. `adk-publish`) category router. Treats deploy as separate from release (feature-flag-gated by default), enforces reversibility, and ensures the first hour after launch is observable.

## Core principle: deploy ≠ release

Code reaches production via **deploy**. Users see the new behavior via **release** (flipping a feature flag from off → on for that user segment). Decoupling them is what makes shipping safe.

## When to use

- A user-visible feature is about to merge to main / deploy to prod.
- A risky internal change (data-migration, infra config, dep major bump) is about to ship.
- A re-launch after a rollback.
- Any change where "what do we do if this is wrong in 10 minutes" needs a written answer.

## When NOT to use

- Doc-only PRs that affect no runtime → skip and merge.
- Urgent hotfix during an active incident → `@adk:build-bugfix` (a.k.a. `adk-build-bugfix`) + `@adk:cicd-monitor`; come back to this skill for the post-incident retro.
- The actual deploy command — this skill prepares for it; the PaaS / CLI does it.
- Non-prod merges to a long-lived feature branch (no user impact yet).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<change>` | yes | What is being shipped (PR link, branch, or summary). |
| `<blast radius>` | yes | Who can be affected — % of users / specific tenants / internal-only. |
| `<flag>` | optional | The feature flag name (or "none — full launch"). |
| `<rollback strategy>` | yes | Flag flip / `git revert` + redeploy / DB-migration reverse / forward-fix only. |
| `--auto` | optional | Skip approval gates (still validates). |

## Workflow

1. **Confirm intent** — restate the change, blast radius, flag (or absence), rollback strategy. Approval gate unless `--auto`.
2. **Pre-flight checklist** — run through `references/pre-launch-checklist.md`. Every item is OK / WARN / BLOCKER. BLOCKER stops the launch until resolved.
3. **Feature-flag readiness** — confirm the flag name, default value (off in prod), targeting (team → 1% → 10% → 50% → 100%), and the cleanup ticket (≤ 2 weeks after 100%). For "no-flag" launches, document why and what the rollback is.
4. **Staged rollout plan** — write the rollout schedule with checkpoints and the SLO/SLI windows that gate each stage (see `references/staged-rollout.md`).
5. **Rollback readiness** — verify the rollback path was tested (or at least dry-run-validated). One of:
   - Flip the flag back (default — fastest).
   - `git revert <merge-sha> && redeploy`.
   - Reverse migration (DB) — must be tested separately.
   - Forward-fix only (acceptable only when reverse is impossible; document why).
6. **Monitoring readiness** — confirm dashboards / alerts / SLOs are in place for: error rate, p95 latency, business metric impacted, client-side errors (web-vitals + error logger). Use `@adk:observability-datadog` (a.k.a. `adk-observability-datadog`) to verify.
7. **Approval gate** — present the checklist + plan to the user (or auto-approve under `--auto`).
8. **Hand off to the deploy mechanism** — the actual deploy is via your PaaS/CLI/CD pipeline; this skill does NOT run it. Pair with `@adk:cicd-monitor` for the watch-CI step.
9. **First-hour post-deploy checks** — list the explicit checks to run in the first 60 min (errors, latency, business signal, customer reports). See `references/first-hour-checklist.md`.
10. **Report** — checklist status, rollout schedule, flag info, rollback path, monitoring links, post-deploy check schedule, flag-cleanup ticket reference.

## Hard rules

- **Pre-flight BLOCKERs are non-negotiable.** No green checklist, no launch.
- **No flag = no launch** for user-visible changes unless the user explicitly accepts the risk and documents the rollback path.
- **Rollback is tested or it doesn't exist.** "We can revert" without verification is wishful thinking.
- **Monitoring must precede release**, not follow it.
- **Flag cleanup is part of the change.** A 6-month-old flag is a maintenance liability — file the cleanup ticket NOW with a 2-week target.
- **First-hour checks are scheduled, not "we'll see if Slack pings".** Times in the calendar; humans assigned.
- **A rollback is not a failure.** It is a feature working as designed. Treat the metrics, not your ego.

## Anti-patterns

- "It's a small change, no flag" for user-visible code — small changes break things too.
- Deploying on Friday 5pm with no on-call — predictable outcome.
- Single-stage rollout (off → 100%) for high-blast-radius changes.
- Monitoring "added later" — you'll be diagnosing blind during the bad hour.
- Flag still around 6 months later — it's now permanent config, not a flag.
- Manual rollback steps that nobody has rehearsed.
- "It works in staging" treated as proof — staging ≠ prod.
- Forward-fix-only chosen because reverse is "annoying" — real reasons only.

## Examples

```
adk-publish-ship "Ship the new pricing page" --blast-radius all-logged-out --flag new_pricing_page --rollback flag-flip
```

```
adk-publish-ship "Roll out v2 search re-ranker" --blast-radius 100%-search-traffic --flag search_v2 --rollback flag-flip
```

```
adk-publish-ship "Drop legacy /v1/users endpoint" --blast-radius partner-api-callers --flag none --rollback revert-and-redeploy
```

## Clarifying questions (default-ask)

1. **What is the blast radius — internal-only, % of users, specific tenants, full?** — _How to pick:_ Lower-blast = fewer rollout stages allowed; higher-blast = more stages, longer windows.
2. **What is the rollback strategy and has it been tested?** — _How to pick:_ Flag flip > revert + redeploy > reverse migration > forward-fix only. Tested > assumed.
3. **What monitoring + SLO will tell us this is going wrong in the first hour?** — _How to pick:_ Error rate, p95 latency, business signal (orders, sign-ups, search CTR), client-side errors. If you cannot name one, do not launch.

## Default vs detailed output

**Default report:** Pre-flight checklist (OK/WARN/BLOCKER counts) + rollout schedule + flag info + rollback path + monitoring links + first-hour check schedule + flag-cleanup ticket ref.

**Detailed report (on request or `--verbose`):** Add the per-item checklist evidence, the SLO/SLI thresholds per rollout stage, the dashboard query strings, the on-call rotation for the launch window, and the post-launch retro template.

**Artifact:** `launch-pack` — Pre-flight checklist log + rollout schedule + first-hour checks + flag-cleanup follow-up filed.

**Artifact path:** `.temp/notes/ship-<slug>-checklist.md` (pre-flight evidence), `.temp/notes/ship-<slug>-rollout.md` (rollout schedule + first-hour checks). Real PR/issue/ticket references go in the report.
