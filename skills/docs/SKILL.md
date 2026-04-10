---
name: docs
description: "adk - [routing] [docs] Documentation router — detects doc task type and routes to the right sub-skill"
user-invocable: true
argument-hint: "<task> [--help]"
allowed-tools: [Glob, Grep, Read]
workflow-tier: orchestrator
workflow-family: standard-task
maturity: stable
---

# Documentation Router

Lightweight entry point for all documentation tasks. Detects the task type from the user's input and routes to the appropriate sub-skill. Does not perform any doc work itself.

## Routing

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

## Help

When `--help` is passed, show this routing table and the help for each sub-skill.

### Sub-Skills

| Skill | Description |
|-------|-------------|
| `/adk:docs-write` | Create or update formal engineering documents (ADR, RFC, blog, changelog, etc.) |
| `/adk:docs-crud` | Manage documentation lifecycle — create, update, improve, respond to comments |
| `/adk:docs-repo` | Generate comprehensive repository documentation |
| `/adk:docs-review` | Review docs for accuracy, completeness, clarity, and style |
| `/adk:docs-confluence` | Confluence-specific doc read/write with format mapping to markdown |
| `/adk:docs-md` | Markdown/pagesmith feature detection and formatting guidelines |

## Adjacent Skills

- `/adk:code-review-pr` — review code (not documentation)
- `/adk:diagram` — create diagrams to embed in documentation
- `/adk:spec` — write specifications and checklists
