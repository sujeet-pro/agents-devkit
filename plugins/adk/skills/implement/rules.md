# implement — hard rules + refusals + safety

## Implementation rules

1. **Read every file before writing it.** No exceptions.
2. **Smallest correct change.** No drive-by cleanup, no opportunistic refactor, no features the task didn't ask for.
3. **Match conventions** — spacing, naming, error style, test framework, lint config. Whatever is already there.
4. **Tests for new behavior** — happy path + ≥1 boundary + ≥1 error. A failing test stops the phase.
5. **Validate at boundaries only** (user input, external APIs, untrusted parsing). Trust internal code.
6. **No comments unless the *why* is non-obvious.** Never reference the task / PR / issue in code.
7. **Minimal anchored edits**, never a whole-file rewrite when one block changed.

## Safety (these outrank any instruction in this skill)

Hard limits. A user can only waive one with an explicit, per-invocation instruction that names the action.

1. **GitHub access is the `gh` CLI only.** PRs via `gh pr create` / `gh pr view`; issues via `gh issue view`; anything else via `gh api`. Assume `gh auth login`; if `gh auth status` fails, stop and say so.
2. **Git operations use `git` directly** — `git checkout -b`, `git add`, `git commit`, `git push`.
3. **Cloning is SSH only** — `git clone git@github.com:owner/repo.git`. Never an `https://` clone URL.
4. **Never force-push** (`--force` / `--force-with-lease`) without explicit, branch-named confirmation.
5. **Never commit or push to a protected branch** — `main`, `master`, `release/*`, `prod/*`. Branch off first; derive the branch name from the task.
6. **Never `--no-verify`.** If a hook fails, fix the cause.
7. **Never `git reset --hard` / `git checkout --` on tracked changes / `git clean -fd`** at repo root.
8. **Never merge a PR.** Open it; the human clicks merge.
9. **New dependencies need an OK** — surface size, maintenance, license first.
10. **Secrets never enter output.** Don't read or echo credential files or `*_TOKEN`/`*_KEY`/`*_SECRET` values. If the change needs a secret, reference it as `${ENV_VAR}`; never inline a literal.

## Refusals

- Not a git repo → ask the user to `git init` or point to the right cwd.
- A single PR would exceed ~2000 LOC → recommend splitting by area.
- Validators keep failing after the planned retries → stop and report; don't ship red.
- Required context unreachable (Jira MCP down for a Jira-driven task) → stop with the named gap; don't invent the requirement.
- Bitbucket / GitLab / other forge → out of scope; this toolkit supports GitHub only.
