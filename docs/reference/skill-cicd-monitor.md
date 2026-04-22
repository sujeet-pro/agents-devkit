---
title: 'cicd-monitor'
description: '|'
skill_name: cicd-monitor
category: router
---
# cicd-monitor — watch GH Actions on the current PR

## When to use

- Right after `@adk:publish-github` opens / updates a PR.
- The user says "watch CI", "wait for the build", "let me know when checks pass".

## When NOT to use

- Fix a failing CI run → `@adk:cicd-fix`.
- Non-GitHub provider (Bitbucket Pipelines: not yet supported).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<pr-url>` or `<pr-number>` | optional | Defaults to current branch's PR |
| `<interval>` | optional | Poll interval in seconds (default 30) |
| `--auto` | optional | Auto-handoff to cicd-fix on failure |

## Workflow

1. **Phase 1 validator.** `gh auth status` ok; PR exists for current branch; user has watch perms.
2. **Resolve PR.** `gh pr view --json number,headRefName,statusCheckRollup`.
3. **Initial state.** List all checks: name + status + url.
4. **Watch loop.** `gh pr checks <N> --watch --interval <interval> --fail-fast`.
   - Stream each state change.
   - On any check `failure` or `cancelled`: stop the watch.
5. **On success.** Report green; stop.
6. **On failure.** Capture failed-job logs: `gh run view <runId> --log-failed > .temp/task-<slug>/cicd/<runId>.log`. Identify the failing step name + first error line. Offer to hand off to `@adk:cicd-fix`. Under `--auto`, do it automatically.
7. **On cancellation / timeout.** Report; do not auto-handoff.

## Background mode

Optionally runs as a `monitors/monitors.json` background watcher (already declared in this plugin's `monitors/monitors.json`). When run via that mechanism, status changes appear as Claude notifications during a session.

## Output

- Streamed status updates in chat.
- `.temp/task-<slug>/cicd/<runId>.log` (only on failure).
- `.temp/task-<slug>/cicd/status.md` final summary.

## Mode

`auto` only.

## Anti-patterns

- Polling faster than every 15s (rate-limit risk).
- Forgetting to capture failed-job logs (the user can't fix without them).
- Auto-handing-off to `cicd-fix` without `--auto` (may surprise the user).
- Watching a PR that's not the user's (different branch, different repo) without confirming.

## References

Standard set + `references/gh-watch-recipes.md`.
