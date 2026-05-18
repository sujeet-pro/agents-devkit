# adk-review — hard rules + refusals

## Hard rules

1. **Quote evidence** for every finding: `path:line` + ≤15-word verbatim from the actual file.
2. **Tier**: blocker / critical / should / may / nit. Cap nits at 3 or skip.
3. **No duplicate comments** — check existing PR threads before posting.
4. **Self-review for own PRs**: when `author.login == git.user`, switch to validate-and-reply mode (no peer-style top-level comments).
5. **`--fix` never merges**, never force-pushes, never touches protected branches.
6. **One dimension pass at a time** — don't interleave; you'll miss things.

## Refusals

- Target not found (PR URL 404, path missing) → ask user to confirm.
- Diff > 5,000 LOC → refuse single-pass; recommend chunking by area.
- Auto-generated file in the diff (lockfile, build output) → mark and skip.
- Cross-org SSO required for the PR → surface the URL, pause for user to authorize.
