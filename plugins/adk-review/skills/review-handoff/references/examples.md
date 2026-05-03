# `review-handoff` — worked examples

## Example 1 — end of day; resume tomorrow

**Prompt:** `/adk-review:review-handoff --auto`

**Phase 0:** picks most-recent task slug `feature-pricing-rework` from `.temp/task-feature-pricing-rework/.last-modified` (touched 12 min ago).

**Phase 1:** preflight green. Repo: `acme/storefront`. No `--post-to`.

**Phase 2:**
- Reads `prompt.txt` → "implement tiered pricing for B2B".
- Reads `skill-plan.md` → ran `/adk-code:code-write` then `/adk-review:review-code-changes`.
- Reads `code/plan.md` → 4 of 5 implementation tasks done.
- Reads `review/findings.md` → 1 Should-Have remaining (missing test for tier transition).
- Git: branch `feature/pricing-rework`, dirty (3 files), 6 commits ahead of `main`, no stash.

**Phase 3 — synthesize handoff.md:**

```markdown
# Handoff — feature-pricing-rework

_Authored 2026-05-03T18:42Z by adk-review:review-handoff for Sujeet Jaiswal._

## Task summary
Implementing tiered pricing for B2B in `acme/storefront`. Per the prompt: "implement tiered pricing for B2B". Plan in `code/plan.md` had 5 tasks; 4 are done; 1 remains. Self-review (`review-code-changes`) flagged 1 Should-Have (missing test for tier transition).

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | architecture | per-customer tier table | discussed at platform sync 2026-05-01; ADR drafted |
| 2 | DB column | numeric(10,2) | matches `prices.amount` shape |
| 3 | API surface | `/v1/customers/<id>/tier` | follows existing `/v1/customers/<id>/...` convention |
| 4 | test coverage | unit-only for now | integration test is in remaining-work |

## Work completed
- Schema migration `migrations/2026_05_03_tiered_pricing.sql` — commit `a1b2c3d`.
- Model `src/billing/tier.ts` (with `Tier`, `TierResolver` classes) — commit `b2c3d4e`.
- API endpoint `src/api/customer-tier.ts` — commit `c3d4e5f`.
- Unit tests (8/9 cases passing) — commit `d4e5f6g`.
- Self-review run; findings at `.temp/task-feature-pricing-rework/review/findings.md`.

## Remaining work
1. Write the 9th unit test (tier transition: free → pro → enterprise) at `src/billing/tier.test.ts:120-160`.
2. Write integration test covering `POST /v1/customers/<id>/tier` end-to-end.
3. Update CHANGELOG.md with the user-facing summary.
4. Open PR with description from `/adk-docs:docs-pr-description`.

## Blockers
| Blocker | Owner | ETA | Workaround |
| --- | --- | --- | --- |
| (none) | — | — | — |

## Key files touched
| File | Why | Last touched |
| --- | --- | --- |
| `migrations/2026_05_03_tiered_pricing.sql` | new schema | commit a1b2c3d |
| `src/billing/tier.ts` | new model | commit b2c3d4e |
| `src/billing/tier.test.ts` | unit tests (8/9 cases) | uncommitted; see git status |
| `src/api/customer-tier.ts` | new endpoint | commit c3d4e5f |

## Files NOT touched (deliberately)
| File | Why not |
| --- | --- |
| `src/billing/legacy-pricing.ts` | will be deprecated in v2; left untouched |
| `src/admin/billing-dashboard.tsx` | UI work scoped to a separate PR per ADR |
| `migrations/2026_05_02_seed_tiers.sql` | considered seeding default tiers; deferred — needs ops sign-off |

## Git state
- Branch: `feature/pricing-rework`
- Dirty: yes (3 files: `src/billing/tier.test.ts`, `CHANGELOG.md`, `docs/api.md`)
- Last 10 commits:
  - d4e5f6g unit tests for Tier (8/9 cases)
  - c3d4e5f add POST /v1/customers/<id>/tier
  - b2c3d4e Tier and TierResolver
  - a1b2c3d migration: add customer_tier table
  - ... (older, on main)
- Uncommitted diff: +124/-12 across 3 files
- Stash: empty

## Environment
- Editor: cursor
- Shell: zsh
- pwd: /Users/sujeet/code/acme/storefront
- Tools: node v22.7, npm 10.8.2, docker 27.3
- Env vars relied on (names only): `STRIPE_API_KEY`, `DATABASE_URL`

## Next step
Run `npm test src/billing/tier.test.ts` to confirm the 8 passing cases; then add the 9th case at `src/billing/tier.test.ts:120-160` (tier transition test). After that:

```
git add -A && git commit -m "test: tier transition" && \
  git push && \
  /adk-docs:docs-pr-description --auto && \
  gh pr create --body-file .temp/task-feature-pricing-rework/pr-body.md
