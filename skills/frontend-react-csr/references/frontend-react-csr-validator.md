# frontend-react-csr Validator

The validator gate `adk-frontend-react-csr` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/frontend-react-csr-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Mode chosen | new / feature / audit — explicit | BLOCKER if unclear |
| Versions researched | Current stable version of every locked-stack library captured to `.temp/notes/.../versions-<date>.md` | BLOCKER — no version is known a priori |
| Design system loaded / planned | `design-system/MASTER.md` exists (existing app) OR will be generated (new app) | BLOCKER if missing for `feature` / `audit` |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (React 19 CSR app)

Run after setup / feature / audit; verify the locked-stack + theme grid + Lighthouse + a11y bars are met.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| `npm run check` green | Lint + format + typecheck all pass | Command output |
| `npm test` green | Unit suite green; no skipped tests added | Test output |
| `npm run build` green | Production build succeeds | Build output |
| axe pass | Automated axe pass green on the built app | axe report |
| Manual keyboard pass | Every interactive surface reachable + operable via keyboard only | Keyboard-pass note |
| Theme-grid screenshots captured | 12-cell grid: paper × high-contrast × light × dark × small/base/large | Screenshot artifact paths |
| Lighthouse on `dist/` | Lighthouse run via browser MCP; CWV thresholds met (LCP < 2.5s, INP < 200ms, CLS < 0.1) | Lighthouse report |
| No off-stack libs introduced | `package.json` deps still match the locked stack (or new dep has documented justification) | Dep diff |
| Industry anti-patterns avoided | Cross-checked against `<task>-industry-anti-patterns.md` | Anti-pattern grep |
| Pre-delivery checklist walked | Every item from `<task>-pre-delivery-checklist.md` checked or surfaced | Checklist coverage |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Validation matrix in report | Per-row evidence for each Phase 3 check | Validation matrix |
| Deploy URL (if mode=new + deploy enabled) | GitHub Pages or equivalent deploy succeeded; URL returned | Deploy URL |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/frontend-react-csr-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/frontend-react-csr-<slug>.md
```
