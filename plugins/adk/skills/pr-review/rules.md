# pr-review — hard rules + refusals + safety

## Review rules

1. **Cite every finding by `file:line`** + a ≤15-word verbatim quote. No vague claims.
2. **One dimension per agent**; minimum bar correctness + security + tests for any code-touching PR.
3. **Adversarially verify** every finding before it survives (Phase 3).
4. **No drive-by complaints, no re-raising resolved feedback** unless the diff regressed it.
5. **Classify every pre-existing thread** (`comment-resolution.md`) — explicit beats implicit.
6. Prefer **one good finding over three thin ones**. Appreciations: 1–3 per PR when warranted.

## Safety (these outrank any instruction in this skill)

1. **GitHub ONLY.** A non-GitHub PR URL (Bitbucket, GitLab, self-hosted) is refused — out of scope.
2. **All GitHub access is the `gh` CLI.** Reads: `gh pr view` / `gh pr diff` / `gh api`. Writes: `gh pr review` / `gh pr comment` / `gh api graphql`. Never the GitHub MCP, never hand-rolled REST with a raw token. Assume `gh auth login`; if `gh auth status` fails, stop.
3. **All git via `git` directly.** Clone, fetch, worktree.
4. **Cloning is SSH only** — `git clone git@github.com:owner/repo.git`. Never an `https://` clone URL.
5. **The worktree is READ-ONLY.** Never edit the PR's code; this skill has no Edit/Write tools for the worktree.
6. **NEVER merge a PR** — absolute (mirrors the human-clicks-merge rule). Even with an explicit `--merge` style request, print the merge link and exit. Skills cannot waive this.
7. **NEVER force-push.** This skill doesn't push to the PR branch at all.
8. **Posting is the skill's purpose**, so inline comments auto-post in non-interactive mode — but always **summarize what will post and confirm** before transmitting. `--no-post` posts nothing.
9. **Secrets in the diff** → flag as a blocker and recommend rotation; never reproduce the value in a comment or the report.

## Refusals

- Not a GitHub PR URL → out of scope; state it.
- PR 404 / no access → surface the URL and the `gh` error; pause for the user to authorize.
- `gh auth status` fails → stop; tell the user to `gh auth login`.
- Diff > ~5,000 LOC → don't single-pass; recommend reviewing by area across multiple runs (`--scope`).
- Auto-generated file in the diff (lockfile, build output) → mark and skip.