```
```

**Phase 6 — surface:** "Handoff written to `.temp/task-feature-pricing-rework/handoff.md`. Next: write the 9th test case; see handoff for the full command. Want me to also `--post-to slack`?"

---

## Example 2 — incident handoff at end of on-call shift

**Prompt:** `/adk-review:review-handoff --post-to slack`

**Phase 0:** picks most-recent task `incident-checkout-13-00` (an incident triage from 2h ago).

**Phase 1:** Slack workspace connector reachable. `~/.config/adk/slack.md.incident_channel: "#incidents"`. Confirmed.

**Phase 2:**
- Reads `investigation/incident.md` → root cause hypothesis: deploy at 12:58 changed user-count query; column renamed last week.
- Reads `investigation/datadog.md` → DD evidence (graph link, error spike).
- Git: branch `main`, clean (no code changes; just investigation).

**Phase 3 — synthesize:** as Example 1 but with incident-shaped sections (e.g. "Mitigation status: still investigating; @bob taking over").

**Phase 5 — post to Slack (gated):**

```
[adk-review:review-handoff] task=incident-checkout-13-00 ... mode=auto+post-to-slack ...

Post handoff to Slack channel #incidents?
Preview: "Handoff for incident-checkout-13-00 — Symptom: dashboard shows 0 active users since 13:00. Root cause hypothesis: deploy at 12:58 ..."

[y/N]
> y
```

Slack post via workspace connector. Captured URL. Written to `handoff-postback.md`.

**Phase 6 — surface:** "Handoff posted to #incidents (link); also at `.temp/task-incident-checkout-13-00/handoff.md`. @bob is the next on-call per `slack.md.on_call_users`; consider DM-ing them."

---

## Example 3 — interactive (`-i`) walks each section

**Prompt:** `/adk-review:review-handoff -i`

**Phase 4 — propose (interactive):**

```
Handoff draft has 10 sections. Walking each.

[1/10] Task summary:
  Implementing tiered pricing for B2B in acme/storefront. Per the prompt: "implement tiered pricing for B2B". Plan in code/plan.md had 5 tasks; 4 are done; 1 remains. Self-review (review-code-changes) flagged 1 Should-Have (missing test for tier transition).

[a]ccept | [e]dit | [s]kip
> e

(opens $EDITOR with the section)

(user edits to add: "Note: switched from JSONB to a separate column at Tony's suggestion last Friday; ADR draft pending")

OK, accepted with edit.

[2/10] Decisions:
  ...
```

User walks each, refining the inferred sections.

---

## Example 4 — multi-day task; daily handoff at end-of-day

**Day 1 prompt:** `/adk-review:review-handoff --auto` → handoff.md written.

**Day 2 morning:** user reads handoff.md, picks up where they left off.

**Day 2 evening prompt:** `/adk-review:review-handoff --auto`

**Phase 0:** same task slug; the prior `handoff.md` is moved to `.archive/2026-05-03T18-42Z/handoff.md`.

**Phase 3:** new handoff.md reflects today's progress; "Files NOT touched" preserves the prior list + any new entries.

**Phase 6:** "Handoff updated. Day 2 added: implemented integration test, deferred admin UI per architectural sync."

The diff between yesterday's and today's handoffs is itself a useful artifact — `git diff .temp/task-<slug>/.archive/2026-05-03T18-42Z/handoff.md .temp/task-<slug>/handoff.md` shows day-over-day progress.

---

## Example 5 — post-to-pr with post-confirmation

**Prompt:** `/adk-review:review-handoff --post-to pr`

**Phase 0–3:** as Example 1.

**Phase 5 — post to PR:**

```
Post handoff as a comment on PR acme/storefront#103?
Preview: "Handoff for feature-pricing-rework — Implementing tiered pricing for B2B ..."

[y/N]
> y
```

`gh pr comment 103 --body-file handoff.md` → returned receipt ID `c-7891`.

**POST-CONFIRMATION:** wait 5s → re-fetch → c-7891 visible (confirmed).

**Phase 6 — surface:** "Posted to PR #103 (link); confirmed at 5s; also at handoff.md."

---

## Example 6 — empty task slug (nothing to hand off)

**Prompt:** `/adk-review:review-handoff` in a fresh terminal session.

**Phase 0:** scans `.temp/task-*/` → finds none from the past hour (or all are empty).

**STOP** with:

```
[adk-review:review-handoff] no recent task found.

`.temp/task-*/` either doesn't exist or has no recently-touched directories. To use review-handoff:
  - Run any other adk skill first (it'll create .temp/task-<slug>/), OR
  - Pass an explicit `<task-slug>` arg: /adk-review:review-handoff old-task-name
```

The skill is opinionated about not synthesizing from nothing.
