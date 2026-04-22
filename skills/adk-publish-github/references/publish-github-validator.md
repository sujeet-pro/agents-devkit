# publish-github Validator

The validator gate `adk-publish-github` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/publish-github-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Action chosen | create-pr / update-pr / comment / label / merge — explicit | BLOCKER if unclear |
| GitHub auth | `gh auth status` succeeds OR github MCP authenticated | BLOCKER otherwise — point at install instructions |
| Repo identity | `<org>/<repo>` resolved from URL or `git remote get-url origin` | BLOCKER otherwise |
| Never-auto guard | If action is `pr-merge` / force-push: explicit user approval required even under `--auto` | BLOCKER without approval |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-publish validation (GitHub action readiness)

Run immediately before the gh / MCP write; every check must pass before any side-effecting call.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Payload validated | Title / body / labels / assignees / base / head all valid | Per-field check |
| No secrets in body | Body scanned for tokens / passwords / API keys | Secret-scan grep |
| Idempotency | Action is idempotent (e.g., do not create duplicate PR for same branch) | Existence check |

## Phase 4: Post-publish validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Action succeeded | gh / MCP returned the expected URL / id | Returned URL / id |
| Read-back verified | `gh pr view` / MCP equivalent confirms the change landed (title matches, body matches, labels present) | Read-back diff |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/publish-github-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/publish-github-<slug>.md
```
