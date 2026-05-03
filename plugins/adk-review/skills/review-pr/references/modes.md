# `review-pr` — mode contract

`review-pr` supports `--auto` (default), `-i` / `--interactive`, and `--fix`. The composition matrix:

| Mode combination | Effect |
| --- | --- |
| `--auto` (default) | Fresh full review → reconcile → propose → post (no per-phase gate). Post-confirmation always runs. |
| `-i` / `--interactive` | Same flow, with per-phase approval. Walks each finding before posting. Mutually exclusive with `--auto`. |
| `--fix` | Adds Phase 6c (apply accepted findings + push). Composes with both `--auto` and `-i`. |
| `--auto --fix` | End-to-end: full review + post + apply + push. STILL never auto-merges. STILL asks before the first push of a session. |
| `-i --fix` | Per-phase approval through review + per-fix approval. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision (e.g. "post all validated non-duplicate findings", "post one consolidated review rather than many comments").
- Still validates (line-anchor re-check before post; post-confirmation re-fetch after post).
- Still surfaces the final report (severity counts, posted vs unposted, residual risk, decisions).
- Refuses any irreversible op explicitly marked "never auto":
  - `gh pr merge` — refused.
  - `git push --force` to protected branches — refused.
  - Re-posting a comment after a propagation miss — refused.
  - Resolving a comment without first posting a reply — refused.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates: classify → reconcile → propose → post.
- For each finding, prompts: `accept | edit | discard | discuss-in-person`.
- Allows the user to re-tier a finding inline (e.g. "this is a Nitpick, not Should-Have").
- Post-stage shows the exact comment body before posting.

## `--fix` (orthogonal to `--auto` / `-i`)

- Adds Phase 6c (apply accepted findings locally + push). Without `--fix`, the skill stops after Phase 6a/6b.
- For non-trivial fixes, delegates to `/adk-code:code-bugfix` (passes the finding as the brief).
- Runs the repo's native tests / typecheck / lint after each fix (or once at the end if the diff is small).
- **Push gate:** asks before the first push of the session, even under `--auto --fix`. Subsequent pushes in the same session don't re-ask UNLESS the target branch changed.
- **Never merges.** Even under `--auto --fix`. Surfaces "merge is the author's call".
- **Never force-pushes** to `main` / `master` / `develop` / any branch in `~/.config/adk/github.md.forbid_force_push_branches`.
- **Never deletes branches.** `gh pr close` is also out of scope.

## Ownership-aware mode behavior

The mode behavior changes slightly based on detected ownership (Phase 0):

### When the PR is yours (`ownership=own`)

| Mode | Behavior |
| --- | --- |
| `--auto` | Self-review pass; surfaces findings on your own PR (still posts to the PR comment thread — useful for agents reviewing themselves). Plus drafts replies to existing reviewer comments. |
| `--auto --fix` | Self-review + reply to existing comments + apply suggested changes + push (asks first). |
| `-i` | Walk every finding + every reply draft before posting. |

### When the PR is a peer's (`ownership=peer`)

| Mode | Behavior |
| --- | --- |
| `--auto` | Standard review: post severity-tiered findings as inline comments. Default behavior. |
| `--auto --fix` | Less common: applies findings directly to the peer's branch. Requires push permission on the head branch (preflight checks). Reply per addressed comment. **Asks before the first push.** |
| `-i` | Walk every finding before posting. |

## What `--fix` will NOT do, ever

1. `gh pr merge` (any flag).
2. `git push --force` to a protected branch.
3. `git push --force-with-lease` without confirmation.
4. `gh pr close`.
5. `git branch -D` of the head branch.
6. `gh pr ready` (changing draft → ready) — that's an authorial choice.
7. Approve the PR (`gh pr review --approve`) — the `code-reviewer` agent has this disallowed at the agent level.

## Subset flags

- `--scope <path>` — restrict review (and `--fix`) to a sub-path of the diff. Useful when the diff is huge and only one subsystem matters.
- `--dimensions <comma-list>` — run only the named dimension passes (e.g. `--dimensions security,perf`). Default: all six.
- `--no-post` — run the full review pipeline but stop before Phase 6 (writes findings only). Useful for `gh pr diff | review-pr --no-post`-style flows.
