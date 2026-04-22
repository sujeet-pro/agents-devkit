# frontend-design Validator

The validator gate `adk-frontend-design` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/frontend-design-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Surface clear | Page / component / flow — picked deliberately | BLOCKER if unclear |
| User goal named | What the user accomplishes is in one sentence | BLOCKER without |
| Existing system read | Existing component library / design tokens / accessibility helpers read | WARN if absent (no system yet) — generate per design-system-master.md |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (design completeness)

Run after the design is drafted; verify it covers every viewport + every interactive state + accessibility + performance.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Design system loaded | `design-system/MASTER.md` (or generated for new app) referenced for every token used | MASTER read receipt |
| All viewports covered | Mobile / tablet / desktop layouts all sketched | Per-viewport presence map |
| All interactive states enumerated | default / hover / focus-visible / active / disabled / loading / empty / error per element | State-coverage map |
| WCAG 2.2 AA met | Contrast ≥ 4.5:1 for body text; tap targets ≥ 44 CSS px; focus visible; keyboard map present | Per-rule check |
| Industry anti-patterns avoided | Cross-checked against `<task>-industry-anti-patterns.md` for the target industry | Anti-pattern grep |
| Pre-delivery checklist walked | Every item from `<task>-pre-delivery-checklist.md` checked or surfaced | Checklist coverage |
| Motion has reduced-motion fallback | Every animation has a documented `prefers-reduced-motion` fallback | Per-animation check |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Design artifact written | `.temp/drafts/design-fe-<slug>.md` (+ optional sketch) in documented shape | File path + size |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/frontend-design-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/frontend-design-<slug>.md
```
