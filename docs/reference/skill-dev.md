---
title: 'dev'
description: 'Development router — detects dev task type and routes to the right sub-skill'
skill_name: dev
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# dev

Use `dev` when you want DevKit to route dev work to the right downstream skill. Its job is classification and parameter forwarding, not doing the downstream work itself.

## Overview

`dev` belongs to the `routing` layer and is declared at the `orchestrator` tier with the `complex-build` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Skill | Description |
|-------|-------------|
| `/adk:dev-build` | Implement features, debug issues, enhance code, run TDD — auto-detects mode |
| `/adk:dev-refactor` | Refactor code — extract, rename, restructure, simplify, modernize |
| `/adk:dev-migrate` | Migrate frameworks, libraries, or language versions |
| `/adk:dev-commit` | Create commits or PR descriptions with conventional messages |

## How It Works

Routing begins by resolving intent. Explicit override flags take priority; otherwise the detection rules below choose a downstream skill, stage, or engine based on the prompt and repository context.

Once the route is fixed, the router keeps parameter forwarding narrow and predictable so the downstream skill receives the same important selectors the user provided.

### Shared Skills

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback |
|--------------|------------------------|------------------------------|------|-----------------|
| preflight-check | `/adk:preflight-check` | `/preflight-check` | before work | Run preflight.py for tool dependencies. |

### Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Routing

Analyze the user's request and route to the matching skill:

| Signal | Route To | Invocation |
|--------|----------|------------|
| "implement", "build", "add feature", "fix bug", "debug", "TDD", "test-driven", "enhance", "improve", "quick fix", "worktree" | Build and implement | `/adk:dev-build` |
| "refactor", "extract", "rename across", "restructure", "simplify", "modernize", "clean up" | Refactor code | `/adk:dev-refactor` |
| "migrate", "upgrade from X to Y", "migration", "breaking changes", "update dependency" | Migrate or upgrade | `/adk:dev-migrate` |
| "commit", "commit message", "PR description", "changelog entry" | Commit and describe | `/adk:dev-commit` |

### Routing Rules

1. If the input mentions implementing, building, debugging, or enhancing code, route to `dev-build`.
2. If the input is about code restructuring without changing behavior, route to `dev-refactor`.
3. If the input mentions migrating from one version/framework to another, route to `dev-migrate`.
4. If the input is specifically about creating commits or PR descriptions, route to `dev-commit`.
5. If the input could be either build or refactor, prefer `dev-build` (it has internal modes for enhancement).
6. If ambiguous, ask the user what kind of development task they need.

### Parameter Forwarding

Pass all parameters from the user's original request to the target skill. The router does not consume any parameters except `--help`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:code-review-pr` — review code after development
- `/adk:plan` — plan before development
- `/adk:spec` — write specifications before implementation
- `/adk:handoff` — pause long development sessions

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:dev
```
