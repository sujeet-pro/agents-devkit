---
title: "docs"
description: Documentation router — detects doc task type and routes to the right sub-skill
skill_name: docs
category: routing
workflow_tier: orchestrator
user_invocable: true
---

# docs

Lightweight entry point for all documentation tasks. Detects the task type from the user's input and routes to the appropriate sub-skill. Does not perform any doc work itself.

## When to Use

- Write any kind of documentation and unsure which specific skill to use
- Create, update, or improve documentation pages
- Generate bulk repository documentation
- Review documentation quality
- Work with Confluence pages
- Get markdown formatting guidelines

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | text | required | Description of the documentation task to perform |
| `--help` | flag | — | Show routing table and sub-skill help |

## Routing Table

| Signal | Route To | Invocation |
|--------|----------|------------|
| "write ADR", "write RFC", "blog post", "changelog", "migration guide", "runbook", "proposal", "system design", "tech radar", "tool eval" | Write formal document | `/adk:docs-write` |
| "create doc", "new page", "update doc", "improve doc", "fix doc", "comment reply", "TDD", "HLD", "LLD", "PRD", "ERD", "incident report", "postmortem", "status report", "API reference" | Doc lifecycle management | `/adk:docs-crud` |
| "generate docs", "document this repo", "document this codebase", "docs for the project" | Bulk repo documentation | `/adk:docs-repo` |
| "review docs", "check documentation", "review this doc", "review the RFC", Confluence URL, Google Docs URL | Review documentation | `/adk:docs-review` |
| "Confluence page", "publish to Confluence", "Confluence", "wiki page" | Confluence doc operations | `/adk:docs-confluence` |
| "markdown rules", "pagesmith format", "markdown features" | Markdown guidelines | `/adk:docs-md` |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Input contains a Confluence URL** | Routes to `docs-confluence` for read/write or `docs-review` for review |
| **Input names a formal document type** (ADR, RFC, blog, changelog) | Routes to `docs-write` |
| **Input is about creating, updating, or improving a doc** | Routes to `docs-crud` |
| **Input is about generating docs for a whole repo** | Routes to `docs-repo` |
| **Input is about reviewing docs for quality** | Routes to `docs-review` |
| **Ambiguous input** | Asks the user what kind of documentation task they need |

## Key Behaviors

- **Signal-based routing**: analyzes the user's prompt for keywords and patterns to select the right sub-skill
- **Priority order**: Confluence URL → formal doc type → CRUD action → bulk repo → review → ambiguous fallback
- **Parameter forwarding**: passes all user parameters through to the target skill unchanged
- **Disambiguation**: when the intent is unclear, asks the user to clarify before routing

## Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:docs-write` | Create or update formal engineering documents (ADR, RFC, blog, changelog, etc.) |
| `/adk:docs-crud` | Manage documentation lifecycle — create, update, improve, respond to comments |
| `/adk:docs-repo` | Generate comprehensive repository documentation |
| `/adk:docs-review` | Review docs for accuracy, completeness, clarity, and style |
| `/adk:docs-confluence` | Confluence-specific doc read/write with format mapping to markdown |
| `/adk:docs-md` | Markdown/pagesmith feature detection and formatting guidelines |

## Output Format

No direct output — the router delegates entirely to the matched sub-skill. Output format is determined by the target skill.

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:code-review-pr` | Review code (not documentation) |
| `/adk:diagram` | Create diagrams to embed in documentation |
| `/adk:spec` | Write specifications and checklists |

## Examples

```
/adk:docs write an RFC for the new auth service
/adk:docs create a TDD for payment processing
/adk:docs update the API reference
/adk:docs review the getting started guide
/adk:docs publish to Confluence
/adk:docs generate docs for this repo
/adk:docs --help
```
