---
title: Agent Reference
description: 18 shared agent definitions used by ADK skills
order: 2
---

# Agent Reference

ADK includes 18 shared agent definitions in the `agents/` directory. Each is a `.md` file with YAML frontmatter (`name`, `description`, `model`, `tools`, `effort`, `memory`, `color`, `skills`) and a system prompt body. Skills reference agents by name via Claude Code's native agent system.

All agents use `adk-` prefix to avoid collisions with user custom agents, `memory: project` for cross-session learning, and `effort: high` for quality output.

## Agent Teams

Agents work best with [agent teams](https://code.claude.com/docs/en/agent-teams) enabled:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

## Code Review & Quality Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-code-reviewer`](./code-reviewer.md) | opus | Multi-perspective code review (correctness, security, performance, architecture) | [Details →](./code-reviewer.md) |
| [`adk-repo-auditor`](./repo-auditor.md) | opus | Whole-codebase architecture and maintainability review | [Details →](./repo-auditor.md) |
| [`adk-security-reviewer`](./security-reviewer.md) | opus | Security-focused review (OWASP, auth, data, deps) | [Details →](./security-reviewer.md) |
| [`adk-pr-fixer`](./pr-fixer.md) | sonnet | Targeted code fixes from PR review comments | [Details →](./pr-fixer.md) |

## Documentation & Research Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-doc-reviewer`](./doc-reviewer.md) | opus | Technical and engineering document reviewer | [Details →](./doc-reviewer.md) |
| [`adk-doc-writer`](./doc-writer.md) | opus | Technical document creation with audience-aware structure | [Details →](./doc-writer.md) |
| [`adk-research-agent`](./research-agent.md) | opus | Primary-source and implementation research with citations | [Details →](./research-agent.md) |
| [`adk-code-snippet-agent`](./code-snippet-agent.md) | sonnet | Code example extraction and formatting for docs | [Details →](./code-snippet-agent.md) |
| [`adk-source-publisher`](./source-publisher.md) | sonnet | Publish to GitHub, Bitbucket, Confluence, or Google Docs | [Details →](./source-publisher.md) |

## Design & Migration Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-frontend-designer`](./frontend-designer.md) | opus | Frontend UI and design-system direction | [Details →](./frontend-designer.md) |
| [`adk-migration-analyst`](./migration-analyst.md) | opus | Framework/library migration path analysis | [Details →](./migration-analyst.md) |
| [`adk-guideline-auditor`](./guideline-auditor.md) | opus | Audit guidelines against authoritative sources | [Details →](./guideline-auditor.md) |

## Orchestration Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-intent-analyst`](./intent-analyst.md) | sonnet | Phase-0 prompt expansion and skill routing | [Details →](./intent-analyst.md) |
| [`adk-plan-reviewer`](./plan-reviewer.md) | sonnet | Plan validation for completeness and sequencing | [Details →](./plan-reviewer.md) |
| [`adk-progress-tracker`](./progress-tracker.md) | sonnet | Execution monitoring across waves | [Details →](./progress-tracker.md) |
| [`adk-consensus-agent`](./consensus-agent.md) | sonnet | Merge multi-agent outputs with confidence | [Details →](./consensus-agent.md) |

## Execution Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-test-agent`](./test-agent.md) | opus | Test writing, coverage analysis, and failure diagnosis | [Details →](./test-agent.md) |
| [`adk-debugger`](./debugger.md) | opus | Root cause analysis and systematic fault isolation | [Details →](./debugger.md) |

## Standard Team Shapes

Skills compose agents into teams for different types of work. See the [`agentic-teams`](/reference/skills/agentic-teams.md) skill reference for the full list of 9 team shapes (Review, Research, Documentation, Diagram, Security, Migration, Engineering, Planning, Execution).
