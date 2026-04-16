# ADK Agent Personas

Canonical reusable agent personas for parallel agentic teams live here.

Each persona is authored once in `agent-personas/adk-*/AGENT.md`. Runtime-specific
install surfaces are generated from those canonical prompts into:

- `agents-claude/*.md`
- `agents-cursor/*.md`
- `agents-codex/*.toml`

## Available Personas

| Agent | Role | Used By |
| --- | --- | --- |
| `adk-brainstorm-facilitator` | Iterative brainstorming, trade-off analysis, and route selection | `adk-brainstorm` |
| `adk-code-reviewer` | Code review with severity-ordered findings | `adk-review-pr`, `adk-review-local-changes` |
| `adk-security-reviewer` | Security-focused analysis | `adk-review-pr`, `adk-audit-repo` |
| `adk-test-engineer` | Test writing, execution, and coverage analysis | `adk-test`, `adk-build` |
| `adk-doc-writer` | Documentation authoring and review | `adk-write-docs`, `adk-review-docs` |
| `adk-research-agent` | Deep technical research with evidence | `adk-research`, `adk-plan` |
| `adk-plan-reviewer` | Plan critique and gap analysis | `adk-plan` |
| `adk-implementer` | Focused code implementation | `adk-build`, `adk-refactor` |
| `adk-debugger` | Systematic root-cause analysis | `adk-build` (debug mode) |

## Persona Format

Each persona directory contains an `AGENT.md` with:

- Mission
- Scope
- Hard rules
- Output format
- Anti-patterns

Regenerate runtime projections after editing a canonical persona:

```bash
python3 scripts/generate_agent_projections.py
```
