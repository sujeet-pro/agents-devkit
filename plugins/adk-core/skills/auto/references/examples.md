# `auto` — worked examples

## Example 1 — production bug from a Slack thread

**Prompt:** `/adk-core:auto Customer dashboard shows 0 for active users since 13:00. https://acme.slack.com/archives/C123/p1745... --auto`

**Phase 0:**

- Slug: `dashboard-active-users-zero`.
- Classification: `investigate, code` (multi-verb).
- Links: 1 Slack → queue context-gather.
- Confidence: high.

**Phase 1:** preflight green. DD MCP reachable. `repos.md` has the dashboard repo.

**Phase 2:** context-gather pulls Slack thread + customer report into `context.md`.

**Phase 3:** chain proposed: `investigate-incident "active users 0 since 13:00" --service dashboard --window last 2h` → `code-bugfix` (only if hypothesis is code) → `review-code-changes --fix`. Auto-approved (under `--auto`).

**Phase 4:** dispatcher spawns `incident-investigator` subagent. Finds: deploy at 12:58 changed user-count query to filter by `is_active=true` but column was renamed to `active_at` last week (DD audit trail + git blame on the query file). Hypothesis confidence: high. Spawns `implementer` + `code-bugfix` to update the query + add a regression test. Spawns `code-reviewer` + `review-code-changes` to self-review.

**Phase 5:** report includes DD dashboard link as residual evidence. PR opened (under `--auto`); CI green in 4 min.

---

## Example 2 — review a PR

**Prompt:** `/adk-core:auto https://github.com/acme/checkout-api/pull/2841`

**Phase 0:**

- Bare GitHub PR URL → routes directly to `review-pr` (single skill).
- Classification: `review`. Confidence: very high.
- Slug: `checkout-api-pr-2841`.

**Phase 1:** preflight green. GitHub MCP / `gh` reachable. `repos.md` has the local checkout.

**Phase 2:** no other links → skip context-gather.

**Phase 3:** chain: `review-pr <url>` (default ownership detection). Single skill — no subagent dispatch needed.

**Phase 4:** runs `review-pr` end-to-end. Finds 1 Blocker (n+1 query), 2 Should-Have, 3 Nitpicks. Posts to GitHub (default `--auto`). Re-fetches and confirms IDs.

**Phase 5:** report links to PR comments + the local findings file.

---

## Example 3 — doc-only task

**Prompt:** `/adk-core:auto Write a runbook for the auth-token rotation procedure`

**Phase 0:** classification = `docs`. No links. Skip context-gather. Slug: `runbook-auth-token-rotation`.

**Phase 1:** preflight green.

**Phase 3:** chain: `docs-write --doc-type runbook`. No subagent needed (doc-writer agent invoked inside the skill).

**Phase 4:** skill writes `.temp/task-<slug>/draft.md`, validates against `docs.md` audience setting.

**Phase 5:** report. Optional follow-up: `docs-publish-confluence` (asks the user under non-`--auto`).

---

## Example 4 — ambiguous prompt → ask one question

**Prompt:** `/adk-core:auto fix the api`

**Phase 0:** ambiguous: which API? what kind of fix? Two clarifying questions raised, but per the rules only ask ONE first.

**Auto's response:** "I see 3 API repos in `repos.md`: `checkout-api`, `search-api`, `pricing-api`. Which one? (or paste a PR URL.)"

After the user picks, Phase 0 continues with the resolved repo, and routing proceeds normally.

---

## Example 5 — full RCA composite

**Prompt:** `/adk-core:auto post-mortem for yesterday's checkout outage at 13:00 UTC`

**Phase 0:** classification = `investigate` (specifically RCA). Slug: `rca-checkout-13-00`.

**Phase 1:** preflight green. DD + Statsig + Slack all reachable.

**Phase 3:** chain: `investigate-rca "checkout outage" --window 2026-05-02T12:00..14:00`. Single composite skill — it internally calls `investigate-incident` + `investigate-statsig --use audit-log` + `git blame`.

**Phase 4:** the composite skill produces `.temp/task-<slug>/investigation/rca.md` ready for paste into a post-mortem template.

**Phase 5:** report links the RCA doc + suggests `docs-publish-confluence` as the natural next step.