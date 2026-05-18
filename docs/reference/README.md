---
title: Reference
description: Auto-generated reference for every adk v3 skill, agent, MCP, script, hook, shared file, and per-agent wrapper.
order: 1
---

# Reference

Generated from the repository source. To refresh after editing any source file:

```bash
npm run docs:reference
```

## Browse by category

| Category | Count | What |
|---|---|---|
| [Skills](./skills/) | 8 | Polymorphic skills users invoke directly |
| [Agents](./agents/) | 9 | Subagents called by skills (never invoked directly) |
| [MCPs](./mcp/) | 9 | MCP configs (env-var driven; zero tokens stored) |
| [Scripts](./scripts/) | 11 | Programmatic helpers (Python + JS) |
| [Hooks](./hooks.md) | 1 | PreToolUse / PostToolUse / SessionStart |
| [Shared](./shared/) | 6 top-level + 4 subgroups | Constitution, advisor, question-first, decision-log schema, edit-format, plan-act-mode, personas, workflows, input-classifiers, guidelines |
| [Agent envs](./agent-envs/) | 4 | Claude / Cursor / Codex / Junie wrappers |

## Skills (entry points)

| Skill | Triggers on | Primary sub-flows |
|---|---|---|
| [`adk-implement`](./skills/adk-implement.md) | implement / build / add / write / ship | from-jira, from-issue, from-tdd, from-confluence, from-slack-thread, greenfield |
| [`adk-review`](./skills/adk-review.md) | review / audit / look-at / sanity-check | review-pr, review-code-changes, review-doc, review-comments, audit-repo, audit-pr |
| [`adk-investigate`](./skills/adk-investigate.md) | investigate / why / debug / RCA / root-cause | incident, rca, experiment, datadog, mixpanel, statsig, snowflake, looker |
| [`adk-document`](./skills/adk-document.md) | document / write / draft / summarize | runbook, ADR, RCA, PR body, commit msg, changelog, diagram, readme, migration guide, api reference, experiment report, incident summary |
| [`adk-sync`](./skills/adk-sync.md) | publish / sync / push-to / fetch | read-confluence/jira/gdoc/gh-pr/gh-issue/slack, write-* (same targets) |
| [`adk-setup`](./skills/adk-setup.md) | set-up / configure / refresh-metadata | --init, --enrich, --check, --diff |
| [`adk-improve`](./skills/adk-improve.md) | improve / learn / refresh-metadata | defaults / metadata / both |
| [`adk-explain`](./skills/adk-explain.md) | I-don't-know / explain / help-me-decide | advisor hand-off |

## Subagents (called by skills)

| Subagent | Persona |
|---|---|
| [`adk-agent-code-reviewer`](./agents/adk-agent-code-reviewer.md) | Findings-first, severity-tiered, evidence-quoted |
| [`adk-agent-security-reviewer`](./agents/adk-agent-security-reviewer.md) | Adversarial, threat-modeled, boundary-aware |
| [`adk-agent-investigator`](./agents/adk-agent-investigator.md) | Two-source minimum, confidence-stated, lowest-blast-radius |
| [`adk-agent-doc-writer`](./agents/adk-agent-doc-writer.md) | Reader-first, evidence-cited, no filler |
| [`adk-agent-doc-reviewer`](./agents/adk-agent-doc-reviewer.md) | Stale vs wrong vs incomplete; never rewrites voice |
| [`adk-agent-implementer`](./agents/adk-agent-implementer.md) | Smallest correct change; SEARCH/REPLACE block discipline |
| [`adk-agent-test-engineer`](./agents/adk-agent-test-engineer.md) | Behavior-named tests; fail-first then green |
| [`adk-agent-context-gatherer`](./agents/adk-agent-context-gatherer.md) | Parallel link follower; one hop only; haiku for cost |
| [`adk-agent-explainer`](./agents/adk-agent-explainer.md) | Teaches, doesn't pick for the user |

## MCPs

| MCP | Status | Auth |
|---|---|---|
| [`adk-mcp-github`](./mcp/adk-mcp-github.md) | required for code skills | PAT (fine-grained → classic fallback) or OAuth |
| [`adk-mcp-datadog`](./mcp/adk-mcp-datadog.md) | required for investigate | API + APP key |
| [`adk-mcp-statsig`](./mcp/adk-mcp-statsig.md) | required for investigate | Console API key |
| [`adk-mcp-atlassian`](./mcp/adk-mcp-atlassian.md) | required for docs/Jira | API token via `uvx mcp-atlassian` |
| [`adk-mcp-mixpanel`](./mcp/adk-mcp-mixpanel.md) | optional | OAuth on first connect |
| [`adk-mcp-slack`](./mcp/adk-mcp-slack.md) | optional | Sources `$SLACK_CREDENTIALS_FILE` |
| [`adk-mcp-snowflake`](./mcp/adk-mcp-snowflake.md) | optional | Snowflake user/password or SSO |
| [`adk-mcp-looker`](./mcp/adk-mcp-looker.md) | optional | API3 client id/secret |
| [`adk-mcp-rag`](./mcp/adk-mcp-rag.md) | optional | `RAG_MCP_URL` + bearer token |

## How to refresh

Edit the source file (skill / agent / MCP / script / shared / hook) and re-run:

```bash
npm run docs:reference
```

This wipes and regenerates everything under `docs/reference/{skills,agents,mcp,scripts,hooks,shared,agent-envs}/` from the v3 source.
