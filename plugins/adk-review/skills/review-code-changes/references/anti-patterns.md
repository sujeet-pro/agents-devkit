# `review-code-changes` — anti-patterns

## Scope

- **Reviewing only the staged changes.** The working tree often has more (unstaged + untracked). Default scope includes all four sources.
- **Skipping untracked files.** New files are usually the bulk of new work and the most likely to lack tests / docs. They MUST be in scope.
- **Including deleted files by default.** Deletions are usually intentional; reviewing them as "missing code" creates noise. Use `--include-deleted` if explicitly wanted.
- **Reviewing the latest commit only.** That misses everything between the baseline and the previous commit. The baseline-vs-HEAD diff is the right scope (plus the live working-tree state).
- **Wrong baseline pick.** If `@{upstream}` is set to a stale branch (e.g. `origin/old-feature`), the diff is wrong. Surface the baseline + source in the status banner so the user catches it.
- **`--scope <path>` that's wider than the actual change.** Use the narrowest path that still covers all changed files in scope; widening adds noise.

## Severity / quality

- **Self-leniency.** "It's just my code; the reviewer will catch the rest." No — the reviewer is a peer; they'll be just as strict as you should be now.
- **Self-flagellation.** Tier the same finding the same way you'd tier a peer's. Don't over-Blocker your own work.
- **Untiered findings.** Same rule as `review-pr`: tier or drop.
- **Bikeshedding style when lint is silent.** Same rule as `review-pr`. Run the cheap lint pre-pass in Phase 1; don't re-raise issues lint will catch.
- **Re-explaining the change.** You wrote it. Lead with what's wrong, not what changed.

## Process

- **Working tree changed mid-review.** If you edit files between Phase 2 and Phase 3, the review is reading stale content. The skill detects via mtime and surfaces; re-run for accuracy.
- **Reviewing on top of an unstable base.** If `git pull` is overdue and the baseline branch has moved, the diff is misleading. Surface in Phase 1 and recommend a `git fetch` before continuing.
- **Mixing review with new work.** Don't keep editing the working tree while the review is running. Save → review → fix → push.
- **Skipping the cheap lint pre-pass.** It's free signal that the lint config will catch most style nits; saves the style dimension from drowning in lint-already-catches-this findings.

## `--fix`-specific

- **Pushing under `--fix`.** Never. Pushing is a separate gated step. The
  skill stops after applying + validating; the user pushes manually after
  explicit approval.
- **Committing under `--fix`.** Don't auto-commit; leave the working tree dirty so the user can see the applied changes with `git diff` before committing.
- **Bundling 5 unrelated fixes into one application.** Even though the skill doesn't auto-commit, the user often `git commit` after — splitting the fix queue by topic helps them author atomic commits.
- **Applying a fix that breaks tests, then continuing.** Stop applying further fixes from the queue. Surface the failure. Don't try to "fix the fix" — that's `/adk-code:code-bugfix`.
- **Modifying `.gitignore` / `.gitattributes` as a "fix".** Those are configuration changes, not findings. Surface as `Question` instead.
- **Touching `package-lock.json` / `go.sum` / `Cargo.lock` as part of a fix.** Lockfile churn from dep changes is OK; lockfile churn unrelated to the fix is noise. Surface the dep-related portion as `Question`.

## Reporting

- **No per-source breakdown in `findings.md`.** The user wants to know "is the unstaged work safe to commit?" — annotate every finding with its scope source.
- **Skipping the next-step suggestion.** Always end with: 0 Blockers/Criticals → "ready to push"; otherwise → "fix before push".
- **Saying "validated" without a path to evidence.** Every claim links to a file in the working tree (or a test command output captured under `validation/`).

## MCP / tooling

- **Calling any remote API.** No `gh`, no MCP, no anything. The skill is local-only.
- **Reading another repo.** The skill is single-repo. If the user's working tree spans two repos (rare), they pick one to review at a time.
- **Modifying meta-info files.** Never. The skill reads `~/.config/adk/review.md`; never writes.
