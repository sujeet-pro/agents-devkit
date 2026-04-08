---
title: Agent Reference
description: 18 shared agent definitions used by ADK skills
order: 2
---

# Agent Reference

ADK includes 18 shared agent definitions in the `agents/` directory. Each agent reference page covers what the agent does, its priorities and focus areas, step-by-step process, allowed tools, preloaded skills, output format, key rules, memory behavior, and which skills invoke it.

All agents use `adk-` prefix to avoid collisions with user custom agents, `memory: project` for cross-session learning, and `effort: high` for quality output.

## Agent Teams

Agents work best with [agent teams](https://code.claude.com/docs/en/agent-teams) enabled:

```json
{ "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
```

## Code Review & Quality Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-code-reviewer`](../agent-code-reviewer.md) | opus | Multi-perspective code review (correctness, security, performance, architecture) | [Details →](../agent-code-reviewer.md) |
| [`adk-repo-auditor`](../agent-repo-auditor.md) | opus | Whole-codebase architecture and maintainability review | [Details →](../agent-repo-auditor.md) |
| [`adk-security-reviewer`](../agent-security-reviewer.md) | opus | Security-focused review (OWASP, auth, data, deps) | [Details →](../agent-security-reviewer.md) |
| [`adk-pr-fixer`](../agent-pr-fixer.md) | sonnet | Targeted code fixes from PR review comments | [Details →](../agent-pr-fixer.md) |

## Documentation & Research Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-doc-reviewer`](../agent-doc-reviewer.md) | opus | Technical and engineering document reviewer | [Details →](../agent-doc-reviewer.md) |
| [`adk-doc-writer`](../agent-doc-writer.md) | opus | Technical document creation with audience-aware structure | [Details →](../agent-doc-writer.md) |
| [`adk-research-agent`](../agent-research-agent.md) | opus | Primary-source and implementation research with citations | [Details →](../agent-research-agent.md) |
| [`adk-code-snippet-agent`](../agent-code-snippet-agent.md) | sonnet | Code example extraction and formatting for docs | [Details →](../agent-code-snippet-agent.md) |
| [`adk-source-publisher`](../agent-source-publisher.md) | sonnet | Publish to GitHub, Bitbucket, Confluence, or Google Docs | [Details →](../agent-source-publisher.md) |

## Design & Migration Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-frontend-designer`](../agent-frontend-designer.md) | opus | Frontend UI and design-system direction | [Details →](../agent-frontend-designer.md) |
| [`adk-migration-analyst`](../agent-migration-analyst.md) | opus | Framework/library migration path analysis | [Details →](../agent-migration-analyst.md) |
| [`adk-guideline-auditor`](../agent-guideline-auditor.md) | opus | Audit guidelines against authoritative sources | [Details →](../agent-guideline-auditor.md) |

## Orchestration Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-intent-analyst`](../agent-intent-analyst.md) | sonnet | Phase-0 prompt expansion and skill routing | [Details →](../agent-intent-analyst.md) |
| [`adk-plan-reviewer`](../agent-plan-reviewer.md) | sonnet | Plan validation for completeness and sequencing | [Details →](../agent-plan-reviewer.md) |
| [`adk-progress-tracker`](../agent-progress-tracker.md) | sonnet | Execution monitoring across waves | [Details →](../agent-progress-tracker.md) |
| [`adk-consensus-agent`](../agent-consensus-agent.md) | sonnet | Merge multi-agent outputs with confidence | [Details →](../agent-consensus-agent.md) |

## Execution Agents

| Agent | Model | Purpose | Reference |
|-------|-------|---------|-----------|
| [`adk-test-agent`](../agent-test-agent.md) | opus | Test writing, coverage analysis, and failure diagnosis | [Details →](../agent-test-agent.md) |
| [`adk-debugger`](../agent-debugger.md) | opus | Root cause analysis and systematic fault isolation | [Details →](../agent-debugger.md) |

## Standard Team Shapes

Skills compose agents into teams for different types of work. See the [`agentic-teams`](/reference/skill-agentic-teams.md) skill reference for the full list of 9 team shapes (Review, Research, Documentation, Diagram, Security, Migration, Engineering, Planning, Execution).
