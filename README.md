# claude-devkit

A plugin system for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that adds skills, agents, guidelines, repo-aware configurations, and MCP integrations to supercharge your development workflow.

---

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Developer Setup](#developer-setup)
- [Skills](#skills)
- [Agents](#agents)
- [Guidelines](#guidelines)
- [Repo Configurations](#repo-configurations)
- [MCP Integrations](#mcp-integrations)
- [PR Review Tags](#pr-review-tags)
- [Updating](#updating)
- [Uninstalling](#uninstalling)
- [Contributing](#contributing)

---

## Overview

claude-devkit extends Claude Code with:

- **Skills** — reusable, invocable workflows (PR review, diagram generation, document writing, Slack composition, frontend design)
- **Agents** — specialized sub-processes for focused tasks (code review, research, document review, diagram generation)
- **Guidelines** — context-aware coding standards that load automatically based on repo type
- **Repo Configurations** — per-repo CLAUDE.md templates for design systems, Next.js apps, JS/TS libraries, and backends
- **MCP Integrations** — routing rules for Google Drive, Confluence, Bitbucket, Slack, Gmail, Google Calendar, and multi-model chat
- **Profiles** — auto-detection of repo type from project files, with tag overrides for PR reviews

Everything installs into `~/.claude/` and is available globally across all your projects.

## Guiding Principles

Every skill in claude-devkit is built on these core patterns:

### Iterative Quality Loops

All skills use a **review → fix → verify** loop inspired by proven agentic patterns:

- **Ralph Wiggum Loop** — Iterative fix-verify with stuck detection. Each iteration reviews its own output, fixes issues, and re-checks. Stops when clean, stuck, or max iterations reached.
- **Copilot Self-Review** — Self-review output before presenting to the user. Code skills run lint → fix → test loops. Doc skills run guideline compliance checks.
- **Cursor Pre-PR Workflow** — Run fast quality checks (typecheck, lint, format) in a loop until passing before finalizing.
- **Aider Convergence** — Max iteration limits + no-progress detection to avoid infinite loops. If no fixes are applied in an iteration, the skill stops and reports remaining issues for human decision.

```
while iteration < max_iterations:
    issues = verify_output()
    if no issues: break           # clean — done
    fix(issues)
    if no fixes applied: break    # stuck — needs human
```

### Agent Delegation

Skills delegate to specialized agents rather than doing everything inline. Research goes to the **research-agent**, code blocks to the **code-snippet-agent**, diagrams to the **diagram-agent**. This keeps each component focused and reusable.

### Repo-Level Guideline Priority

Skills automatically discover and prioritize repo-specific guidelines over devkit defaults. They check common locations (`docs/guidelines/`, `guidelines/`, `.github/guidelines/`, `CLAUDE.md` sections) so teams can customize quality standards per project.

### Modern CLI Tooling

All skills use modern CLI replacements (`fd` over `find`, `rg` over `grep`, `bat` over `cat`, `jq` for JSON) for faster, more reliable execution.

## Prerequisites

claude-devkit is designed for macOS and expects specific tools to be installed. These are managed via the [dot-files](https://github.com/sujeet-pro/dot-files) Ansible setup.

### Required CLI Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `fd` | Fast file finder (replaces `find`) | `brew install fd` |
| `rg` (ripgrep) | Fast text search (replaces `grep`) | `brew install ripgrep` |
| `bat` | Syntax-highlighted file viewer (replaces `cat`) | `brew install bat` |
| `jq` | JSON processor | `brew install jq` |
| `gh` | GitHub CLI | `brew install gh` |
| `node` | Node.js runtime | `mise install node` |
| `python3` | Python runtime | `mise install python` |
| `uvx` | Python package runner | `mise install uv` |
| `claude` | Claude Code CLI | `brew install claude-code` |

### Diagram Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `mmdc` (mermaid-cli) | Render Mermaid diagrams to images | `npm install -g @mermaid-js/mermaid-cli` |
| `excalidraw-cli` | Render Excalidraw files to images | `npm install -g excalidraw-cli` |

### Recommended CLI Tools

These enhance agent capabilities for code analysis, diffing, and output quality:

| Tool | Purpose | Install |
|------|---------|---------|
| `ast-grep` | Structural code search/replace using ASTs (far more precise than regex) | `brew install ast-grep` |
| `difft` (difftastic) | Syntax-aware structural diff (understands 30+ languages) | `brew install difftastic` |
| `tokei` | Fast code statistics by language (lines, comments, blanks) | `brew install tokei` |
| `delta` | Syntax-highlighting pager for git diff/grep/blame | `brew install git-delta` |
| `gron` | Make JSON greppable (transforms into discrete assignments) | `brew install gron` |

### Optional CLI Tools

| Tool | Purpose | Install |
|------|---------|---------|
| `eza` | Modern `ls` replacement | `brew install eza` |
| `fzf` | Fuzzy finder | `brew install fzf` |
| `glow` | Render markdown in terminal | `brew install glow` |
| `shellcheck` | Shell script linter | `brew install shellcheck` |
| `hyperfine` | CLI benchmarking | `brew install hyperfine` |

### Environment Variables

Add these to `~/.zshenv` (see `dot-files/configs/shell/.zshenv.example`):

```bash
# Required for Bitbucket MCP (PR reviews)
export BITBUCKET_TOKEN="your-bitbucket-app-password"

# Required for Confluence MCP (document operations)
export CONFLUENCE_API_TOKEN="your-atlassian-api-token"
export CONFLUENCE_BASE_URL="https://yoursite.atlassian.net/wiki"
export CONFLUENCE_EMAIL="your-email@example.com"
```

**OAuth-based services** (no env vars needed):
- **Google Drive MCP**: Browser-based OAuth on first run
- **Slack / Gmail / Calendar**: Claude.ai built-in integrations, connect via Claude Desktop -> Settings -> Integrations

### MCP Servers

See [settings/mcp-setup.md](settings/mcp-setup.md) for detailed setup instructions for each MCP server.

### Verify Setup

```bash
# Check all prerequisites
./scripts/check-prerequisites.sh

# Check environment variables
./scripts/check-env.sh

# Validate MCP server configurations
./scripts/validate-mcp.sh

# Test actual MCP connectivity (inside Claude Code)
/validate-mcp
```

## Quick Start

### Option A: Plugin Marketplace (recommended)

Install directly from Claude Code — no separate publishing step needed, reads `.claude-plugin/marketplace.json` from GitHub:

```bash
# Register this repo as a marketplace
/plugin marketplace add sujeet-pro/claude-devkit

# Install everything (skills + agents + guidelines) — recommended
/plugin install devkit-full@claude-devkit

# Or install components separately
/plugin install devkit-guidelines@claude-devkit  # guidelines only
/plugin install devkit-agents@claude-devkit      # agents only
/plugin install pr-review@claude-devkit          # individual skill
```

> **Note on dependencies**: Most skills depend on shared guidelines (`guidelines/`) and agents (`agents/`). Installing `devkit-full` gets everything. If you install individual skills, they still work but with reduced quality — guideline checks and agent delegation gracefully degrade when dependencies are missing.

### Option B: Git Clone + Install Script

```bash
# Clone the devkit
git clone https://github.com/sujeet-pro/claude-devkit.git ~/.claude-devkit

# Install (copies files into ~/.claude/)
~/.claude-devkit/install.sh

# Or see what's included first
~/.claude-devkit/install.sh --list
```

Optionally install a repo-specific CLAUDE.md into your project:

```bash
cd /path/to/your/project
~/.claude-devkit/install.sh --repo-config=default
```

That is it. Open Claude Code in any project and the skills, agents, and guidelines are available.

## Developer Setup

For contributors who want to edit devkit files and see changes immediately:

```bash
# Clone to your preferred location
git clone https://github.com/sujeet-pro/claude-devkit.git ~/personal/claude-devkit

# Install in dev mode (creates symlinks instead of copies)
cd ~/personal/claude-devkit
./install.sh --mode=dev
```

In dev mode, symlinks point from `~/.claude/` back to the repo. Any file you edit is immediately reflected in Claude Code sessions — no rebuild or re-install needed.

To verify the installation:

```bash
ls -la ~/.claude/skills/
ls -la ~/.claude/agents/
ls -la ~/.claude/guidelines/
```

## Skills

Skills are invocable workflows triggered with the `/` command in Claude Code.

| Skill | Command | Description |
|-------|---------|-------------|
| **PR Review** | `/pr-review <pr>` | Multi-agent code review for GitHub and Bitbucket. Spawns 5 parallel agents (guidelines, bugs, security, performance, architecture), deduplicates findings, and posts inline PR comments after your approval. |
| **Slack Compose** | `/slack-compose <prompt>` | Compose Slack messages with channel/thread context awareness. Supports professional, casual, technical, and announcement tones. Draft-first by default. |
| **Diagram** | `/diagram <description>` | Generate technical diagrams in Mermaid or Excalidraw. Auto-detects diagram type (flowchart, sequence, class, state, ER, architecture). Outputs source files and rendered images. |
| **Doc Review** | `/doc-review <url>` | Review documents on Confluence or Google Docs. Spawns 3 agents (accuracy, clarity, completeness) and posts inline comments after your approval. |
| **Doc Write** | `/doc-write <topic>` | Write comprehensive documents with research, diagrams, and code examples. Outputs to local markdown, Confluence, or Google Docs. |
| **Blog** | `/blog <topic>` | Write, review, or update blog posts. Narrative structure, opinion-driven content, 800–1500 words. Modes: `write`, `review`, `update`. |
| **Article** | `/article <topic>` | Write, review, or update deep technical articles. Exhaustive research, principal engineer voice, 4000–8000+ words. Modes: `write`, `review`, `update`. |
| **Project Docs** | `/project-docs` | Write, review, or update project documentation from codebase scanning. Architecture diagrams, quick starts, API references. Modes: `write`, `review`, `update`. |
| **Research** | `/research <topic>` | Deep web research with citations. Configurable depth: `quick`, `standard`, `exhaustive`. Multi-agent execution with organized findings. |
| **PR Describe** | `/pr-describe <pr>` | Generate and post PR descriptions from code changes. Analyzes diff, commits, and context. Supports GitHub and Bitbucket. Styles: `concise`, `detailed`, `conventional`. |
| **Self-Review** | `/self-review` | Iterative self-review: reviews code, applies fixes, runs lint/test/build in a loop until clean. Configurable scope (`branch`, `staged`), fix mode (`prompt`, `auto`, `dry-run`), and max iterations. |
| **Frontend Design** | `/frontend-design <desc>` | Generate 5 distinct design variations with a self-contained HTML preview. Interactive selection, iteration, and production-ready code output. |
| **Create Skill** | `/create-skill <name>` | Create new devkit skills with iterative quality loops, agent delegation, and guideline compliance built in. Types: `code`, `document`, `review`, `automation`, `integration`. |
| **Validate MCP** | `/validate-mcp [server]` | Test all MCP server connections and help with OAuth login flows. Checks Confluence, Bitbucket, Google Drive, Slack, Gmail, and Calendar connectivity. |

### Skill Examples

```bash
# Review a GitHub PR with auto-detected guidelines
/pr-review 42

# Review a Bitbucket PR with explicit tags
/pr-review https://bitbucket.org/workspace/repo/pull-requests/15 --tags=ds

# Compose a Slack message
/slack-compose "Update the team on the v2.0 release status" --channel=engineering --tone=professional

# Generate an architecture diagram
/diagram "Microservices architecture for the payment system" --type=architecture

# Review a Confluence page
/doc-review https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/12345 --focus=accuracy

# Write a deep-dive document to Confluence
/doc-write "Event-driven architecture patterns" --format=confluence --depth=deep-dive --audience=senior

# Write a new blog post
/blog "Why we migrated from REST to gRPC" --tone=opinionated

# Review an existing blog post
/blog --source=./posts/grpc-migration.md --mode=review

# Write a deep technical article
/article "Understanding the Linux scheduler" --depth=exhaustive --audience=staff

# Update an existing article with latest info
/article --source=./articles/linux-scheduler.md --mode=update

# Generate project docs from codebase
/project-docs --depth=comprehensive

# Review existing docs against the codebase
/project-docs --source=./docs/ --mode=review

# Deep research on a topic
/research "Comparison of vector databases for RAG pipelines" --depth=exhaustive

# Generate a PR description and post it
/pr-describe 42
/pr-describe 42 --style=conventional

# Self-review before pushing
/self-review
/self-review --scope=staged --fix=auto
/self-review --base=develop --max-iterations=3

# Create a new skill
/create-skill deploy-preview --description="Deploy PR preview environments" --type=automation

# Generate frontend design variations
/frontend-design "Analytics dashboard with real-time charts" --framework=nextjs --style=tailwind
```

## Agents

Agents are specialized sub-processes spawned by skills or invoked directly for focused tasks.

| Agent | Model | Description |
|-------|-------|-------------|
| **code-reviewer** | Opus | Multi-perspective code analysis covering bugs, security, performance, and architecture. Outputs structured findings with severity, confidence, and suggested fixes. |
| **diagram-agent** | Opus | Technical diagram specialist. Generates Mermaid and Excalidraw diagrams following best practices for clarity, hierarchy, labeling, and grouping. |
| **doc-reviewer** | Opus | Document review specialist. Evaluates accuracy (verified via web search), clarity, completeness, and formatting. |
| **research-agent** | Opus | Deep research specialist. Searches the web, cross-references sources, synthesizes findings, and provides full citations. |

Agents are used internally by skills (e.g., `/pr-review` spawns the code-reviewer agent five times in parallel), but can also be invoked directly for ad-hoc tasks.

## Guidelines

Guidelines are reference documents loaded as context during PR reviews and code generation. They define coding standards and expectations.

| Guideline | File | Loaded When |
|-----------|------|-------------|
| **General** | `guidelines/general.md` | Always loaded for all reviews |
| **Design System** | `guidelines/design-system.md` | Loaded for `[ds]` tagged repos |
| **Frontend Next.js** | `guidelines/frontend-nextjs.md` | Loaded for `[fe]` tagged repos |
| **JS/TS Library** | `guidelines/js-ts-library.md` | Loaded for `[lib]` tagged repos |
| **Backend Java** | `guidelines/backend-java.md` | Loaded for `[be]` tagged Java repos |
| **Backend Python** | `guidelines/backend-python.md` | Loaded for `[be]` tagged Python repos |
| **Scripts** | `guidelines/scripts.md` | Loaded for `[script]` tagged repos |

The general guideline is always loaded as a baseline. Additional guidelines stack on top based on the detected or explicitly tagged repo type.

## Repo Configurations

Repo configurations are CLAUDE.md templates installed into the root of individual projects. They give Claude Code project-specific instructions.

### Available Templates

| Template | Command | Best For |
|----------|---------|----------|
| **default** | `--repo-config=default` | Any project. General best practices, skill usage guide, MCP reference. |
| **design-system** | `--repo-config=design-system` | Design system repos. Enforces token usage, WCAG 2.1 AA accessibility, component API stability, layered architecture. |
| **frontend-nextjs** | `--repo-config=frontend-nextjs` | Next.js apps. Server vs Client component rules, App Router patterns, Core Web Vitals targets, loading/error state requirements. |
| **library** | `--repo-config=library` | JS/TS libraries. Public API management, bundle size budgets, tree-shaking rules, semantic versioning, TypeScript type quality. |
| **backend** | `--repo-config=backend` | Java/Python backends. API design, error handling hierarchy, security standards, database practices, logging standards. |

### Installation

Install a repo configuration into any project:

```bash
cd /path/to/your/project
/path/to/claude-devkit/install.sh --repo-config=design-system
```

This copies a `CLAUDE.md` file into the project root. If a `CLAUDE.md` already exists, it is backed up with a timestamp before being replaced.

You can edit the installed CLAUDE.md freely. It will only be overwritten if you re-run the `--repo-config` command.

## MCP Integrations

claude-devkit integrates with these MCP servers for external service access:

| MCP Server | Service | Auth | Tools Prefix |
|---|---|---|---|
| `atlassian-confluence` | Confluence pages, spaces, comments | API Token | `mcp__atlassian-confluence__*` |
| `bitbucket` | PRs, repos, pipelines, comments | App Password | `mcp__bitbucket__*` |
| `google-drive` | Google Docs, Sheets, Slides, Drive, Calendar | OAuth (browser) | `mcp__google-drive__*` |
| `claude_ai_Slack` | Slack messages, channels, threads | Claude.ai Integration | `mcp__claude_ai_Slack__*` |
| `claude_ai_Gmail` | Email reading, drafting, searching | Claude.ai Integration | `mcp__claude_ai_Gmail__*` |
| `claude_ai_Google_Calendar` | Calendar events, scheduling | Claude.ai Integration | `mcp__claude_ai_Google_Calendar__*` |
| `multi` | Multi-model comparison, debate | API Keys | `mcp__multi__*` |

### Tool Routing

Claude automatically routes to the correct MCP server based on context:
- Confluence URLs (`*.atlassian.net/wiki/*`) -> `atlassian-confluence` MCP
- Bitbucket URLs (`bitbucket.org/*`) -> `bitbucket` MCP
- Google Docs/Sheets/Slides URLs -> `google-drive` MCP
- Slack operations -> `claude_ai_Slack` MCP
- Email operations -> `claude_ai_Gmail` MCP
- Calendar operations -> `claude_ai_Google_Calendar` MCP

Detailed routing rules are in `settings/mcp-instructions.md`.

## PR Review Tags

Tags customize the PR review focus. They can be applied in three ways (in priority order):

1. **Explicit argument**: `/pr-review 42 --tags=ds,fe`
2. **PR title or description**: `[ds] Add new color tokens for dark mode`
3. **Auto-detected** from project files (package.json, config files, directory structure)

### Supported Tags

| Tag | Repo Type | Extra Scrutiny On |
|-----|-----------|-------------------|
| `[ds]` | Design System | Token usage, accessibility, API stability, visual regression tests |
| `[fe]` | Frontend Next.js | Core Web Vitals, server/client components, SEO, loading states |
| `[lib]` | JS/TS Library | Public API surface, bundle size, tree-shaking, semver, types |
| `[be]` | Backend | Security, error handling, database patterns, API contracts |
| `[script]` | Scripts | Error handling, idempotency, portability, documentation |

Tags are case-insensitive. If no tag is provided and auto-detection does not match, the general guidelines apply.

### Auto-Detection Heuristics

The detection system (`profiles/detect.md`) examines:

- `package.json` fields and dependencies
- Config files (`next.config.js`, `pom.xml`, `pyproject.toml`, etc.)
- Directory structure (`.storybook/`, `packages/`, `src/main/java/`, etc.)
- Keywords in package metadata

## Updating

Update the devkit to the latest version:

```bash
# Auto-detects install mode from manifest
/path/to/claude-devkit/update.sh

# Force a specific mode
/path/to/claude-devkit/update.sh --mode=dev
```

In **dev mode**, the updater runs `git pull --ff-only` in the devkit repo. Since symlinks point to the repo, changes are immediately available.

In **remote mode**, the updater pulls the latest source and re-runs the installer to copy updated files into `~/.claude/`.

## Uninstalling

Remove all devkit-installed files:

```bash
/path/to/claude-devkit/uninstall.sh
```

The uninstaller reads the manifest at `~/.claude/.devkit-manifest` to determine exactly which files to remove. It shows a confirmation prompt before deleting anything.

For non-interactive uninstall (CI/scripts):

```bash
/path/to/claude-devkit/uninstall.sh --yes
```

Note: Uninstalling removes files from `~/.claude/` but does not remove per-repo `CLAUDE.md` files installed via `--repo-config`. Delete those manually if needed.

## Publishing & Distribution

### This repo IS the marketplace

No separate publishing step is needed. The `.claude-plugin/marketplace.json` file makes this repo installable directly from Claude Code via:

```bash
/plugin marketplace add sujeet-pro/claude-devkit
```

Claude Code reads the manifest from GitHub. Push to `main` and it's live.

### Optional: Anthropic Community Skills

Individual skills can also be submitted to the [Anthropic Skills Repository](https://github.com/anthropics/skills) for broader community visibility:

1. Ensure the skill is self-contained (all instructions in `SKILL.md`)
2. Follow the [Anthropic skill format](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
3. Submit a PR to `anthropics/skills` with the skill directory

### Listing Available Skills

```bash
# See all skills, agents, and guidelines in the devkit
./install.sh --list
```

## Contributing

### Project Structure

```
claude-devkit/
├── install.sh              # Main installer (--mode=remote|dev)
├── uninstall.sh            # Removes installed devkit items
├── update.sh               # Updates devkit and re-installs
├── CLAUDE.md               # Instructions for devkit contributors
├── skills/                 # Skill definitions
│   └── <skill-name>/
│       └── SKILL.md
├── agents/                 # Agent definitions
│   └── <agent-name>.md
├── guidelines/             # Guideline documents
│   └── <guideline-name>.md
├── settings/               # Settings and MCP routing
│   ├── base-settings.json
│   └── mcp-instructions.md
├── profiles/               # Repo type detection
│   ├── detect.md
│   └── README.md
└── repo-configs/           # Per-repo CLAUDE.md templates
    ├── design-system/CLAUDE.md
    ├── frontend-nextjs/CLAUDE.md
    ├── library/CLAUDE.md
    ├── backend/CLAUDE.md
    └── default/CLAUDE.md
```

### Adding a New Skill

1. Create a directory: `skills/my-skill/`
2. Add `SKILL.md` with frontmatter (name, description, arguments) and workflow instructions
3. Test: `./install.sh --mode=dev`, then invoke `/my-skill` in Claude Code

### Adding a New Agent

1. Create a file: `agents/my-agent.md`
2. Include frontmatter (name, description, model, tools) and system instructions
3. Test: `./install.sh --mode=dev`, then verify the agent is available

### Adding a New Guideline

1. Create a file: `guidelines/my-guideline.md`
2. Write the guideline rules in markdown
3. Update `profiles/detect.md` if the guideline should be auto-loaded for a repo type
4. Update the PR review skill's guideline loading table if needed

### Adding a New Repo Config

1. Create a directory: `repo-configs/my-type/`
2. Add `CLAUDE.md` with repo-specific instructions
3. Update `install.sh` help text to list the new type
4. Test: `./install.sh --repo-config=my-type` in a test project

### Conventions

- Skills use `SKILL.md` format inside a named directory under `skills/`
- Agents are single `.md` files under `agents/`
- Guidelines are single `.md` files under `guidelines/`
- Settings files go under `settings/`
- All markdown files use ATX-style headers (`#`, `##`, etc.)
- Shell scripts start with `#!/usr/bin/env bash` and use `set -euo pipefail`
- Scripts must work on both macOS (darwin) and Linux

### Testing Your Changes

```bash
# Install in dev mode
./install.sh --mode=dev

# Open a real project and verify skills/agents/guidelines work
# Test uninstall
./uninstall.sh

# Test repo-config installation
cd /path/to/test/project
/path/to/claude-devkit/install.sh --repo-config=default

# Test remote mode
./install.sh --mode=remote
```

---

## License

See [LICENSE](./LICENSE) for details.
