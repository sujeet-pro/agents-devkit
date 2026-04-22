---
title: 'cicd-fix'
description: 'Parse failed CI job logs (from `@adk:cicd-monitor` (a.'
artifact_kind: skill
skill_name: cicd-fix
category: standalone
---
# cicd-fix

Parse failed CI job logs (from `@adk:cicd-monitor` (a.k.a. `adk-cicd-monitor`) or `gh run view --log-failed`), identify root cause, propose and apply a fix, push, then loop back to `cicd-monitor` to re-watch. Handles common failure classes: lint, typecheck, test, build, missing dep, snapshot drift, flaky test, infra retry. Use whenever CI is red and the user wants the agent to address it. Do not use for code changes unrelated to CI (use `@adk:build-feature` or `@adk:build-bugfix`).

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-cicd-fix` form via `agents-skills/`.

```text
/adk:cicd-fix            # interactive run (Claude Code)
/adk:cicd-fix --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-cicd-fix` (resolved through the
`agents-skills/adk-cicd-fix/` symlink).

## Source

Direct from `skills/cicd-fix/SKILL.md` — this page is auto-generated.

## When to use

- A `cicd-monitor` run reported failure.
- The user pasted a failed job URL ("fix this CI failure").

## When NOT to use

- The fix is unrelated to CI (use the appropriate `build-*` skill).
- The failure is in a third-party action / runner infra (escalate to user; not a code fix).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<run-id>` or `<failed-log-path>` | yes | From `cicd-monitor` or pasted by user |
| `--auto` | optional | Apply fix without approval gate |

## Workflow

1. **Phase 1 validator.** Failed log accessible.
2. **Classify failure** (per `references/failure-class-recipes.md`):
   - `lint` — eslint/ruff/etc. exit non-zero.
   - `typecheck` — tsc/mypy/go-vet failure.
   - `test` — unit/integration test failure.
   - `build` — bundler/compiler failure.
   - `dep-missing` — `Cannot find module` / `package not found`.
   - `snapshot-drift` — snapshot test diff (likely intentional change without snapshot update).
   - `flaky` — failure on retry succeeds, or known-flaky pattern in repo.
   - `infra` — runner timeout, registry unreachable, etc.
3. **Per class, apply recipe:**
   - lint → run repo's autofix command (`npm run lint -- --fix`); commit.
   - typecheck → read the error, fix the type, run typecheck locally to confirm.
   - test → read the failure, fix the underlying code OR (if test is wrong and we're sure) update the test.
   - build → read the error; usually missing import or syntax; fix.
   - dep-missing → `npm install <dep>` or restore lockfile; commit.
   - snapshot-drift → if intentional change, run `npm test -- -u` to update snapshots; commit.
   - flaky → run `gh run rerun <runId> --failed` ONCE; if still failing, treat as real and re-classify.
   - infra → `gh run rerun <runId>`; if still failing, escalate.
4. **Approval gate** (unless `--auto`): show classification + proposed fix; ask "apply?".
5. **Apply fix.** Edit files. Run local validator (`@adk:review-local --mode review` quick).
6. **Commit + push.** `git commit -m "fix(ci): <one-liner>"` + `git push`.
7. **Loop back.** Hand off to `@adk:cicd-monitor` to re-watch.
8. **Phase 4 validator.** Push successful; new run in progress.

## Mode

- `auto` (default): present diagnosis + fix; gate; apply.
- `fix`: same workflow; no gate (suitable for `auto` chains).

## Output

- Inline progress in chat.
- `.temp/task-<slug>/cicd/fix-<runId>.md` (diagnosis + applied fix + new run id).

## Anti-patterns

- "Fixing" by removing the failing test.
- Updating snapshots without verifying the change is intentional.
- Pushing without local validation.
- Looping more than 3 times on the same class without escalating.
- Treating flaky as real on the first occurrence (try one rerun first).
- Treating real failures as flaky (only one rerun allowed).

## References

Standard set + `references/failure-class-recipes.md`.


## Related skills

- [`auto`](./skill-auto.md) — `@adk:auto` (a.k.a. `adk-auto`)
- [`build`](./skill-build.md) — `@adk:build` (a.k.a. `adk-build`)
- [`cicd-monitor`](./skill-cicd-monitor.md) — `@adk:cicd-monitor` (a.k.a. `adk-cicd-monitor`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
