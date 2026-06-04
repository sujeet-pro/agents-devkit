# implement — workflow

Five phases. The default flow stops at the Phase 1 → Phase 2 boundary and waits for a go-ahead. `--plan` stops after Phase 1; `--act` skips the confirm gate. The phased process is the contract; the **Workflow tool** drives the heavy execution + self-review.

## Phase 0 — gather

- Classify the input per `dispatch.md` and fetch the requirement (Jira via Atlassian MCP, GitHub issue via `gh issue view`, Confluence/Slack via MCP, freeform = the prose). For a mixed bag of links, fan out the `context-gatherer` agent.
- Read the repo's conventions: build/test tooling (`package.json`, `pyproject.toml`, `go.mod`, `Makefile`), lint config, `CLAUDE.md`/`AGENTS.md`, and recent commits for commit + code style.
- **Challenge** if a quick `grep` suggests the feature already exists: "Found X that may already cover this — update it or build new?"

## Phase 1 — advise + plan

- In `-i` mode, ask up to 3 high-value questions: **scope** (vertical-slice / full / spike), **constraints** (deadline, blocker, reviewer, can't-touch-X), **test strategy** when not derivable. In default mode, pick the recommended default for each and **state the assumptions** so the user can correct.
- Present **2–4 approaches** with one-line trade-offs each; mark one recommended. Example: vertical-slice (ship happy path now) / full (happy + edge cases + tests) / spike (draft, no tests, early eyes).
- Write the plan: goal, in/out scope, chosen approach + rationale, file-level change list, risks + mitigations, validators to run, rollback. **Stop and confirm** before editing (unless `--act`).

## Phase 2 — execute (the Workflow)

For a multi-file or non-trivial change, drive a **Workflow**:

1. Spawn the `implementer` agent to write the smallest correct change, reading every file before editing it and matching repo idiom.
2. Spawn the `test-engineer` agent (in parallel where independent) to add behavior-named tests: happy path + ≥1 boundary + ≥1 error per behavior.
3. Once code + tests land, spawn `code-reviewer` (and `security-auditor` if the diff touches auth / input / crypto / deps) to **self-review the diff** before you report — adversarially verify any finding before acting on it.

A one-file, single-concern edit may skip the Workflow — edit inline with the Edit tool, then still run the validators. Say you skipped it.

Edit discipline: minimal, anchored edits (change the block you mean to change, not the whole file). Read before every write. No drive-by cleanup.

## Phase 3 — validate

- Run the repo's own gates on the changed surface: typecheck, lint, and the narrowest relevant tests. Not a full-suite run unless the change is broad.
- A failing gate **stops the phase** — fix the cause or report; never `--no-verify`, never paper over it.
- Self-coherence: what shipped matches the plan; explain any deviation.

## Phase 4 — report

- Risk-first summary: blockers / follow-ups first, then what got done (with `file:line`), files touched, files intentionally not touched, what was skipped + why.
- Suggest next steps: a PR (`gh pr create` on the feature branch), a PR description (`/adk:document --type pr-body`), or a review (`/adk:review .`).
- **Pushing / opening a PR is gated** (`rules.md`): confirm before any `git push` or `gh pr create`.

## Narrate

State each phase boundary, every auto-defaulted assumption, the approach chosen, each Workflow fan-out, and every validator result. Confirm before any shared-state write. Never go silent for more than a phase.
