---
name: pr-finalize
description: Use when implementation is complete and you need to verify, run a final review, and choose how to integrate the branch (merge, squash, or rebase)
user_invocable: true
arguments:
  - name: base
    description: "Base branch to compare against (default: main)"
    required: false
  - name: strategy
    description: "Integration strategy: merge, squash, rebase, or ask (default: ask)"
    required: false
  - name: pr
    description: "Existing PR number or URL to update instead of creating a new one"
    required: false
  - name: publish
    description: "Where to send the PR: source, markdown, both (default: source)"
    required: false
---

# Finishing a Development Branch

Use `skills/_references/agentic-teams.md`, `skills/_references/preflight-validations.md`, `skills/_references/source-routing.md`, and `skills/_references/output-formats.md`.

## Preflight

Before verification or review, run:

`zsh scripts/check-skill-deps.zsh pr-finalize pr=<pr> publish=<publish>`

Then confirm:

- The current branch is not `main` or `master`.
- The working tree is clean (no uncommitted changes). If dirty, stop and ask the user to commit or stash first.
- The branch has at least one commit ahead of `base`.

## Phase 1: Fresh Verification

Run verification in parallel when child agents are available:

### Test Pass

- Detect the project's test runner from `package.json`, `Makefile`, `Cargo.toml`, `pyproject.toml`, `go.mod`, or similar.
- Run the full test suite. Report pass/fail counts.

### Build and Static Analysis Pass

- Run the linter if configured.
- Run the type-checker if configured.
- Run the build command if configured.
- Report each as clean or list failures.

### Behavioral Spot-Check

- Identify the specific behavior or output changed by the branch (from the diff against `base`).
- Run a targeted verification of that behavior (e.g., specific test files, a curl against a local server, a CLI invocation).

If any verification step fails, stop and present the failures. Do not proceed to review or integration until all checks pass. Ask the user whether to fix the issues or continue anyway.

## Phase 2: Final Review

Run review child agents in parallel:

- `code-reviewer` for correctness, security, performance, and code patterns across the full branch diff
- `repo-auditor` for architecture, dependency direction, and change isolation
- `doc-reviewer` for docs impact, naming, migration notes, and reviewer ergonomics

Load coding guidelines following the same model as `/devkit:review-code-local`:

- Always load `skills/_references/guidelines/coding/general.md` and `skills/_references/guidelines/coding/architecture.md`
- Add repo-type guidance based on the files changed (frontend, backend, design-system, scripts, etc.)
- Load `skills/_references/guidelines/coding/security.md` if security-sensitive files are touched
- Load `skills/_references/guidelines/coding/testing.md` if test files are touched

Consolidate findings: deduplicate across agents, assign severity and confidence, and filter below 80% confidence.

### Review Gate

Present the consolidated findings to the user:

```text
## Final Review

### Findings
| Severity | File | Issue | Confidence |
|----------|------|-------|------------|
| ...      | ...  | ...   | ...        |

### Blockers: N critical/high findings
### Warnings: N medium/low findings
```

If there are critical or high-severity findings:

- Present them individually and ask whether to fix before integrating or proceed anyway.
- If the user chooses to fix, apply changes and re-run verification (Phase 1) on affected files only.

If there are no blockers, proceed to Phase 3.

## Phase 3: Branch Status Summary

Present a full branch status before offering integration options:

```text
## Branch Status

Branch: <current branch>
Base: <base branch>
Commits ahead: N
Files changed: N

### Verification
- Tests: <pass count>/<total count> passed
- Lint: <clean or N issues>
- Types: <clean or N issues>
- Build: <success or failure>

### Review
- Critical: N
- High: N
- Medium: N
- Low: N
- All blockers resolved: yes/no

### Risk Assessment
- <1-3 bullet points summarizing key risks, breaking changes, or deployment considerations>
```

## Phase 4: Integration

### Strategy Selection

If `strategy=ask` (the default), present the options with a recommendation:

```text
## Integration Options

1. **Squash merge** — combine all N commits into one clean commit on base
   Best when: the branch has messy WIP commits or the feature is a single logical change

2. **Merge commit** — preserve full branch history with a merge commit
   Best when: the branch has well-structured commits that tell a useful story

3. **Rebase** — replay commits on top of base without a merge commit
   Best when: the branch has clean, atomic commits and you want linear history

Recommended: <recommendation based on commit count, message quality, and branch complexity>
```

If `strategy` is explicitly set to `merge`, `squash`, or `rebase`, skip the selection prompt.

### PR Creation or Update

Detect GitHub or Bitbucket from the repository remote using source routing.

**If `pr` is provided**: update the existing PR description using the branch status and review summary.

**If no `pr` is provided**: ask the user whether to:

1. **Create a PR** — generate a PR description from the diff, commits, and review findings, then create it through the matching MCP.
2. **Merge locally** — perform the selected merge strategy locally without creating a PR.

When creating or updating a PR, base the description on the real diff, commits, and review findings. Include:

- What changed and why
- Verification results
- Risk and rollback notes
- Test and docs impact
- Follow-up items if any

Post through the GitHub or Bitbucket MCP when `publish` includes source updates.

### Local Merge (when chosen)

If the user chooses local merge instead of a PR:

1. Confirm the strategy one more time.
2. Execute the merge:
   - `squash`: `git checkout <base> && git merge --squash <branch> && git commit`
   - `merge`: `git checkout <base> && git merge --no-ff <branch>`
   - `rebase`: `git rebase <base>` (on the feature branch, then fast-forward base)
3. Do not push unless the user explicitly asks.
4. Do not delete the feature branch unless the user explicitly asks.

## Output

Display a final summary:

```text
## Finalize Complete

Branch: <branch>
Base: <base>
Strategy: <merge | squash | rebase | PR created>
PR: <PR URL if created or updated, otherwise "local merge">

### Verification
- Tests: passed
- Lint: clean
- Types: clean
- Build: success

### Review
- Findings: N total (N resolved, N accepted as-is)
- Blockers: none

### Next Steps
- <push, deploy, delete branch, or other follow-up actions>
```

## Adjacent Skills

- `/devkit:dev-implement` for the full implementation flow that hands off to this skill
- `/devkit:dev-verify` for standalone verification without the review and integration steps
- `/devkit:review-code-local` for a standalone local review without integration
- `/devkit:pr-describe` for generating or updating a PR description without verification or review
