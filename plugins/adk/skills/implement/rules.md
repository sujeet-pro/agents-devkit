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

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — `gh`-CLI-only GitHub, SSH-only clones, no force-push / no merge / no protected-branch writes, no `--no-verify` or destructive git, secrets never in output, read-only until a plan is confirmed. On top of the shared contract, for this skill:

1. **Branch off before writing.** Derive the feature branch name from the task (e.g. the Jira key or issue slug); never work directly on the checked-out protected branch.
2. **New dependencies need an OK** — surface size, maintenance, and license before adding one.

## Refusals

- Not a git repo → ask the user to `git init` or point to the right cwd.
- A single PR would exceed ~2000 LOC → recommend splitting by area.
- Validators keep failing after the planned retries → stop and report; don't ship red.
- Required context unreachable (Jira MCP down for a Jira-driven task) → stop with the named gap; don't invent the requirement.
- Bitbucket / GitLab / other forge → out of scope; this toolkit supports GitHub only.
