# `review-feedback` — mode contract

`review-feedback` supports `--auto` (default), `-i` / `--interactive`, and `--fix`. The composition matrix:

| Mode | Effect |
| --- | --- |
| `--auto` (default) | Fetch → classify → draft replies → STOP. Doesn't apply or post. Useful for "what would you do?" |
| `--auto --fix` | Full end-to-end: classify → apply → push (asks first) → reply (with confirmation) → resolve. The intended default for "address the PR feedback". |
| `-i` | Per-phase approval. Walks each comment classification + each reply draft. |
| `-i --fix` | Per-phase + per-fix + per-push gating. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode, NO `--fix`)

- Skips per-phase approval gates.
- Classifies all open comments.
- Drafts replies.
- **Does NOT apply, push, or post.**
- Outputs `classification.md` + `replies-draft.md` + `report.md`.
- Useful as a triage tool — see what would be done before doing it.

## `--auto --fix` (the recommended default for this skill)

- Classifies all open comments.
- Drafts replies.
- Applies all `apply-*` classifications (delegating non-trivial to `/adk-code:code-bugfix`).
- Validates after each fix (or once at end if scope is small).
- Asks at the push-gate (always — even under `--auto --fix`).
- Pushes (NEVER `--force`; NEVER to protected branches).
- Posts each reply with post-confirmation (5/10/20s retry budget).
- Resolves `apply-*` threads after reply confirms.
- Leaves `discuss-not-fix` / `wont-fix` / `already-resolved` threads OPEN.

## `-i` (interactive)

- Mutually exclusive with `--auto`.
- Per-phase approval gates: classification → reply drafts → (apply / push / post).
- For each comment: shows the classification + reasoning, asks "accept / re-classify / skip".
- For each reply draft: shows the draft, asks "accept / edit / skip".
- For `--fix`: per-fix approval before applying; per-push approval before pushing.

## `--fix` (orthogonal to `--auto` / `-i`)

- Adds Phases 5b (apply), 5c (push), 5d (post + resolve).
- Without `--fix`: only Phases 5a (draft) — no apply, no push, no post.
- For non-trivial fixes, delegates to `/adk-code:code-bugfix`.
- For trivial edits (typo, formatting, simple suggestion), edits inline.

## What `--fix` will NOT do, ever

1. `gh pr merge` (any flag).
2. `git push --force` to protected branches.
3. `git push --force-with-lease` without confirmation.
4. `gh pr close`.
5. `git branch -D` of the head branch.
6. `gh pr ready` (changing draft → ready) — that's an authorial choice.
7. Approve the PR (`gh pr review --approve`).
8. Re-classify a `wont-fix` to `apply-*` automatically (the user must explicitly re-classify).
9. Resolve a thread before the reply is post-confirmed.
10. Resolve a `discuss-not-fix` / `wont-fix` thread (those stay open by design).

## Subset flags

- `--scope <comment-id-list>` — restrict to a subset of comments by ID (comma-separated GitHub comment IDs).
- `--only-classify` — like `--auto` without `--fix`; explicit form. Outputs classification + drafts; no apply/push/post.
- `--no-resolve` — don't resolve threads even after reply confirms (useful when the user wants the reviewer to verify before resolving).
- `--squash-fixes` — apply all fixes as one squashable commit instead of one-per-comment.

## Default vs override

| Decision | Default | Override |
| --- | --- | --- |
| Comment scope | all open comments | `--scope <id-list>` |
| Apply behavior | apply only `apply-*` classifications | (not user-overrideable per-class; user re-classifies under `-i`) |
| Validation command | `repos[<name>].notes` if listed; else common defaults | (not overrideable; edit `repos.md`) |
| Commit style | one per logical fix (grouped) | `--squash-fixes` |
| Push gate | always asks at first push | (not overrideable) |
| Resolve apply-* threads | yes (after confirm) | `--no-resolve` |
| Resolve discuss/wont-fix/already-resolved | NO | (not overrideable; by design) |
