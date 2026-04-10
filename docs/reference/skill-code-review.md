---
title: 'code-review'
description: 'Code review router — detects review type and routes to the right sub-skill'
skill_name: code-review
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# code-review

Use `code-review` when you want DevKit to route code review work to the right downstream skill. Its job is classification and parameter forwarding, not doing the downstream work itself.

## Overview

`code-review` belongs to the `routing` layer and is declared at the `orchestrator` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Skill | Description |
|-------|-------------|
| `/adk:code-review-pr` | Review code changes in a PR, local diff, or branch. Supports review, fix, describe, finalize actions. |
| `/adk:code-review-repo` | Review an entire repository for architecture, code quality, patterns, and tech debt. |
| `/adk:code-review-fix` | Fix PR review comments — read comments, apply code fixes, reply to reviewers. |

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Routing

Analyze the user's request and route to the matching skill:

| Signal | Route To | Invocation |
|--------|----------|------------|
| PR URL (github.com/*/pull/*, bitbucket.org/*/pull-requests/*), "PR", "pull request", "my changes", "review this PR", diff/patch input | Code review a PR | `/adk:code-review-pr` |
| "fix comments", "address feedback", "resolve", "apply fixes", "PR comments" | Fix review comments | `/adk:code-review-fix` |
| "repo", "codebase", "architecture", "tech debt", "review this repo", no specific target | Review entire repository | `/adk:code-review-repo` |

### Routing Rules

1. If the input contains a PR URL, always route to `code-review-pr` regardless of other keywords.
2. If the input mentions fixing or addressing existing review comments, route to `code-review-fix`.
3. If the input is about reviewing a whole repo or codebase, route to `code-review-repo`.
4. If ambiguous, ask the user: "Are you reviewing a PR, fixing review comments, or auditing the codebase?"

### Parameter Forwarding

Pass all parameters from the user's original request to the target skill. The router does not consume any parameters except `--help`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:docs-review` — review documentation (not code)
- `/adk:audit` — broader audit with security, performance, and dependency focus
- `/adk:dev-build` — implement features and fix bugs

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:code-review
```
