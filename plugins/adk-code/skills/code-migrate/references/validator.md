# `code-migrate` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-migrate.md`.

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt`.
- [ ] Repo resolved; `<from>` and `<to>` versions resolved precisely (no "latest" without resolution + Decision-table entry).
- [ ] Slug derived.

## Phase 1 — preflight

- [ ] `git status` clean. Dirty → ask.
- [ ] Branch captured. Protected → branch-creation prompt fired.
- [ ] Validation commands resolved: typecheck + lint + test + **build**.
- [ ] **Baseline = green**: all four commands green on HEAD. A migration on red is BLOCKED.
- [ ] Current dependency versions snapshotted (for the report's before/after).

## Phase 2 — read upstream migration guide

- [ ] `migration-notes.md` exists.
- [ ] `migration-notes.md` cites the source URL + fetch timestamp.
- [ ] Each breaking-change rule has a quote (≤15 words; verifier or auditor can spot-check).
- [ ] Each rule is labeled "applies to us: yes / partial / no" with a one-line evidence.
- [ ] If guide is paywalled / unavailable: STOP and surface; the skill REQUIRES an authoritative source.

## Phase 3 — inventory

- [ ] `migration-inventory.md` exists.
- [ ] One row per "applies-to-us" rule from `migration-notes.md`.
- [ ] Each row has: pattern, file count, site count, 2-3 sample sites.
- [ ] Rules with `count = 0` are still listed (proves you checked).

## Phase 4 — plan groups

- [ ] `plan.md` exists with `## Groups` table.
- [ ] Each group has: name, file count, strategy, validation strategy.
- [ ] Sequence ordered: low-blast-radius first; high last.
- [ ] Dependency version bump is in the LAST group (or the order is documented as required by the guide).
- [ ] `## Items NOT applied` lists every guide rule the plan does not address, with reason.
- [ ] Approval gate fired (unless `--auto`).

## Phase 5 — execute group-by-group

For each group:

- [ ] Implementer subagent ran with the group's rules + sample sites.
- [ ] Per-group validation ran (typecheck + scoped tests).
- [ ] Per-group output captured in `validation/per-skill/code-migrate.md` under the group's section.
- [ ] If RED: stopped the chain; surfaced; operator decided next action.
- [ ] No file outside the group's planned set was touched (or scope creep was re-confirmed).

## Phase 6 — final validation

- [ ] **Full build**: green (mandatory for migrations).
- [ ] **Full test suite**: green. Test count matches baseline (or differences documented).
- [ ] **Typecheck**: green.
- [ ] **Lint**: green.
- [ ] **Smoke check**: ran (per migration type — Node bump → entry-point invocation; framework migration → dev server start; etc.).
- [ ] All outputs captured.

## Phase 7 — pre-handoff

- [ ] `report.md` covers: Migration, Files changed, Groups applied, Migration guide rules applied, Migration guide rules NOT applied, Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` exists.
- [ ] `report.md` includes the version diff (`package.json` / `build.gradle` / `Cargo.toml` before/after).
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## Hard checks (the skill cannot pass without these)

1. `migration-notes.md` exists with a source URL and ≤15-word quotes.
2. `migration-inventory.md` exists with per-rule counts.
3. `plan.md` has `## Groups` table.
4. Per-group validation evidence is present in `validation/per-skill/code-migrate.md`.
5. Final build is green.
6. Final test suite is green.
7. The dependency-version diff is recorded in the report.
8. Items NOT applied are listed with reasons.

## On any check failure

1. Log the failure under `## Validator failures`.
2. Block the next phase.
3. If the same kind of failure repeats 3 times in this session, surface to the user.
4. If a group goes red and revert/re-think doesn't recover, STOP for operator input — don't paper over the failure to keep moving.
