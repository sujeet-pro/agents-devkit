# DevKit

DevKit is a shared skills pack for software-development agents. It provides code review, documentation, research, codebase audits, diagrams, engineering workflows, and source-native publishing across Claude, Codex, Cursor, Gemini, OpenCode, and related hosts.

`review-*` skills leave comments or produce review artifacts without mutating the source. `write-*` skills draft or directly revise professional engineering documents.

Inspired by [superpowers](https://github.com/obra/superpowers). Diagram skills from [diagramkit](https://github.com/sujeet-pro/diagramkit). Markdown capabilities informed by [pagesmith](https://github.com/sujeet-pro/pagesmith).

## Install

### Claude Code

Register the marketplace and install the plugin:

```bash
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install devkit@devkit-marketplace
```

Skills become available as `/devkit:<skill-name>` immediately.

**For contributors** — clone the repo and link it as the active plugin so local edits reflect immediately:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
# Inside Claude Code, run:
/dev-link
```

This symlinks `~/.claude/plugins/marketplaces/devkit-marketplace` to your working directory. Run `/dev-link action=unlink` to restore the published version.

See [SETUP.md](./SETUP.md) for MCP server configuration and dependency validation.

### Cursor

Install via the Cursor plugin marketplace:

```
/add-plugin devkit
```

Or search "devkit" in the Cursor plugin marketplace UI.

Skills and agents are registered automatically from `.cursor-plugin/plugin.json`.

### Codex CLI

Tell Codex to fetch and follow the install instructions:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/sujeet-pro/agents-devkit/refs/heads/main/.codex/INSTALL.md
```

This clones the repo to `~/.devkit` and symlinks the skills directory into `~/.agents/skills/devkit` for native discovery. See [docs/README.codex.md](./docs/README.codex.md) for details.

### Gemini CLI

```bash
gemini extensions install https://github.com/sujeet-pro/agents-devkit
```

Gemini loads `GEMINI.md` as context and maps DevKit tool references to native Gemini equivalents. See [GEMINI.md](./GEMINI.md) for runtime rules.

### OpenCode

Add DevKit as a git-backed plugin in your `opencode.json`:

```json
{
  "plugin": ["devkit@git+https://github.com/sujeet-pro/agents-devkit.git"]
}
```

Restart OpenCode after updating the config. The plugin bridge registers the skills directory and injects the bootstrap skill. See [docs/README.opencode.md](./docs/README.opencode.md) for details.

## Update

All platforms: run `/devkit:manage-update` from within your agent session. This pulls the latest from GitHub, syncs upstream sources, validates tools, and auto-installs missing dependencies.

```bash
/devkit:manage-update                              # Pull latest, auto-install deps
/devkit:manage-update no-auto-install=true         # Pull latest, check only
/devkit:manage-update dry-run=true                 # Preview changes without applying
/devkit:manage-update refresh-mcp=true             # Re-read ~/.zshenv and refresh MCP config
```

After update, the skill automatically runs `/devkit:manage-setup` to validate and install any new dependencies.

### Platform-Specific Notes

| Platform | What `/devkit:manage-update` does | Post-update |
|----------|----------------------------------|-------------|
| Claude Code | `git pull` in `~/.claude/plugins/marketplaces/devkit-marketplace` | Run `/reload-plugins` |
| Cursor | `git pull` in Cursor plugin cache | Restart Cursor |
| Codex CLI | `git pull` in `~/.devkit` | Auto-reflects via symlinks |
| Gemini CLI | `git pull` in extensions directory | Restart Gemini CLI |
| OpenCode | `git pull` in plugin cache | Restart OpenCode |

### Setup Validation

Run setup independently at any time (idempotent):

```bash
/devkit:manage-setup                               # Check + auto-install missing required tools
/devkit:manage-setup no-auto-install=true           # Check only, no installs
/devkit:manage-setup refresh-mcp=true               # Re-read ~/.zshenv, refresh MCP servers
```

## Skills

### Reviewing Others' PRs

| Skill | Use When |
| --- | --- |
| `/devkit:review-code` | Route a code review request to PR review, local review, or codebase review |
| `/devkit:review-code-pr` | Review a GitHub or Bitbucket PR — auto-detects fresh vs follow-up, defaults to interactive mode |

### Managing My PRs

| Skill | Use When |
| --- | --- |
| `/devkit:pr-describe` | Generate or update a PR description from the real diff |
| `/devkit:pr-fix-comments` | Read PR review comments, fix the code, and commit changes |
| `/devkit:pr-finalize` | Verify, review, and choose how to integrate the branch |

### Other Reviews

| Skill | Use When |
| --- | --- |
| `/devkit:review-code-local` | Review staged, unstaged, or branch-local work without auto-fixing it |
| `/devkit:review-doc` | Review markdown, Confluence, or Google Docs without editing the source |
| `/devkit:review-codebase` | Audit an entire repository and suggest improvements |
| `/devkit:audit-security` | Deep security-focused code review (OWASP, auth, data, deps) |
| `/devkit:audit-performance` | Bundle size, latency, memory analysis with recommendations |

### Documentation and Research

| Skill | Use When |
| --- | --- |
| `/devkit:write-doc` | Draft or directly revise engineering docs with research, code examples, and diagrams |
| `/devkit:write-project-docs` | Generate or refresh professional project documentation from the codebase |
| `/devkit:write-article` | Draft or revise a deep engineering article |
| `/devkit:write-blog` | Draft or revise an engineering blog post |
| `/devkit:write-markdown` | Produce markdown-first engineering deliverables |
| `/devkit:publish-confluence` | Publish markdown docs and assets to Confluence |
| `/devkit:research` | Multi-agent software engineering research |
| `/devkit:research-quick` | Quick research pass |
| `/devkit:research-deep` | Exhaustive research pass |

### Engineering Workflows

| Skill | Use When |
| --- | --- |
| `/devkit:write-adr` | Generate or refresh Architecture Decision Records |
| `/devkit:audit-dependency` | Scan for outdated/vulnerable dependencies |
| `/devkit:write-migration-guide` | Generate framework/library migration guides |
| `/devkit:write-changelog` | Generate changelogs from git history |
| `/devkit:write-onboarding` | Generate repo-specific onboarding docs |
| `/devkit:write-api-docs` | Generate API documentation from code |
| `/devkit:write-runbook` | Create operational runbooks |
| `/devkit:write-tech-radar` | Evaluate and classify technologies |

### Diagrams and Design

| Skill | Use When |
| --- | --- |
| `/devkit:diagram` | Pick the right diagram engine and generate source plus render |
| `/devkit:diagram-mermaid` | Generate Mermaid diagrams |
| `/devkit:diagram-excalidraw` | Generate Excalidraw diagrams |
| `/devkit:diagram-drawio` | Generate draw.io diagrams |
| `/devkit:diagram-graphviz` | Maintain or create Graphviz/DOT diagrams when the repo already uses them |
| `/devkit:diagram-convert` | Convert rendered assets when PNG or JPEG is required |
| `/devkit:design-frontend` | Create frontend or design-system directions |

### Development Process

| Skill | Use When |
| --- | --- |
| `/devkit:plan-brainstorm` | Design refinement and specification |
| `/devkit:plan-write` | Turn requirements into execution plans |
| `/devkit:plan-execute` | Execute plans with review checkpoints and per-task child agents |
| `/devkit:dev-tdd` | RED-GREEN-REFACTOR cycle enforcement |
| `/devkit:dev-debug` | 4-phase root cause analysis |
| `/devkit:dev-verify` | Evidence-based verification |
| `/devkit:pr-finalize` | Merge/PR/cleanup workflow |
| `/devkit:dev-worktree` | Isolated workspace creation |

### Utility

| Skill | Use When |
| --- | --- |
| `/devkit:agent-multi` | Run a task through multiple providers or models |
| `/devkit:agent-team` | Orchestrate complex tasks across multiple agents |
| `/devkit:manage-validate` | Validate MCP server configuration |
| `/devkit:manage-update` | Update DevKit from GitHub or local filesystem |
| `/devkit:manage-improve` | Audit and improve DevKit itself |
| `/devkit:manage-skill` | Create or update DevKit skills |
| `/devkit:use` | Choose the right entry skill at session start |

## Agents

| Agent | Purpose |
| --- | --- |
| `code-reviewer` | Diff-aware code review |
| `repo-auditor` | Whole-codebase architecture and maintainability review |
| `doc-reviewer` | Technical document review |
| `research-agent` | Primary-source and implementation research |
| `source-publisher` | Publish results to GitHub, Bitbucket, Confluence, or Google Docs |
| `consensus-agent` | Merge agent or provider outputs |
| `frontend-designer` | Frontend and design-system direction |
| `pr-fixer` | Read PR comments and apply targeted code fixes |
| `security-reviewer` | Security-focused code review (OWASP, auth, data) |
| `migration-analyst` | Framework/library migration analysis |
| `guideline-auditor` | Audit guidelines against authoritative sources |

## Guidelines

### Coding
General, Architecture, Frontend (Next.js), Design System, Backend (General, Java, Python, Kotlin, Node.js), JS/TS Library, Scripts, API Design, Testing, Observability, Security

### Document
General, Article, Blog, PRD, HLD, LLD, TDD, Project, Tool Evaluation, Research, ADR, System Design, Deep Dive, Runbook, API Reference, Changelog

## MCP Integrations

| MCP | Use |
| --- | --- |
| GitHub | PR review, code operations, comments |
| Bitbucket | PR review, code operations, comments |
| Atlassian Confluence | Document review, publishing |
| Google Drive | Google Docs review, publishing |

See [settings/mcp-setup.md](./settings/mcp-setup.md) for setup details.

## Source Manifest

DevKit tracks upstream sources in `manifest.json`:

| Source | Type | What |
| --- | --- | --- |
| [diagramkit](https://github.com/sujeet-pro/diagramkit) | copy | Diagram skills and reference docs |
| [superpowers](https://github.com/obra/superpowers) | copy | Development process skills |
| [pagesmith](https://github.com/sujeet-pro/pagesmith) | ref | Markdown capabilities reference |

Sync with: `zsh scripts/sync-sources.zsh`

## Validation

```bash
zsh scripts/check-prerequisites.zsh          # CLI tools
zsh scripts/check-env.zsh                    # Environment variables
zsh scripts/check-skill-deps.zsh review-pr   # Skill-specific deps
zsh install.zsh --list                       # List all installable items
```

## Repo Layout

```text
agents-devkit/
├── .claude-plugin/      # Claude Code plugin metadata
├── .cursor-plugin/      # Cursor plugin metadata
├── .codex/              # Codex setup docs
├── .opencode/           # OpenCode setup docs
├── agents/              # Agent definitions
├── lib/                 # Shared Node.js utilities
├── profiles/            # Repo-type detection rules
├── scripts/             # Validation, setup, sync scripts
├── settings/            # Settings and MCP docs
├── skills/              # Skill library
│   └── _references/     # Guidelines, reference docs, diagram specs
├── manifest.json        # Upstream source tracking
└── install.zsh          # Idempotent installer
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, guidelines, agents, and test locally.
