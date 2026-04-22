# `auto` workflow — detailed steps

## Phase A — expand + classify

1. **Restate** the prompt in your own words. One sentence.
2. **Classify** into domains. Output a comma-separated list (`build`, `frontend`, `review`, `publish`, ...).
3. **Slug** the task. Kebab-case. Date-prefix only if disambiguation needed (`2026-04-22-csv-export`).
4. **Create** `.temp/task-<slug>/` if not present. Write a one-line `prompt.md` containing the verbatim user prompt.
5. **Detect links**. Regex match for: `*.atlassian.net`, `*.confluence.com`, `docs.google.com/document/`, `slack.com/archives/`, `mail.google.com/`, `github.com/.../{pull,issues}/`. If any match, queue `@adk:context-gather`.
6. **Approval gate** (unless `--auto`): show classification, slug, links queued, ask "proceed?".

## Phase B — requirements + scoping

1. Spawn `agents/brainstorm-facilitator.md` (via `Task` tool) loaded with `@adk:requirements` + `@adk:scoping`. Pass:
   - The prompt.
   - `.temp/task-<slug>/context.md` if context-gather ran.
2. The subagent runs the requirements skill first (iterative Q&A) → emits `requirements.md`.
3. Then runs scoping → emits `scope.md`.
4. Returns control. Show `requirements.md` + `scope.md` summary. Approval gate.
5. If user requests changes, re-spawn the subagent with the revisions.

## Phase C — dispatch

1. Read `scope.md`. Identify the work slices.
2. For each slice, decide the skill set per `references/dispatch-matrix.md`.
3. **UI special-case:** if frontend touched, dispatch `@adk:frontend-design` first **in plan mode**. It will spawn `@adk:frontend-mockup` to emit `preview/sample-1.html` ... `preview/sample-5.html`. Show all 5 to the user. User picks one (or asks for 5 more variants). Locked sample becomes the design baseline.
4. Spawn parallel subagents via `Task` tool. Each gets:
   - The slice's skill name and inputs.
   - The path to `.temp/task-<slug>/`.
   - The skill's output expectation.
5. Wait for all subagents to complete. Each returns its own report.

## Phase D1 — local validation

1. Spawn `agents/code-reviewer.md` loaded with `@adk:review-local` to do an aggregate self-review across all changes.
2. Each per-skill validator must already have run inside its own subagent's Phase 4 gate.
3. If any Blocker / Critical finding → loop back to Phase C with the fix request.

## Phase D2 — browser validation

1. Detect UI work: changes to `*.tsx`, `*.css`, `*.html`, or presence of `.temp/task-<slug>/preview/*.html`.
2. If detected, run `@adk:validate-browser` with the modes appropriate to the slice:
   - Bug fix → `verify-fix`.
   - New UI → `visual-check` + `console-audit` + `a11y-audit`.
   - Interaction-heavy → also `interaction-test`.
3. Outputs go to `.temp/task-<slug>/browser-validation/<mode>/`.
4. On any failure → loop back to Phase C.

## Phase D3 — publish + CI

1. Spawn `@adk:publish-commit` to draft the commit message.
2. Spawn `@adk:publish-github` to push and open/update the PR via `gh` CLI.
3. Spawn `@adk:cicd-monitor` to watch checks. It uses `gh pr checks --watch`.
4. On CI red → spawn `@adk:cicd-fix`. Apply fix. Loop back to D1 (or D2 if UI).
5. On CI green → write final report to `.temp/task-<slug>/report.md`. End.
