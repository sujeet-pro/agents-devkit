# pr-review — hard rules + refusals + safety

## Review rules

1. **Cite every finding by `file:line`** + a ≤15-word verbatim quote. No vague claims.
2. **One dimension per agent**; minimum bar correctness + security + tests for any code-touching PR.
3. **Adversarially verify** every finding before it survives (Phase 3).
4. **No drive-by complaints, no re-raising resolved feedback** unless the diff regressed it.
5. **Classify every pre-existing thread** (`comment-resolution.md`) — explicit beats implicit.
6. Prefer **one good finding over three thin ones**. Appreciations: 1–3 per PR when warranted.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — GitHub-only via the `gh` CLI, SSH-only clones, no force-push / no merge / no protected-branch writes, secrets never in output. Two of those are absolute here: **merging is never done** (even with an explicit `--merge`-style request, print the merge link and exit — this skill cannot waive it), and this skill **never pushes to the PR branch at all**. On top of the shared contract, for this skill:

1. **The worktree is READ-ONLY.** Never edit the PR's code; this skill has no Edit/Write tools for the worktree.
2. **Posting is the skill's purpose**, so inline comments auto-post in non-interactive mode — but always **summarize what will post and confirm** before transmitting. `--no-post` posts nothing.

## Refusals

- Not a GitHub PR URL → out of scope; state it.
- PR 404 / no access → surface the URL and the `gh` error; pause for the user to authorize.
- `gh auth status` fails → stop; tell the user to `gh auth login`.
- Diff > ~5,000 LOC → don't single-pass; recommend reviewing by area across multiple runs (`--scope`).
- Auto-generated file in the diff (lockfile, build output) → mark and skip.
