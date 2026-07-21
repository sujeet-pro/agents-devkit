# review — hard rules + refusals + safety

## Review rules

1. **Quote evidence** for every finding: `path:line` + ≤15-word verbatim from the actual file.
2. **Tier** every finding (blocker / critical / should / may / nit). Cap nits at 3 or skip.
3. **No duplicate comments** — check existing PR threads before posting (PR targets).
4. **Self-review** for your own PR (`author.login == gh api user --jq .login`): switch to validate-and-reply mode; don't write peer-style top-level criticism.
5. **One dimension at a time** — never interleave; you'll miss things.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — `gh`-CLI-only GitHub, SSH-only clones, no force-push / no merge / no protected-branch writes, secrets never in output, read-only by default. These apply to `--fix` and to any posting. On top of the shared contract, for this skill:

1. **`--fix` pushes to the target PR's existing head branch only** — never a new branch, never a protected branch.
2. **Posting to a PR is gated.** Only post when the task asked for it, and confirm the batch ("about to post N comments to PR #X — proceed?") before transmitting. Drafting findings locally never needs confirmation; transmitting does.

## Refusals

- Target not found (PR 404, path missing) → ask the user to confirm.
- Diff > 5,000 LOC → refuse a single pass; recommend chunking by area.
- Auto-generated file in the diff (lockfile, build output) → mark and skip.
- Cross-org SSO required for the PR → surface the URL and pause for the user to authorize `gh`.
- Bitbucket / GitLab / other forge URL → out of scope; this toolkit supports GitHub only.
