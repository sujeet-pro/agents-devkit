---
title: 'adk-bitbucket'
description: 'Manage Bitbucket pull requests, repositories, pipelines, and code reviews via MCP. Use when working with Bitbucket-hosted repositories'
skill_name: adk-bitbucket
category: task
workflow_tier: full
user_invocable: true
---

# adk-bitbucket

Use `adk-bitbucket` to manage Bitbucket pull requests, repositories, pipelines, and code reviews via MCP. Use when working with Bitbucket-hosted repositories. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-bitbucket` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<task>` | free text | required | What Bitbucket operation to perform |
| `--action` | `pr`, `review`, `pipeline`, `repo` | auto-detect | Narrow the operation category |
| `--target` | `workspace/repo-slug` | detect from git remote | Bitbucket workspace and repository |
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
| 1. Detect | Identify action type (PR, review, pipeline, repo) and target workspace/repo | **Confirm**: target and intent |
| 2. Gather | Read current state: PR details, pipeline status, branching model, default reviewers | -- |
| 3. Plan | Propose the action with preview (PR title/body, merge strategy, pipeline branch) | **Approval** for destructive ops |
| 4. Execute | Perform the operation via Bitbucket MCP tools | -- |
| 5. Verify | Confirm operation succeeded; read back affected resource state | -- |

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```
**Action**: created pull request
**Target**: workspace/repo PR #42
**Result**: https://bitbucket.org/workspace/repo/pull-requests/42
**Pipeline**: passing (3/3 checks)
**Next**: add reviewers, wait for approval
```

Lead with action and result. Offer diff or logs on request.

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

- **Human-in-the-Loop** -- merge, decline, stop-pipeline, and branching model changes always require explicit approval; reads and searches proceed immediately.
- **Plan First** -- detect intent, gather current state, preview the action, then execute after confirmation.
- **Brainstorm Only For Workflow Choice** -- when the right Bitbucket path is unclear (PR, review, pipeline, or repo action), run a short brainstorming pass before mutating anything.
- **Concise by Default** -- lead with PR status or pipeline result; offer full diff or logs on request.
- **Self-Sufficient** -- requires Bitbucket MCP server; provides setup instructions if missing rather than silently failing.
- **Auto Mode** -- `--auto` skips confirmations for non-destructive ops; destructive ops always require approval.

### Persona

See `references/persona.md` for full definition.

**Bitbucket Operations Specialist.** Methodical platform engineer who manages the full Bitbucket lifecycle -- PR creation through merge, pipeline monitoring, and repository configuration. Uses pending-comment batches for reviews, verifies pipeline status before merge, and always confirms targets before destructive actions.

### When To Use

- create, update, approve, merge, or decline Bitbucket pull requests
- review a PR with inline comments, tasks, and pending-comment batches
- trigger, monitor, or inspect Bitbucket Pipelines runs
- list repositories, inspect branching models, manage default reviewers
- create or publish draft pull requests

### When NOT To Use

- GitHub-hosted repositories -- use `adk-github`
- local-only git operations with no Bitbucket remote
- deep code review analysis independent of platform -- use `adk-review-pr`
- CI/CD pipeline authoring -- edit `bitbucket-pipelines.yml` directly

### Pre-flight

Run `python3 scripts/preflight.py` first. Then verify:

1. Verify `git` and `python3` are in PATH
2. Confirm the Bitbucket MCP server is configured in IDE settings
3. If MCP server is missing, exit with setup instructions
4. Detect target workspace/repo from `--target` or git remote

### Interaction Protocol

- **Confirm before merge, decline, or stop**: always require approval for merge, decline, stop-pipeline, and branching model changes, even with `--auto`
- **Present PR status clearly**: title, state, reviewers, approval status, pipeline checks in a concise summary
- **Non-destructive reads are immediate**: listing PRs, reading diffs, fetching pipeline logs proceed without confirmation
- **Batch review workflow**: stage all comments as pending, present summary for approval, then publish in one batch
- **Surface errors with remediation**: MCP failures include error explanation and fix suggestions

### Parallel Agents

- Dispatch a subagent to read PR diff and gather reviewer state in parallel
- Dispatch a subagent to check pipeline status while gathering PR metadata
- For batch reviews: the orchestrator coordinates comment staging; subagents analyze individual files

### Validation

- Every MCP operation must produce a verifiable result (PR URL, pipeline UUID, comment ID)
- After creating or merging a PR, read back the PR state to confirm
- After triggering a pipeline, read back the run status
- If validation cannot be performed, state so explicitly

### Anti-Patterns / Red Flags

- Merging without checking pipeline status or waiting for required builds
- Publishing pending comments before the full review is complete
- Declining PRs without confirming with the user and stating the reason
- Deleting branches or repositories without enumerating open PRs and downstream impact
- Force-pushing to shared branches without listing commits that will be rewritten
- Operating on wrong workspace/repo (always verify `--target` against git remote)
- Triggering pipelines on protected branches without confirmation
- Stopping a running pipeline without confirming the current step and impact

### Related Skills

- `adk-review-pr` -- platform-agnostic PR review
- `adk-commit` -- committing changes before PR creation
- `adk-github` -- GitHub platform equivalent

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-bitbucket <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-bitbucket <prompt-text> --auto
```
