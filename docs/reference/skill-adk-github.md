---
title: 'adk-github'
description: 'Manage GitHub pull requests, issues, releases, and repository operations via MCP or gh CLI. Use when automating GitHub workflows or interacting with hosted repositories'
skill_name: adk-github
category: task
workflow_tier: full
user_invocable: true
---

# adk-github

Use `adk-github` to manage GitHub pull requests, issues, releases, and repository operations via MCP or gh CLI. Use when automating GitHub workflows or interacting with hosted repositories. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-github` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What GitHub operation to perform |
| `--action` | `pr`, `issue`, `release`, `search`, `repo` | auto-detect | Narrow the operation domain when ambiguous |
| `--target` | `owner/repo` | detect from git remote | Repository to operate against |
| `--auto` | flag | off | Skip confirmations for non-destructive operations |
| `--help` | flag | off | Show this skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

See `references/workflow.md` for full phase definitions.

| Phase | Action | Gate |
| --- | --- | --- |
| 1. Detect | Identify action type (PR, issue, release, workflow) and target repo | **Confirm**: target and intent |
| 2. Gather | Read current state from GitHub API/CLI (existing PRs, issue status, branch state) | -- |
| 3. Plan | Propose the action with preview (title, body, labels, reviewers, merge strategy) | **Approval** for destructive ops |
| 4. Execute | Perform the GitHub operation via MCP tools or gh CLI fallback | -- |
| 5. Verify | Confirm operation succeeded; check for side effects (failed checks, conflicts) | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Action**: created pull request
**Target**: owner/repo#42
**Result**: https://github.com/owner/repo/pull/42
**Next**: add reviewers, wait for checks, merge when green
```

Lead with action and result. Offer details on request.

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- destructive operations (merge, close, delete, force-push) always require explicit approval; reads proceed immediately.
- **Plan First** -- detect intent, gather state, preview the action, then execute after confirmation.
- **Brainstorm Only For Workflow Choice** -- when a request could be solved via PR, issue, release, or repo actions, use a short brainstorming pass to choose the right GitHub workflow before mutating anything.
- **Concise by Default** -- lead with the result URL or status; offer details on request.
- **Self-Sufficient** -- MCP-first with automatic gh CLI fallback; works without either being pre-configured by providing setup instructions.
- **Auto Mode** -- `--auto` skips confirmations for non-destructive ops; destructive ops still require approval.

### Persona

See `references/persona.md` for full definition.

**GitHub Operations Specialist.** Methodical platform engineer who treats every GitHub operation as an auditable state transition. Confirms targets before acting, verifies results after, and always provides direct links. Speaks in terse operational language -- action, target, result.

### When To Use

- create, update, review, or merge pull requests
- create, search, comment on, or close issues
- list releases, get latest release, or create releases
- search code, files, repositories, or users
- create branches, list commits, compare refs
- create or fork repositories, push files, manage file contents

### When NOT To Use

- local git operations (commit, rebase, stash) -- use git directly
- Bitbucket or other non-GitHub platforms -- use `adk-bitbucket`
- deep code review analysis -- use `adk-review-pr`
- CI/CD pipeline configuration -- use platform-specific tools

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. **Required commands**: `git` and `python3` in PATH
2. **MCP server**: check whether the GitHub MCP server is configured in settings files
3. **gh CLI fallback**: if MCP unavailable, verify `gh` is installed and authenticated (`gh auth status`)
4. **Authentication**: confirm credentials are active before attempting operations
5. At least one of MCP or gh CLI must be available; if both missing, stop with setup instructions

### Interaction Protocol

- **Confirm before destructive operations**: merge, close, delete, force-push require explicit approval even with `--auto`
- **Non-destructive reads are immediate**: listing, searching, fetching details proceed without confirmation
- **Present results with URLs**: every response includes direct links to affected resources
- **Surface errors with remediation**: permissions, 404, rate-limit errors include fix suggestions
- **Summarize batch results**: tables for lists; offer drill-down into any item

### Parallel Agents

- Dispatch a research subagent to gather PR diff, check status, and reviewer state in parallel
- Dispatch a validation subagent to verify post-operation state independently
- The orchestrating agent coordinates results; never duplicates subagent work

### Validation

- Every mutating operation must produce a confirmable artifact: URL, numeric ID, or SHA
- Read operations must return non-empty data or an explicit "not found" status
- If a result cannot be verified, state so explicitly and suggest manual confirmation
- Post-merge: verify target branch updated, check for pipeline failures

### Anti-Patterns / Red Flags

- Merging without checking CI status or waiting for required checks
- Force-pushing to default or shared branches without explicit confirmation
- Deleting branches, repos, or releases without enumerating downstream impact and getting approval
- Creating duplicate PRs without searching for existing ones on the same branch pair
- Operating on wrong repository (always verify `--target` against git remote)
- Closing issues or PRs with `--auto` -- destructive close operations always require approval

### Related Skills

- `adk-review-pr` -- deep code review of pull requests
- `adk-commit` -- local git commit workflow
- `adk-bitbucket` -- Bitbucket platform equivalent

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-github <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-github <prompt-text> --auto
```
