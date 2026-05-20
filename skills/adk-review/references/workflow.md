# adk-review — workflow

Five phases. Read-only by default; `--fix` extends with apply + push.

## Phase 0 — context-gather

- Fetch the target (PR via `gh`/MCP; local diff via `git diff base...HEAD`; doc via filesystem or MCP).
- Pull repo conventions: `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, recent commits for style, `package.json`/`pyproject.toml` for tooling.
- Build `.temp/adk/review/<task>/context.md`.

## Phase 1 — advise

- Up to 3 questions: severity bar, dimensions to run, post policy (if PR is someone else's).
- **Challenge fires** if PR already has ≥2 approvals: "fresh pass or last-commit-only?"
- Recommend plan + dimensions.

## Phase 2 — execute (one dimension pass at a time)

**Order:** correctness → tests → security → performance → readability → consistency.

- Per finding: severity, dimension, `path:line`, ≤15-word verbatim quote, fix.
- Each pass writes `.temp/adk/review/<task>/findings/<dimension>.md`.

## Phase 3 — validate

- Cross-check that quotes match the actual file content (regen if drifted).
- Check no finding is a duplicate of an existing PR comment (review-pr only).
- Constitution check on `--fix` flow (no force, no merge, no protected push).

## Phase 4 — report + post-or-apply

- **Default**: report findings; don't post.
- **`--auto`** on someone else's PR: post validated non-duplicate findings (one confirm per batch).
- **`--fix`**: apply accepted findings locally; validate; push to PR HEAD branch after confirm.

## Personas loaded

- `shared/personas/code-reviewer.md` — primary.
- `shared/personas/security-reviewer.md` — when diff touches auth / input / crypto / deps.
- `shared/personas/test-engineer.md` — for the tests dimension pass.

## Mode awareness (`--plan` / `--act`)

- `--plan`: stops after Phase 2 (findings emitted; nothing posted, nothing fixed).
- `--act`: requires a prior `--plan` run; applies accepted findings.
- (no flag): all five phases, confirm gate before posting / fixing.

See `shared/plan-act-mode.md`.
