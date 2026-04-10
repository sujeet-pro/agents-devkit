---
title: 'docs'
description: 'Documentation router — detects doc task type and routes to the right sub-skill'
skill_name: docs
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# docs

Use `docs` when you want DevKit to route docs work to the right downstream skill. Its job is classification and parameter forwarding, not doing the downstream work itself.

## Overview

`docs` belongs to the `routing` layer and is declared at the `orchestrator` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Skill | Description |
|-------|-------------|
| `/adk:docs-write` | Create or update formal engineering documents (ADR, RFC, blog, changelog, etc.) |
| `/adk:docs-crud` | Manage documentation lifecycle — create, update, improve, respond to comments |
| `/adk:docs-repo` | Generate comprehensive repository documentation |
| `/adk:docs-review` | Review docs for accuracy, completeness, clarity, and style |
| `/adk:docs-confluence` | Confluence-specific doc read/write with format mapping to markdown |
| `/adk:docs-md` | Markdown/pagesmith feature detection and formatting guidelines |

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Routing

Analyze the user's request and route to the matching skill:

| Signal | Route To | Invocation |
|--------|----------|------------|
| "write ADR", "write RFC", "blog post", "changelog", "migration guide", "runbook", "proposal", "system design", "tech radar", "tool eval" | Write formal document | `/adk:docs-write` |
| "create doc", "new page", "update doc", "improve doc", "fix doc", "comment reply", "respond to comments", "TDD", "HLD", "LLD", "PRD", "ERD", "incident report", "postmortem", "status report", "API reference" | Doc lifecycle management | `/adk:docs-crud` |
| "generate docs", "document this repo", "document this codebase", "docs for the project" | Bulk repo documentation | `/adk:docs-repo` |
| "review docs", "check documentation", "review this doc", "review the RFC", Confluence URL, Google Docs URL | Review documentation | `/adk:docs-review` |
| "Confluence page", "publish to Confluence", "Confluence", "wiki page" | Confluence doc operations | `/adk:docs-confluence` |
| "markdown rules", "pagesmith format", "markdown features" | Markdown guidelines | `/adk:docs-md` |

### Routing Rules

1. If the input contains a Confluence URL, route to `docs-confluence` for read/write or `docs-review` for review.
2. If the input explicitly names a formal document type (ADR, RFC, blog, changelog), route to `docs-write`.
3. If the input is about creating, updating, or improving an existing doc, route to `docs-crud`.
4. If the input is about generating docs for a whole repo, route to `docs-repo`.
5. If the input is about reviewing docs for quality, route to `docs-review`.
6. If ambiguous, ask the user what kind of documentation task they need.

### Parameter Forwarding

Pass all parameters from the user's original request to the target skill. The router does not consume any parameters except `--help`.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


## Related Skills

### Adjacent Skills

- `/adk:code-review-pr` — review code (not documentation)
- `/adk:diagram` — create diagrams to embed in documentation
- `/adk:spec` — write specifications and checklists

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:docs
```
