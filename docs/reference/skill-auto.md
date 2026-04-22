---
title: 'auto'
description: '|'
skill_name: auto
category: standalone
---
# auto — prompt-routing dispatcher

Top-level orchestration skill. Reads the prompt, picks the right downstream skills, and runs them via Claude subagents.

## When to use

- The user's prompt is multi-step or end-to-end (e.g. "build feature X", "fix bug Y and ship it", "investigate incident Z").
- The user has not named a specific `adk-*` skill.
- The work spans multiple layers (plan + build + review + publish).

## When NOT to use

- The user explicitly invoked a specific skill (e.g. `/adk:plan-brainstorm` — go to that skill directly).
- The request is a single trivial action ("rename this variable", "what does X do?").

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<prompt>` | yes | The full user request, verbatim |
| `--auto` | optional | Skip approval gates between phases |
| `--scope <path>` | optional | Restrict subagent reads to a path |

## Workflow (4 phases)

### Phase A — prompt expansion + classification

1. Restate the prompt in your own words. Confirm understanding (one-line).
2. Classify into one or more domains: `discovery`, `plan`, `frontend`, `build`, `review`, `docs`, `audit`, `publish`, `observability`, `bootstrap`.
3. Decide the **task slug** (kebab-case, derived from the prompt). Create `.temp/task-<slug>/` per `@adk:temp-folder` (a.k.a. `adk-temp-folder`).
4. Identify any **links** in the prompt (Jira ticket, Confluence page, Google Doc, Slack thread, Gmail, GitHub URL). If present, **always** invoke `@adk:context-gather` (a.k.a. `adk-context-gather`) before Phase B. Output → `.temp/task-<slug>/context.md`.

Approval gate unless `--auto`: present the chosen task slug, classification, and required context-gather sources; ask "proceed?".

### Phase B — requirements + scoping (with the user)

Spawn the `agents/brainstorm-facilitator.md` subagent loaded with `@adk:requirements` (a.k.a. `adk-requirements`) and `@adk:scoping` (a.k.a. `adk-scoping`). The subagent runs an iterative Q&A:

- Captures `requirements.md` (what the user actually wants).
- Captures `scope.md` (in/out, blast radius, success criteria, milestones).
- Surfaces 2-3 directional options per major decision (per the interaction contract).

Loop until the user accepts both artifacts. Approval gate at the end: "lock scope and dispatch?".

### Phase C — dispatch per-task subagents (parallel)

Read `scope.md`. Decide which downstream skills are needed and dispatch each as its own subagent via the `Task` tool. Use `agents/dispatcher.md` to coordinate.

| Subagent | Skill loaded | Trigger |
| --- | --- | --- |
| `agents/implementer.md` | `@adk:build-feature` / `build-bugfix` / `build-refactor` / `build-migrate` | code change required |
| `agents/test-engineer.md` | `@adk:build-test` | new behavior to lock in |
| `agents/doc-writer.md` | `@adk:docs-write` | doc deliverable |
| `agents/code-reviewer.md` | `@adk:review-local` | self-review before push |
| `agents/security-reviewer.md` | `@adk:audit-repo` (security focus) | auth / payments / secrets touched |
| (no subagent) | `@adk:frontend-design` + `@adk:frontend-mockup` | UI work; produces `preview/sample-{1..5}.html` during plan mode |
| (no subagent) | `@adk:validate-browser` | UI changed OR `preview/*.html` produced |
| (no subagent) | `@adk:publish-commit` + `@adk:publish-github` | commit + open/update PR |
| (no subagent) | `@adk:cicd-monitor` then `@adk:cicd-fix` | post-push CI watching |

For UI work, `frontend-design` is run **in plan mode** and emits 5 sample HTML mockups (`preview/sample-{1..5}.html`) that the user picks one of before any implementation. This is a hard contract — never implement UI without showing 5 samples first unless `--auto` and the user explicitly opted into "skip-design".

### Phase D — validation gates

- **D1 — local validation:** Each subagent runs its own per-skill validator (Phase 1-4). `@adk:review-local` runs as the final aggregate self-review.
- **D2 — browser validation:** If any UI was touched OR `.temp/task-<slug>/preview/*.html` exists, run `@adk:validate-browser` (a.k.a. `adk-validate-browser`) with the appropriate mode (`verify-fix` for bug fixes, `visual-check` + `console-audit` + `a11y-audit` for new UI). Findings go to `.temp/task-<slug>/browser-validation/`.
- **D3 — publish + CI:** Spawn `@adk:publish-commit` then `@adk:publish-github`. Then `@adk:cicd-monitor` watches `gh pr checks --watch`. On red, spawn `@adk:cicd-fix`. Loop back to Phase C if a code change is needed.

Loop on any failure. Stop when all gates green AND user confirms (or `--auto` AND no red gates remain).

## Auto-flow diagram

See `references/how-it-works.md`.

## Output

A consolidated report at `.temp/task-<slug>/report.md`:

- What was built.
- Decisions made (with the option each was picked from).
- Validation evidence (local + browser + CI).
- Residual risk / open follow-ups.
- Links to all artifacts in `.temp/task-<slug>/`.

## Mode contract

`auto` only supports `--mode auto` (the default). It IS the auto loop. Sub-skills may be invoked in `--mode review` or `--mode fix` per scope.

## Anti-patterns

See `references/anti-patterns.md`. Headlines:

- Skipping Phase A's task-slug + `.temp/task-<slug>/` setup. Every later artifact lives there.
- Skipping context-gather when links are present. The user expects the agent to actually read the linked Jira / Confluence / Slack content.
- Implementing UI without the 5-sample mockup loop.
- Skipping `validate-browser` after a UI change.
- Auto-merging the PR. Never. Even under `--auto`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Mermaid diagrams for Phase A→D and the dispatch decision tree |
| `references/modes.md` | Mode contract (auto-only) |
| `references/persona.md` | Dispatcher persona and hard rules |
| `references/workflow.md` | Detailed step list expanded from SKILL.md |
| `references/clarifying-questions.md` | The questions Phase A asks the user (default-ask, with rubrics) |
| `references/dispatch-matrix.md` | Full skill ↔ subagent ↔ trigger table |
| `references/output-format.md` | Final report shape |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Four-phase validator gate |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked examples (UI feature, bug fix, incident triage) |
| `references/interaction-contract.md` | Default-ask + `--auto` contract (synced from `bin/canonical/`) |
