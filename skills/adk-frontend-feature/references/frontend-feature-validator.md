# frontend-feature Validator

The validator gate `adk-frontend-feature` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/frontend-feature-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Stack discovered | Framework / router / state lib / styling / test framework all detected | BLOCKER if mismatch with task expectations |
| Design system loaded | `design-system/MASTER.md` (or `design-system/pages/<page>.md`) read | WARN if absent — recommend `adk-frontend-design` first |
| Existing tokens / patterns read | Component library + design tokens read; will reuse not re-invent | WARN if missing |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-merge validation (frontend implementation)

Run after the implementation is complete; verify accessibility, responsiveness, all states, and design-system conformance.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Lint + typecheck on changed files | `<repo lint>` + `<repo typecheck>` exit 0 on the change | Command output |
| Unit tests on changed code green | Tests for the changed component / hook / page green | Test output |
| a11y check passes | axe (or equivalent) green on the new / changed UI | axe report |
| Build still passes | Production build succeeds (catches CSS / asset / SSR issues) | Build output |
| All interactive states implemented | default / hover / focus-visible / active / disabled / loading / empty / error | State-coverage map |
| Responsive at 360 / 768 / 1280 | Verified at the three required viewports (+ landscape on mobile) | Per-viewport screenshot or note |
| Tokens / patterns reused | No raw hex / arbitrary px / one-off styles; tokens used | Token-usage grep |
| Industry anti-patterns avoided | Cross-checked against `<task>-industry-anti-patterns.md` | Anti-pattern grep |
| Pre-delivery checklist walked | Every item from `<task>-pre-delivery-checklist.md` checked or surfaced | Checklist coverage |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Diff staged or committed | `git status` shows the change | git status output |
| Validator log written | All four phases captured | File path + size |
| Manual follow-up captured | Every WARN from Phases 1-3 surfaces in residual risk | Follow-up list |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/frontend-feature-<slug>-validator.md` for audit. Format:

```
## Phase 1
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 2
- <gate>: OK (<evidence>)
- ...

## Phase 3
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 4
- <check>: OK | WARN (<evidence>)
- ...

Final report: .temp/reports/frontend-feature-<slug>.md
```
