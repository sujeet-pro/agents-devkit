# Shared Agents

Markdown files in this directory define reusable agent roles for DevKit skills.

Each agent file has YAML frontmatter with `name`, `description`, `model`, and `allowed-tools`, followed by a system prompt that defines the agent's behavior.

Skills reference agents by name — Claude Code's native agent system loads these definitions automatically when a skill uses `context: fork` with `agent: <name>`.

## Available Agents

| Agent | Purpose |
| --- | --- |
| `code-reviewer` | Multi-perspective code review |
| `doc-reviewer` | Technical document review |
| `research-agent` | Primary-source research |
| `security-reviewer` | Security-focused code review |
| `repo-auditor` | Whole-codebase architecture audit |
| `source-publisher` | Publish to GitHub/Bitbucket/Confluence/Google Docs |
| `consensus-agent` | Merge and reconcile multi-agent outputs |
| `frontend-designer` | Frontend and design-system direction |
| `migration-analyst` | Framework/library migration analysis |
| `pr-fixer` | Apply fixes from PR review comments |
| `guideline-auditor` | Audit guidelines against sources |
| `code-snippet-agent` | Code snippet extraction and formatting |
| `intent-analyst` | Expand user intent, assumptions, complexity, and routing choices |
| `plan-reviewer` | Review implementation plans for completeness and sequencing |
| `progress-tracker` | Monitor execution progress, stalls, and recovery options |
