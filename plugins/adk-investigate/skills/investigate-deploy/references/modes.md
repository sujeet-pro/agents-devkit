# `investigate-deploy` — mode contract

`investigate-deploy` is **read-only**. It supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix`.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks documented defaults at every decision:
  - Repo: from CWD via `git remote get-url`, or from `repos.md` if shorthand resolved.
  - Workflow: from `repos.md.repos[<repo>].deploy_workflow`, or `deploy` fallback.
  - Window: `last 2h`.
  - Limit: `50` runs.
- Still validates after every phase.
- Still surfaces a final report.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
  - Phase 0: shows resolved repo + workflow + window, asks "proceed?".
  - Phase 2: shows the constructed `gh` command, asks "run it?".

## `--fix` is not supported

- This skill is read-only. It uses `gh run list` which has no write side-effects.
- If the operator passes `--fix`, the skill rejects with: "investigate-deploy is read-only; use the deploy system UI for rollback / retry / cancel".

## What `--auto` will NEVER do

1. Trigger / retry / cancel a workflow run (`gh run rerun`, `gh run cancel`).
2. Roll back a deploy.
3. Modify a workflow file or its config.
4. Force-push a tag.
5. Claim "deploy caused incident" — that's `/adk-investigate:investigate-incident`'s job.
6. Use the GitHub MCP — `gh` CLI is the documented source for this skill.
