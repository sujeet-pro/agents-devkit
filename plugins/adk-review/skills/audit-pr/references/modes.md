# `audit-pr` — mode contract

`audit-pr` supports `--auto` (default), `-i` / `--interactive`, and `--fix`. The composition matrix:

| Mode | Effect |
| --- | --- |
| `--auto` (default) | Run all 10 checks in parallel; emit verdict; STOP. |
| `-i` / `--interactive` | Same flow with per-check approval for `Warn`/`Fail` items. |
| `--fix` | Adds Phase 5b (auto-fix safely-fixable subset only). Composes with `--auto` and `-i`. |
| `--auto --fix` | End-to-end: checks + auto-fix safely-fixable. Stops before push (push gate asks). |
| `-i --fix` | Per-check + per-fix approval. |
| `--post-comment` | Adds Phase 5c (post audit summary as PR comment with post-confirmation). Off by default. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode)

- Skips per-phase approval gates.
- Runs all 10 checks (or the `--checks` subset).
- Parallelizes independent checks (max 4 at once).
- Emits the verdict + per-check details.
- Does NOT post to PR (use `--post-comment` for that).
- Does NOT fix (use `--fix` for that).

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates: especially walks each `Warn` and `Fail`, asking the user how to proceed.
- For `Warn`: asks "downgrade to Pass for this run? Open follow-up? Suggest fix?".
- For `Fail`: asks "block on this? Override (allowed for non-critical fails)? Suggest fix?".

## `--fix` (orthogonal)

- Adds Phase 5b (auto-fix). Without `--fix`: just report.
- Auto-fixes ONLY the safely-fixable subset:
  - lint-clean → run lint tool's auto-fix mode.
  - license-headers → prepend the repo-required header.
  - docs-toc → regenerate the TOC.
- Does NOT auto-fix:
  - tests-added (writing tests is `/adk-code:code-test`'s job).
  - secrets-in-diff (NEVER auto-fix — surface for the user to rotate).
  - perf-regression (investigation, not a fix).
  - bundle-size (manual investigation needed).
  - dep-licenses (replacing a dep is a `/adk-code:code-migrate` task).
  - typecheck-clean (semantic fix; could break things if auto-applied).
  - a11y-regression (often requires UX judgment).
  - doc-updated (writing docs is `/adk-docs:docs-write`'s job).
- After applying fixes, re-runs the affected check to confirm Pass.
- If `--fix` should also push:
  - PUSH-GATE: asks before the first push of the session, even under `--auto --fix`.
  - Push to PR head branch. NEVER `--force`. NEVER to protected branches.

## `--post-comment` (orthogonal; off by default)

- Adds Phase 5c (post audit summary as a top-level PR comment).
- The comment uses a fixed template (see `references/output-format.md`).
- Post-confirmation per `/adk-review:review-pr` `references/post-confirmation.md`.
- Useful for automation contexts where the audit signal should appear in the PR thread (e.g. CI invokes audit-pr after a push).

## What `--fix` will NOT do, ever

1. `gh pr merge` (any flag).
2. `git push --force` to protected branches.
3. `gh pr close`.
4. Auto-fix `tests-added`, `secrets-in-diff`, `perf-regression`, `bundle-size`, `dep-licenses`, `typecheck-clean`, `a11y-regression`, `doc-updated`.
5. Push without asking, even under `--auto --fix`.
6. Modify `~/.config/adk/*.md`.
7. Override an existing license header (only prepends to files without one).
8. Edit code outside the changed files in the diff (limit fixes to PR-touched files).

## Subset flags

- `--checks <comma-list>` — restrict to a subset by name (e.g. `--checks lint,typecheck,secrets`).
- `--no-conditional` — skip conditional checks (a11y, perf, bundle-size) regardless of relevance detection.
- `--post-comment` — opt into Phase 5c (PR comment).
- `--no-cache` — re-run lint / typecheck even if the prior run is recent (default: cache for 5 minutes within a session).
- `--fail-fast` — stop on the first `Fail` (default: run all checks even after a fail; complete picture).

## Default vs override

| Decision | Default | Override |
| --- | --- | --- |
| Checks subset | all 10 (filtered to relevant) | `--checks <list>` |
| Conditional checks | run if relevant; skip otherwise | `--no-conditional` (skip even if relevant) |
| Comment posting | NO | `--post-comment` (still uses post-confirmation) |
| Auto-fix scope | safely-fixable subset only | (not user-overrideable; safety) |
| Push after fix | asks at gate | (not overrideable; gate always asks) |
| Verdict on N/A | doesn't change overall verdict (just surfaces install command) | (not overrideable) |
| Fail-fast | NO | `--fail-fast` |
