# ADK Agents

Shared agent definitions for child agents spawned by ADK skills during execution. Each agent is a Claude Code [subagent](https://code.claude.com/docs/en/sub-agents) distributed via the `adk` plugin.

## Agent Teams

ADK agents work best with [agent teams](https://code.claude.com/docs/en/agent-teams) enabled. To enable, add to your project's `.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

If agent teams are not enabled, skills fall back to sequential execution or subagent delegation.

## Structure

Each agent is a `.md` file with YAML frontmatter and a system prompt body. Skills reference agents by name via Claude Code's native agent system.

### Required Frontmatter Fields

| Field | Description |
|-------|-------------|
| `name` | Unique identifier with `adk-` prefix (e.g., `adk-code-reviewer`) |
| `description` | When Claude should delegate to this agent |
| `model` | `opus` for heavy analysis, `sonnet` for focused tasks |
| `tools` | Tool allowlist ([available tools](https://code.claude.com/en/tools-reference)) |
| `effort` | Quality level: `high` (default for ADK agents) |
| `memory` | Persistent learning scope: `project` (default) or `user` |
| `color` | UI color in task list: blue, green, cyan, pink, yellow, purple, orange, red |

### Optional Frontmatter Fields

| Field | Description |
|-------|-------------|
| `skills` | Skills to preload into agent context at startup |
| `maxTurns` | Maximum agentic turns before stopping |
| `permissionMode` | Permission handling: `default`, `acceptEdits`, `auto`, `plan` |
| `background` | Set `true` to always run as a background task |
| `isolation` | Set `worktree` for isolated git worktree execution |

## Naming Convention

- Agent names use `adk-` prefix: `adk-code-reviewer`, `adk-research-agent`
- Plugin users see agents as `adk:adk-code-reviewer` in the typeahead
- The prefix prevents collisions with user custom agents

## Agent Index

| Agent | Model | Color | Purpose |
| ----- | ----- | ----- | ------- |
| `adk-code-reviewer` | opus | blue | Multi-perspective code review across 10 dimensions |
| `adk-repo-auditor` | opus | blue | Whole-codebase architecture and maintainability review |
| `adk-security-reviewer` | opus | blue | Security-focused code review (OWASP, auth, data) |
| `adk-pr-fixer` | sonnet | blue | Read PR comments and apply targeted code fixes |
| `adk-doc-reviewer` | opus | green | Technical document review for accuracy and completeness |
| `adk-doc-writer` | opus | green | Technical document creation with audience-aware structure |
| `adk-code-snippet-agent` | sonnet | green | Code snippet extraction and formatting |
| `adk-research-agent` | opus | cyan | Primary-source and implementation research |
| `adk-migration-analyst` | opus | cyan | Framework/library migration path analysis |
| `adk-frontend-designer` | opus | pink | Frontend and design system direction |
| `adk-intent-analyst` | sonnet | yellow | Expand user intent, assumptions, complexity, and routing |
| `adk-plan-reviewer` | sonnet | yellow | Validate plan completeness, ordering, and estimates |
| `adk-progress-tracker` | sonnet | yellow | Monitor execution progress, detect stalls and failures |
| `adk-consensus-agent` | sonnet | purple | Merge and reconcile multi-agent outputs |
| `adk-source-publisher` | sonnet | purple | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `adk-guideline-auditor` | opus | orange | Audit guidelines against authoritative sources |
| `adk-test-agent` | opus | red | Test writing, coverage analysis, and failure diagnosis |
| `adk-debugger` | opus | red | Root cause analysis and systematic fault isolation |

## Memory

All agents use `memory: project` to accumulate project-specific knowledge across sessions. Memory is stored in `.claude/agent-memory/<agent-name>/` and is shareable via version control.

Agents are instructed to:
- **Read** their memory at the start of each task to apply accumulated knowledge
- **Update** their memory with patterns, conventions, and decisions discovered during work

Over time, agents become more effective as they learn project-specific conventions, common issues, and user preferences.

## Skills Preloading

Agents can have ADK skills preloaded into their context via the `skills` field. This gives agents domain knowledge without requiring runtime discovery:

| Agent | Preloaded Skills | Purpose |
|-------|-----------------|---------|
| `adk-code-reviewer` | `coding`, `review-standards` | Coding guidelines + review pipeline |
| `adk-security-reviewer` | `coding` | Security-relevant coding patterns |
| `adk-repo-auditor` | `coding`, `architecture` | Coding + architecture patterns |
| `adk-pr-fixer` | `coding` | Coding conventions for fixes |
| `adk-doc-reviewer` | `docs-guidelines`, `docs-md` | Doc standards + markdown rules |
| `adk-doc-writer` | `docs-guidelines`, `docs-md` | Doc standards + markdown rules |
| `adk-code-snippet-agent` | `docs-md` | Markdown code block conventions |
| `adk-migration-analyst` | `coding` | Framework usage patterns |
| `adk-frontend-designer` | `coding` | Frontend coding patterns |
| `adk-test-agent` | `coding` | Test framework conventions |
| `adk-debugger` | `coding` | Debugging-relevant code patterns |

## Standard Team Shapes

Skills compose agents into teams. See `templates/skill/references/agentic-teams.md` for the full contract.
