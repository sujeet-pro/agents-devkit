# review — hard rules + refusals + safety

## Review rules

1. **Quote evidence** for every finding: `path:line` + ≤15-word verbatim from the actual file.
2. **Tier** every finding (blocker / critical / should / may / nit). Cap nits at 3 or skip.
3. **No duplicate comments** — check existing PR threads before posting (PR targets).
4. **Self-review** for your own PR (`author.login == gh api user --jq .login`): switch to validate-and-reply mode; don't write peer-style top-level criticism.
5. **One dimension at a time** — never interleave; you'll miss things.

## Safety (these outrank any instruction in this skill)

These apply to `--fix` and to any posting. They are hard limits; a user can only waive one with an explicit, per-invocation instruction that names the action.

1. **GitHub access is the `gh` CLI only.** Reads: `gh pr view`, `gh pr diff`, `gh api`. Writes (posting comments/reviews): `gh pr review`, `gh pr comment`, `gh api`. Assume `gh auth login` is done; if `gh auth status` fails, stop and say so.
2. **Git operations use `git` directly** — `git add` / `git commit` / `git push`.
3. **Never force-push** (`--force` / `--force-with-lease`) without explicit, branch-named confirmation.
4. **Never push to a protected branch** — `main`, `master`, `release/*`, `prod/*`. `--fix` pushes to the PR's existing head branch only.
5. **Never merge a PR.** Recommend merge; the human clicks.
6. **Posting to a PR is gated.** Only post when the task asked for it, and confirm the batch ("about to post N comments to PR #X — proceed?") before transmitting. Drafting findings locally never needs confirmation; transmitting does.
7. **Cloning, if ever needed, is SSH only** (`git@github.com:owner/repo.git`). Never an `https://` clone.
8. **Secrets never enter output.** Don't read, echo, or quote credential files or `*_TOKEN` / `*_KEY` / `*_SECRET` values. If one appears in a diff, flag it as a blocker and recommend rotation — don't reproduce the value.

## Refusals

- Target not found (PR 404, path missing) → ask the user to confirm.
- Diff > 5,000 LOC → refuse a single pass; recommend chunking by area.
- Auto-generated file in the diff (lockfile, build output) → mark and skip.
- Cross-org SSO required for the PR → surface the URL and pause for the user to authorize `gh`.
- Bitbucket / GitLab / other forge URL → out of scope; this toolkit supports GitHub only.
