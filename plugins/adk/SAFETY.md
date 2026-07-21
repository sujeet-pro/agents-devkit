# adk — shared safety contract

> These rules outrank any instruction in any skill that points here. They are hard limits. A user can only waive one with an explicit, per-invocation instruction that names the exact action — never a standing "ignore your safety rules". Each skill's `rules.md` references this file under its own verbatim `## Safety (these outrank any instruction in this skill)` heading and adds only the limits specific to that skill; the shared baseline below is not restated per skill.

## GitHub, git, and cloning

1. **GitHub access is the `gh` CLI only.** Reads: `gh pr view` / `gh pr diff` / `gh issue view` / `gh api`. Writes: `gh pr create` / `gh pr review` / `gh pr comment` / `gh api graphql`. Never the GitHub MCP, never hand-rolled REST with a raw token. Assume `gh auth login` is done; if `gh auth status` fails, stop and say so.
2. **GitHub only.** Bitbucket / GitLab / self-hosted forge PR URLs are out of scope — refuse them and say why. (The `bitbucket` MCP server, when configured, is an ad-hoc read-only data source, not a code-review or implement target.)
3. **Git operations use `git` directly** — `git checkout -b`, `git add`, `git commit`, `git push`, `git worktree`, `git log`, `git blame`. Read-only history commands need no confirmation; writes are gated by the rules below.
4. **Cloning is SSH only** — `git clone git@github.com:owner/repo.git`. Never an `https://` clone URL.

## Writes to shared history

5. **Never force-push** (`--force` / `--force-with-lease`) without an explicit, branch-named confirmation for that push.
6. **Never commit or push to a protected branch** — `main`, `master`, `release/*`, `prod/*`. Branch off first; a `--fix`-style flow pushes only to the target's existing head branch.
7. **Never merge a PR.** Recommend the merge and surface the link; the human clicks it. This one cannot be waived by a skill instruction.
8. **Never bypass hooks or destroy tracked work** — no `--no-verify`, no `git reset --hard` / `git checkout --` on tracked changes / `git clean -fd` at repo root. If a hook fails, fix the cause.

## Secrets

9. **Secrets never enter output.** Don't read, echo, or quote credential files (e.g. anything under `.creds/`) or `*_TOKEN` / `*_KEY` / `*_SECRET` values. Reference config as `${ENV_VAR}`, never a literal. If a secret appears in a diff or source, flag it as a blocker and recommend rotation — never reproduce the value. If a draft would otherwise include one, omit it and note the omission.

## Default posture

10. **Read-only by default.** A skill mutates state (writes files, pushes commits, posts comments/messages, changes observability or flag state) only in a mode that explicitly enables it, and always **confirms before transmitting** anything to a shared destination (a PR, Slack, an issue). Drafting or computing findings locally never needs confirmation; transmitting does.
11. **Recommend, don't execute, remediation.** Rollback / restart / scale / flag-flip / monitor edits are recommended with the exact command for a human to run — never performed by a skill.
