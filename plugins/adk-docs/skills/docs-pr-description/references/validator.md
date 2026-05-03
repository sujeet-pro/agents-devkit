# `docs-pr-description` — per-phase validator

Logged to `.temp/task-<slug>/validation/docs-pr-description.md`.

## Phase 0

- [ ] `.temp/task-<slug>/` exists, gitignored.
- [ ] Prompt saved verbatim.
- [ ] Current branch detected; PR number (if any) recorded.

## Phase 1

- [ ] `bin/adk-info --check` == 0.
- [ ] Base branch resolved and exists in git.
- [ ] Under `--fix`: `gh auth status` == 0 OR `github` MCP reachable.
- [ ] PR template path checked; template content captured in
      `template.md` when present.

## Phase 2

- [ ] `commits.txt` exists and contains ≥ 1 commit (or a "no commits
      vs base" error with remediation).
- [ ] `diffstat.txt` exists and shows ≥ 1 file changed.
- [ ] `tests.diff` captured (possibly empty; not a gating failure).
- [ ] Ticket references extracted from commit bodies; the list is
      the allow-list for the Linked tickets section.

## Phase 3

- [ ] Changes-by-area table has ≥ 1 row and ≤ 10 rows.
- [ ] Every row cites a folder from `diffstat.txt`.
- [ ] Breaking changes enumerated explicitly (even "none").

## Phase 4

- [ ] `pr-title.txt` exists; length ≤ 70 chars.
- [ ] `pr-body.md` exists.
- [ ] `pr-body.md` has: Summary, Changes by area, Test plan, Risks,
      Linked tickets (even if "None"), Follow-ups (optional).
- [ ] Every ticket in "Linked tickets" appears in `commits.txt`.
- [ ] Test plan section is non-empty.
- [ ] All code fences have a language tag.
- [ ] No env-var / secret-shaped strings embedded (simple regex
      guardrail).
- [ ] Summary bullets: 2-4; first bullet starts with `**Risk:**` or
      `**Risks:**`.

## Phase 5 (under `--fix`)

- [ ] User confirmed the remote write (ask-once gate).
- [ ] Backup of existing PR body in
      `.temp/task-<slug>/backup/pr-body.md`.
- [ ] Current user is the PR author
      (`gh pr view --json author --jq .author.login`).
- [ ] `gh pr edit` returned 0.
- [ ] Re-fetched body matches `pr-body.md` (modulo GitHub's markdown
      normalizer, e.g. trailing whitespace trimming).

## On failure

- Log with remediation.
- Block the next phase.
- After 3 same-kind failures, surface and stop.
