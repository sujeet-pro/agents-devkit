---
title: 'auto'
description: 'Prompt-routing dispatcher.'
artifact_kind: skill
skill_name: auto
category: standalone
---
# auto

Prompt-routing dispatcher. Use this first for any non-trivial request when you (or the user) are not certain which adk skill to invoke. It expands the prompt, classifies the domain, runs requirements + scoping with the user (via the brainstorm-facilitator subagent), then dispatches per-task subagents loaded with the right downstream skills (build, test, docs, review, browser-validate, publish, cicd-monitor) in parallel. Use whenever the user issues a multi-step request such as "build me X", "fix this bug end-to-end", "ship a feature", "investigate this incident". Do not use when the user has already named a specific skill (just invoke that skill).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-auto` form via `agents-skills/`.

```text
/adk:auto            # interactive run (Claude Code)
/adk:auto --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-auto` (resolved through the
`agents-skills/adk-auto/` symlink).

## Source

Direct from `skills/auto/SKILL.md` — this page is auto-generated.

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


## Related skills

- [`audit`](./skill-audit.md) — `@adk:audit` (a.k.a. `adk-audit`)
- [`audit-repo`](./skill-audit-repo.md) — `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- [`build`](./skill-build.md) — `@adk:build` (a.k.a. `adk-build`)
- [`build-bugfix`](./skill-build-bugfix.md) — `@adk:build-bugfix` (a.k.a. `adk-build-bugfix`)
- [`build-feature`](./skill-build-feature.md) — `@adk:build-feature` (a.k.a. `adk-build-feature`)
- [`build-migrate`](./skill-build-migrate.md) — `@adk:build-migrate` (a.k.a. `adk-build-migrate`)
- [`build-refactor`](./skill-build-refactor.md) — `@adk:build-refactor` (a.k.a. `adk-build-refactor`)
- [`build-test`](./skill-build-test.md) — `@adk:build-test` (a.k.a. `adk-build-test`)
- [`cicd-fix`](./skill-cicd-fix.md) — `@adk:cicd-fix` (a.k.a. `adk-cicd-fix`)
- [`cicd-monitor`](./skill-cicd-monitor.md) — `@adk:cicd-monitor` (a.k.a. `adk-cicd-monitor`)
- [`context-gather`](./skill-context-gather.md) — `@adk:context-gather` (a.k.a. `adk-context-gather`)
- [`docs`](./skill-docs.md) — `@adk:docs` (a.k.a. `adk-docs`)
- [`docs-write`](./skill-docs-write.md) — `@adk:docs-write` (a.k.a. `adk-docs-write`)
- [`frontend`](./skill-frontend.md) — `@adk:frontend` (a.k.a. `adk-frontend`)
- [`frontend-design`](./skill-frontend-design.md) — `@adk:frontend-design` (a.k.a. `adk-frontend-design`)
- [`frontend-mockup`](./skill-frontend-mockup.md) — `@adk:frontend-mockup` (a.k.a. `adk-frontend-mockup`)
- [`plan`](./skill-plan.md) — `@adk:plan` (a.k.a. `adk-plan`)
- [`publish`](./skill-publish.md) — `@adk:publish` (a.k.a. `adk-publish`)
- [`publish-commit`](./skill-publish-commit.md) — `@adk:publish-commit` (a.k.a. `adk-publish-commit`)
- [`publish-github`](./skill-publish-github.md) — `@adk:publish-github` (a.k.a. `adk-publish-github`)
- [`requirements`](./skill-requirements.md) — `@adk:requirements` (a.k.a. `adk-requirements`)
- [`review`](./skill-review.md) — `@adk:review` (a.k.a. `adk-review`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
- [`scoping`](./skill-scoping.md) — `@adk:scoping` (a.k.a. `adk-scoping`)
- [`temp-folder`](./skill-temp-folder.md) — `@adk:temp-folder` (a.k.a. `adk-temp-folder`)
- [`validate-browser`](./skill-validate-browser.md) — `@adk:validate-browser` (a.k.a. `adk-validate-browser`)
