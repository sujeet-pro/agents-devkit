# audit-site Validator

The validator gate `adk-audit-site` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/audit-site-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| URL reachable | HEAD / GET succeeds; not behind auth (unless creds provided) | BLOCKER if unreachable |
| Dimensions chosen | Performance / accessibility / SEO / UX / security-headers — explicit list | BLOCKER if `all` without sanity check |
| Browser MCP available | browser MCP authenticated OR fallback to curl + headless lighthouse | WARN with workaround |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-report validation (site audit completeness)

Run after dimension passes complete; verify each dimension was actually probed against the live URL.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Lighthouse / equivalent ran | Lighthouse (or equivalent) ran on key pages; results captured | Lighthouse JSON / report path |
| axe / equivalent ran for a11y | axe (or equivalent) ran on key pages; violations captured | axe report |
| Security headers checked | CSP / HSTS / X-Frame-Options / Referrer-Policy / Permissions-Policy probed | Header probe output |
| Findings have URL + selector evidence | Every finding cites the URL + CSS selector / DOM path / response header | Per-finding evidence |
| Severity honest | Severity tier matches actual impact | Per-finding severity justification |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Site audit report written | `.temp/reports/audit-site-<slug>.md` in the documented shape | File path + size |
| Raw tool output captured | Lighthouse JSON, axe report, header probes in `.temp/notes/` | Artifact list |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/audit-site-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/audit-site-<slug>.md
```
