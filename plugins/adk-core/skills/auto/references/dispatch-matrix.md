# `auto` — dispatch matrix (full prompt-pattern → skill mapping)

Triggers → skill set → subagent. Multiple rows can fire per prompt.

## Code change (`adk-code`)


| Trigger                                                                            | Skill                    | Subagent                                          |
| ---------------------------------------------------------------------------------- | ------------------------ | ------------------------------------------------- |
| "add … to …" / "implement Y" / "build feature X" / "extend the X"                  | `adk-code:code-write`    | `implementer`                                     |
| "fix the bug …" / "X is broken" / "Y crashes when Z" / "Customer reports …"        | `adk-code:code-bugfix`   | `implementer` + `test-engineer` (regression test) |
| "extract …" / "rename … everywhere" / "split this 800-line file" / "deduplicate …" | `adk-code:code-refactor` | `implementer`                                     |
| "upgrade React 18 → 19" / "Spring Boot 2 → 3" / "migrate to Vitest"                | `adk-code:code-migrate`  | `implementer`                                     |
| "add tests for X" / "raise coverage on Y" / "convert manual QA to automated"       | `adk-code:code-test`     | `test-engineer`                                   |
| "X is slow" / "p99 < 500ms on /api/y" / "memory regression"                        | `adk-code:code-perf`     | `implementer`                                     |
| "design endpoint for X" / "evolve the SDK surface" / "version the API"             | `adk-code:code-api`      | `implementer`                                     |
| "fix CVE-…" / "harden auth" / "add input validation for X"                         | `adk-code:code-security` | `implementer` + `security-reviewer`               |


## Code review (`adk-review`)


| Trigger                                                                         | Skill                            | Subagent                              |
| ------------------------------------------------------------------------------- | -------------------------------- | ------------------------------------- |
| "review PR " / "look at #N" / bare GitHub PR URL / "fix the PR comments"        | `adk-review:review-pr`           | `code-reviewer`                       |
| "review my changes" / "self review" / "before push" / "look at my diff vs main" | `adk-review:review-code-changes` | `code-reviewer`                       |
| "address the review comments" / "fix the PR feedback" / "respond to comments"   | `adk-review:review-feedback`     | `code-reviewer`                       |
| "draft a handoff" / "session pause" / "wrapping up for today"                   | `adk-review:review-handoff`      | (no subagent)                         |
| "audit this PR" / "sanity-check the diff" / "pre-merge gate"                    | `adk-review:audit-pr`            | `code-reviewer`                       |
| "audit the repo" / "what's the security posture of X?" / "tech-debt assessment" | `adk-review:audit-repo`          | `code-reviewer` + `security-reviewer` |


## Documentation (`adk-docs`)


| Trigger                                                                                     | Skill                              | Subagent       |
| ------------------------------------------------------------------------------------------- | ---------------------------------- | -------------- |
| "write a README for X" / "draft an ADR for Y" / "create a runbook for Z" / "document the …" | `adk-docs:docs-write`              | `doc-writer`   |
| "review this doc" / "audit the runbook" / "is this Confluence page still right?"            | `adk-docs:docs-review`             | `doc-reviewer` |
| "draft PR description" / "what's the description for this PR?" / "PR body"                  | `adk-docs:docs-pr-description`     | `doc-writer`   |
| "commit message for this" / "commit msg"                                                    | `adk-docs:docs-commit-message`     | `doc-writer`   |
| "update changelog for v1.2.0" / "release notes"                                             | `adk-docs:docs-changelog`          | `doc-writer`   |
| "diagram of the auth flow" / "sequence for X" / "ER for the orders schema"                  | `adk-docs:docs-diagram`            | (no subagent)  |
| "publish to Confluence space ENG" / "create page under …"                                   | `adk-docs:docs-publish-confluence` | (no subagent)  |
| "publish to GDrive folder X" / "as GDoc"                                                    | `adk-docs:docs-publish-gdrive`     | (no subagent)  |


## Investigations (`adk-investigate`)


| Trigger                                                                                    | Skill                                    | Subagent                |
| ------------------------------------------------------------------------------------------ | ---------------------------------------- | ----------------------- |
| "errors in checkout" / "p99 on /api/y" / "alerts firing now" / "summarize the X dashboard" | `adk-investigate:investigate-datadog`    | (no subagent)           |
| "funnel signup → checkout" / "DAU last week" / "cohort retention"                          | `adk-investigate:investigate-mixpanel`   | (no subagent)           |
| "pulse for X experiment" / "what changed in Statsig last hour" / gate-name + "exposures"   | `adk-investigate:investigate-statsig`    | (no subagent)           |
| "count of orders today" / "active SKUs" / "X aggregated by Y"                              | `adk-investigate:investigate-snowflake`  | (no subagent)           |
| "what deployed recently" / "deploys in last 2h"                                            | `adk-investigate:investigate-deploy`     | (no subagent)           |
| "why is checkout broken?" / "investigate alert from 10m ago" / "users see 500s"            | `adk-investigate:investigate-incident`   | `incident-investigator` |
| "should we ship X experiment?" / "is the Y test winning?"                                  | `adk-investigate:investigate-experiment` | (no subagent)           |
| "RCA for the X incident" / "post-mortem prep for Y"                                        | `adk-investigate:investigate-rca`        | `incident-investigator` |


## Meta (`adk-core`)


| Trigger                                                             | Skill                     | Subagent                                         |
| ------------------------------------------------------------------- | ------------------------- | ------------------------------------------------ |
| Prompt has any link (Jira / Confluence / Slack / GDoc / Gmail / GH) | `adk-core:context-gather` | `context-gatherer` (always before primary skill) |
| "set up adk" / "configure datadog" / "missing config"               | `adk-core:setup`          | (no subagent)                                    |
| "what does adk know?" / "show config"                               | `adk-core:info`           | (no subagent)                                    |
| "what would you do here?" / outer-skill mid-pivot                   | `adk-core:prompt-expand`  | `prompt-expander`                                |


## Composite chains (multiple skills)


| Trigger                                | Chain                                                                                  |
| -------------------------------------- | -------------------------------------------------------------------------------------- |
| "investigate X bug and fix it"         | `investigate-incident` → `code-bugfix` → `review-code-changes`                         |
| "ship the X experiment"                | `investigate-experiment` → (if green) `code-write` (gate flip) → `review-code-changes` |
| "review and fix the PR"                | `review-pr --fix` (single skill, two phases)                                           |
| "draft a runbook for X and publish it" | `docs-write` → `docs-publish-confluence`                                               |
| "fix CI on this PR"                    | `investigate-deploy` → `code-bugfix` → `review-code-changes`                           |
| "full RCA for the X outage"            | `investigate-rca` (composite skill, calls others internally)                           |


## Selection rules when multiple match

1. Prefer the most specific skill (e.g. `code-bugfix` over `code-write` when "bug" is in the prompt).
2. Prefer non-destructive over destructive when ambiguous (`investigate-datadog` before `code-bugfix`).
3. If the prompt names a URL or PR number, that drives the primary skill (`review-pr` for a GH PR URL alone).
4. If the prompt has both a "what" and a "why" (investigate AND fix), chain them.
5. Confidence threshold: if no skill scores ≥0.7, ask one clarifying question.