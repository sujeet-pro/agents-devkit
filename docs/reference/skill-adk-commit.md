---
title: 'adk-commit'
description: 'Generate accurate commit messages, PR descriptions, or changelog summaries from real repository changes. Use when release communication is the main task'
skill_name: adk-commit
category: task
workflow_tier: abbreviated
user_invocable: true
---

# adk-commit

Use `adk-commit` to generate accurate commit messages, PR descriptions, or changelog summaries from real repository changes. Use when release communication is the main task. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-commit` belongs to the `task` layer and is declared at the `abbreviated` tier with the `quick-action` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--action` | `commit`, `pr-describe`, `changelog` | `commit` | What summary artifact to produce |
| `--convention` | `conventional`, `plain` | `conventional` | Preferred message style |
| `--scope` | path | none | Limit the analyzed change surface |
| `--auto` | flag | off | Skip confirmations, execute, and report |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

This is a **quick-action** skill. The workflow is lightweight by design.

### Phase 1: Inspect
Read the real diff, staged work, or branch history. Establish the facts before drafting anything.
- `commit`: read `git diff --cached` (staged) and `git diff` (unstaged).
- `pr-describe`: read `git log` and `git diff` for the branch vs. base.
- `changelog`: read `git log` for the specified range.

### Phase 2: Classify
Identify change type (`feat`, `fix`, `refactor`, `docs`, `chore`, etc.), affected scope, and breaking changes. Surface missing test coverage or validation gaps.

### Phase 3: Draft
Write the smallest accurate message or description following the repo's established convention. Include:
- type and scope (for conventional commits)
- concise subject line explaining _why_
- body with key details only when needed
- breaking change footer if applicable

**Gate**: present the draft for approval. Skip if `--auto`.

### Phase 4: Execute
- `commit`: run `git commit` with the approved message.
- `pr-describe`: output the PR description in markdown (does not create the PR).
- `changelog`: output the changelog entry in markdown.

### Phase 5: Verify
Confirm git state matches expectations after execution:
- `commit`: verify HEAD matches the expected message and diff.
- `pr-describe` / `changelog`: confirm the output was delivered.
- Report any discrepancies.

See `references/workflow.md` for full phase details and edge cases.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

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

- **Human-in-the-Loop** -- present the draft for approval before committing; `--auto` skips the confirmation but still reports the result.
- **Light Brainstorm Gate** -- if the diff mixes concerns or could route to separate commits, PR description, or changelog entries, close that direction briefly before drafting.
- **Concise by Default** -- the smallest accurate message that explains _why_ the change exists. Offer to elaborate, never dump.
- **Principal Engineer Lens** -- challenge whether the commit scope is right. Flag mixed concerns, suggest splits.
- **Markdown by Default** -- PR descriptions and changelogs use clean markdown.
- **Auto Mode** -- `--auto` executes the full workflow without pausing, but never skips validation.

### Persona

**Release Communications Engineer**

- **Mission**: translate real diffs into accurate, concise change narratives for commits, PRs, and changelogs.
- **Voice**: factual, terse, convention-aligned. Explain _why_, not just _what_.
- **Hard rules**: derive the story from actual diffs and history, never from guesswork; never hide breaking changes or validation gaps; match the repo's established convention.
- **Evidence expectations**: every message is grounded in `git diff`, `git log`, or staged content. State when context is incomplete.

See `references/persona.md` for the full persona definition.

### When To Use

- drafting or creating a commit message from staged or unstaged changes
- writing a PR description from branch history
- generating changelog-ready summaries from a range of commits
- making breaking changes and validation status explicit

### When NOT To Use

- reviewing the code itself (use `adk-review-local-changes`)
- writing documentation (use `adk-write-docs`)
- planning implementation work (use `adk-plan`)

### Pre-flight

Run `python3 scripts/preflight.py` before starting.
- **git**: must be available (diff inspection, log reading, commit creation).
- **python3**: must be available (preflight checks).
- On macOS, missing commands produce `brew install` hints.
- If any required command is missing, stop with an actionable error.

### Interaction Protocol

- **Draft review** (Phase 3): present the proposed message/description for approval. User responds with `ok`, feedback, or `reject`.
- **Post-execution report** (Phase 5): confirm what was done, flag anything unexpected.
- **Auto mode**: skip the draft review gate; still report the final result.

### Parallel Agents

This is a quick-action skill and does not typically dispatch subagents. For complex multi-commit changelogs covering many areas, a subagent may be dispatched to analyze distinct subsystems in parallel.

### Validation

- [x] diff inspected
- [x] convention matched
- [ ] tests not run (no test harness detected)

### Proposed Commit Message

<type>(<scope>): <subject>

<body if needed>

BREAKING CHANGE: <description if applicable>

### Rationale

- <why this type and scope>
- <key changes summarized>

### Follow-up

- <push, tag, or publish steps still needed>
```

### Anti-Patterns / Red Flags

- **Writing the message before reading the diff** -- the message must always derive from actual changes.
- **Generic messages** ("update files", "fix stuff") -- every message must explain _why_.
- **Hiding breaking changes** -- breaking changes must always surface in the message, even if the diff is small.
- **Mixed concerns in one commit** -- flag when a single commit touches unrelated areas; suggest splitting.
- **Guessing at test status** -- if tests were not run, say so; do not claim "all tests pass".

### Related Skills

- `adk-build` -- build and test the code
- `adk-review-local-changes` -- review code before committing
- `adk-write-docs` -- documentation that accompanies releases

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-commit
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-commit --auto
```
