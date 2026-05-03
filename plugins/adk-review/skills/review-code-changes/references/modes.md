# `review-code-changes` — mode contract

`review-code-changes` supports `--auto` (default), `-i` / `--interactive`, and `--fix`. The composition matrix:

| Mode | Effect |
| --- | --- |
| `--auto` (default) | Detect baseline → gather scope → review → report findings (no per-phase gate). |
| `-i` / `--interactive` | Same flow with per-phase approval. Walks each finding before adding to the report. Mutually exclusive with `--auto`. |
| `--fix` | Adds Phase 5b (apply accepted findings to the working tree, validate). Composes with both `--auto` and `-i`. **Never pushes.** |
| `--auto --fix` | End-to-end: review + apply + validate. Stops before push. |
| `-i --fix` | Per-phase approval through review + per-fix approval. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode)

- Skips per-phase approval gates.
- Picks the documented baseline (tracking → origin/branch → main → master → first-parent).
- Picks "all dimensions" by default (override with `--dimensions`).
- Includes all four scope sources (branch + staged + unstaged + untracked).
- Surfaces findings in `report.md` + per-source breakdown.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates: baseline picked → scope confirmed → propose findings.
- For each finding, prompts `accept | edit | discard`.
- Allows the user to re-tier inline.
- For `--fix`: per-fix approval before applying.

## `--fix` (orthogonal to `--auto` / `-i`)

- Adds Phase 5b (apply accepted findings + validate).
- For trivial fixes, edits inline. For non-trivial fixes, delegates to `/adk-code:code-bugfix`.
- Runs the repo's native tests / typecheck / lint after each fix (or once at the end if the scope is small).
- **Does NOT push.** That's intentional — pushing is a separate explicit
  `git push` / `gh` step, and the user often wants to eyeball the diff before
  pushing.
- **Does NOT open a PR.** That's `/adk-docs:docs-pr-description` then `gh pr create` (separate, gated).
- **Does NOT comment-post anywhere.** No remote calls at all.

## What `--fix` will NOT do, ever

1. `git push` (any flag, any branch).
2. `gh pr create` / `gh pr edit` / `gh pr merge` / `gh pr comment`.
3. `git commit` automatically — it leaves the working tree dirty for the user to commit. (Exception: under `-i --fix`, asks per-fix whether to commit; otherwise leaves uncommitted.)
4. Modify `.git/config` or any other repo metadata.
5. Touch `~/.config/adk/*.md`.
6. Touch any file outside the repo root.

## Subset flags

- `--scope <path>` — restrict review (and `--fix`) to a sub-path of the repo. Useful when the working tree has many unrelated dirty files (e.g. WIP across multiple subsystems).
- `--dimensions <comma-list>` — run only the named dimension passes. Default: all six.
- `--no-untracked` — exclude untracked files from scope. Default: include.
- `--include-deleted` — include files deleted from the working tree (i.e. removed but not committed) for sanity-checking the deletion. Default: exclude (rare to want).

## Default vs override

| Decision | Default | Override |
| --- | --- | --- |
| Baseline | `@{upstream}` → `origin/<branch>` → `main` → `master` → first-parent | `<base-branch>` arg |
| Dimensions | all six | `--dimensions <list>` |
| Scope sources | all four (branch + staged + unstaged + untracked) | `--scope <path>` (path filter), `--no-untracked` (exclude untracked) |
| Validation command (`--fix`) | `repos[<name>].notes`, else common defaults | (not user-overrideable; edit `repos.md`) |
| Commit-after-fix | no (working tree stays dirty) | (not user-overrideable; user commits manually after) |
| Push-after-fix | NEVER | (not overrideable; use `git push` separately) |

## Why `--fix` doesn't push

Three reasons:

1. **Eyeball before push.** The user often wants to see the actual diff with `git diff` (and maybe a tool like `lazygit` or `tig`) before pushing. Auto-pushing removes that step.
2. **Composition with other skills.** Common chain: `code-bugfix` → `review-code-changes --fix` → `docs-commit-message` → manual `git commit && git push`. Auto-push would step on the `docs-commit-message` skill.
3. **The push gate is explicit user approval.** A push needs its own preflight
   (no stale upstream, branch protection, force-push refusal on protected).
   Bypassing it via `review-code-changes --fix --push` would hide that shared-state action.

If the user really wants "review + push", they chain explicitly:

```
/adk-review:review-code-changes --auto --fix && git commit -am "..." && git push
```

Or use `/adk-core:auto` which composes the right chain end-to-end (and stops at the push-gate).
