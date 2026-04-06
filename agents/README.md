# ADK Agents

Shared agent definitions for child agents spawned by ADK skills during execution.

## Structure

Each agent is a `.md` file with YAML frontmatter (`name`, `description`, `model`, `allowed-tools`) and a system prompt body. Skills reference agents by name via the host's native agent system.

## Agent Index


| Agent                | Model  | Purpose                                                  |
| -------------------- | ------ | -------------------------------------------------------- |
| `code-reviewer`      | opus   | Multi-perspective code review across 10 dimensions       |
| `repo-auditor`       | opus   | Whole-codebase architecture and maintainability review   |
| `doc-reviewer`       | opus   | Technical document review for accuracy and completeness  |
| `research-agent`     | opus   | Primary-source and implementation research               |
| `source-publisher`   | sonnet | Publish to GitHub, Bitbucket, Confluence, or Google Docs |
| `consensus-agent`    | sonnet | Merge and reconcile multi-agent outputs                  |
| `frontend-designer`  | opus   | Frontend and design system direction                     |
| `pr-fixer`           | opus   | Read PR comments and apply targeted code fixes           |
| `security-reviewer`  | opus   | Security-focused code review (OWASP, auth, data)         |
| `migration-analyst`  | opus   | Framework/library migration path analysis                |
| `guideline-auditor`  | sonnet | Audit guidelines against authoritative sources           |
| `code-snippet-agent` | sonnet | Code snippet extraction and formatting                   |
| `intent-analyst`     | sonnet | Expand user intent, assumptions, complexity, and routing |
| `plan-reviewer`      | sonnet | Validate plan completeness, ordering, and estimates      |
| `progress-tracker`   | sonnet | Monitor execution progress, detect stalls and failures   |


## Standard Team Shapes

Skills compose agents into teams. See `templates/skill/references/agentic-teams.md` for the full contract.