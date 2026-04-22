# `auto` — examples

## Example 1: build a UI feature with a Jira link

User: `/adk:auto Build the export-to-CSV button on the data grid. https://acme.atlassian.net/browse/DATA-1234`

Phase A:
- Slug: `csv-export-button`.
- Classification: `frontend`, `build`.
- Links: 1 Jira → queue context-gather.
- Approval gate: confirmed.

Phase A.5 (`context-gather`): pulls Jira ticket title, description, AC, design link, parent epic. Writes `context.md`.

Phase B (`brainstorm-facilitator` + `requirements` + `scoping`):
- Iterates with user. Locks `requirements.md` (CSV must include all visible columns honoring filters; download in browser; max 50k rows; UTF-8 BOM for Excel).
- Locks `scope.md` (touch: `DataGrid.tsx`, `useExport.ts`, `csv.ts`; out: server-side export; success: button works in Chrome/Safari/Firefox at 360/768/1280; milestones: design → impl → tests → browser-validate → PR).

Phase C:
- Dispatch `frontend-design` (plan mode) → `frontend-mockup` emits 5 button samples in `preview/`. User picks `sample-3.html`.
- Spawn `implementer` + `frontend-feature` for the React change.
- Spawn `test-engineer` + `build-test` for unit tests on `csv.ts`.

Phase D1: `code-reviewer` + `review-local`. Two Suggestions, no Blockers.

Phase D2: `validate-browser` runs `visual-check` (3 viewports) + `console-audit` + `a11y-audit`. All green.

Phase D3: `publish-commit` drafts the message. `publish-github` opens PR. `cicd-monitor` watches; CI green in 4 minutes.

Final `report.md` covers Result + 7 Decisions + 4 Skills + Validation evidence + 0 follow-ups.

## Example 2: production bug fix from a Slack thread

User: `/adk:auto Customer dashboard shows 0 for active users since 13:00. https://acme.slack.com/archives/C123/p1745... --auto`

Phase A:
- Slug: `dashboard-active-users-zero`.
- Classification: `observability`, `build`.
- Links: 1 Slack thread → context-gather pulls thread + customer report.

Phase B (under `--auto`):
- Defaults applied. `requirements.md` = "active-users tile renders 0 since 13:00 today; restore correct count". `scope.md` = surgical, prod hotfix path.

Phase C:
- `observability-incident` runs Datadog query for the metric → finds a deploy at 12:58 changed the user-count query to filter by `is_active=true` but the column was renamed to `active_at` last week.
- `implementer` + `build-bugfix` updates the query.
- `test-engineer` + `build-test` adds a regression test.

Phase D1, D2 (no UI), D3: green. PR open. CI green. Report includes the Datadog dashboard link as residual evidence.

## Example 3: doc-only task

User: `/adk:auto Write a runbook for the auth-token rotation procedure`

Phase A: classification = `docs`. No links. Skip context-gather.

Phase B: `requirements` (audience: on-call SREs; format: numbered procedure; preconditions; rollback). `scope` (touch: `docs/runbooks/auth-token-rotation.md`; out: code change).

Phase C: `doc-writer` + `docs-write`. Done.

Phase D1: `review-local` confirms doc-only diff. Phase D2 skipped (no UI). Phase D3: `publish-commit` + `publish-github`. Done.
