# adk-brainstorm

Close ambiguity before planning, docs, or implementation.

## Quick Start

```text
/adk-brainstorm "Design the rollout for a new auth flow" --skill-context plan --artifact plan
```

## What This Skill Does

`adk-brainstorm` captures the current state, target state, acceptable blast radius, desired confidence, and preferred artifact before a task moves into spec, planning, docs, or implementation. It prefers the `brainstorming` MCP server when configured and falls back to the shared manual workflow when it is not.

## Typical Routes

- `adk-spec` for PRDs and formal specifications
- `adk-plan` for executable implementation plans
- `adk-write-docs` for proposals, RFCs, HLDs, LLDs, and TDDs
- `adk-build` when no persistent artifact is needed and the path is already clear

## Examples

```text
/adk-brainstorm "Choose between a surgical fix and a bounded refactor for flaky retries" --skill-context build --confidence 95 --change-tolerance surgical
/adk-brainstorm "Decide what docs we need for a new internal platform capability" --skill-context write-docs --artifact all
```
