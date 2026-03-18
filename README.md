# claude-devkit

A plugin system for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that adds skills, agents, guidelines, repo-aware configurations, and MCP integrations to supercharge your development workflow.

---

## Quick Start

Install everything in Claude Code with two commands:

```bash
/plugin marketplace add sujeet-pro/claude-devkit
/plugin install devkit-full@claude-devkit
```

This installs all skills, agents, and guidelines globally into `~/.claude/`. Available immediately across all your projects.

For guided setup with MCP server configuration, give Claude Code the [`SETUP.md`](./SETUP.md) file:

```
Read SETUP.md and follow the instructions to set up claude-devkit
```

For contributors who want to edit devkit files and see changes live, see [Developer Setup](#developer-setup).

---

## Table of Contents

- [Overview](#overview)
- [Capability Routing](#capability-routing)
- [Skills](#skills)
- [Agents](#agents)
- [Guidelines](#guidelines)
- [Repo Configurations](#repo-configurations)
- [MCP Integrations](#mcp-integrations)
- [PR Review Tags](#pr-review-tags)
- [Prerequisites](#prerequisites)
- [Developer Setup](#developer-setup)
- [Selective Plugin Install](#selective-plugin-install)
- [Updating](#updating)
- [Uninstalling](#uninstalling)
- [Contributing](#contributing)

---

## Overview

claude-devkit extends Claude Code with:

- **Skills** — reusable, invocable workflows (PR review, diagram generation, document writing, Slack composition, frontend design)
- **Agents** — specialized sub-processes for focused tasks (code review, research, document review, diagram generation)
- **Guidelines** — context-aware coding and document standards that load automatically based on repo type and document type
- **Repo Configurations** — per-repo CLAUDE.md templates for design systems, Next.js apps, JS/TS libraries, and backends
- **MCP Integrations** — routing rules for Google Drive, Confluence, Bitbucket, Slack, Gmail, and Google Calendar
- **Profiles** — auto-detection of repo type from project files, with tag overrides for PR reviews

Everything installs into `~/.claude/` and is available globally across all your projects.

### Guiding Principles

Every skill in claude-devkit is built on these core patterns:

**Agentic Teams** — Skills delegate to specialized agents via the Agent tool rather than doing everything inline. Research goes to the **research-agent**, code blocks to the **code-snippet-agent**, diagrams to the **diagram-agent**. Multi-agent reviews spawn 5 parallel agents for comprehensive coverage. This keeps each component focused, reusable, and independently improvable.

**Iterative Quality Loops** — All skills use a **review -> fix -> verify** loop with convergence detection:

```
while iteration < max_iterations:
    issues = verify_output()
    if no issues: break           # clean — done
    fix(issues)
    if no fixes applied: break    # stuck — needs human
```

**Principal Engineer Quality** — All output targets senior audience (staff/principal engineers, stakeholders, management). Code must address performance, security, accessibility, maintainability, DX, and cost. Documents require technical accuracy with citations to authoritative sources.

**Repo-Level Guideline Priority** — Skills automatically discover and prioritize repo-specific guidelines over devkit defaults. They check common locations (`docs/guidelines/`, `guidelines/`, `.github/guidelines/`, `CLAUDE.md` sections) so teams can customize quality standards per project.

**Modern CLI Tooling** — All skills use modern CLI replacements (`fd` over `find`, `rg` over `grep`, `bat` over `cat`, `jq` for JSON) for faster, more reliable execution.

## Capability Routing

Use these rules to select the right skill, agent, or MCP server for any task.

### Task -> Skill Mapping

| Task | Skill | Agents Used |
|------|-------|-------------|
| Review a PR | `/pr-review <pr>` | 5x code-reviewer (parallel: guidelines, bugs, security, performance, architecture) |
| Self-review before push | `/self-review` | code-reviewer |
| Generate PR description | `/pr-describe <pr>` | — |
| Auto-detect review type | `/review` | Routes to `/pr-review` or `/doc-review` |
| Deep technical article | `/article <topic>` | research-agent, diagram-agent, code-snippet-agent |
| Blog post | `/blog <topic>` | research-agent, code-snippet-agent |
| Project documentation | `/project-docs` | diagram-agent, code-snippet-agent |
| General document | `/doc-write <topic>` | research-agent, diagram-agent, code-snippet-agent |
| Review a document | `/doc-review <url>` | 5x doc-reviewer (parallel: structure, accuracy, clarity, code, consistency) |
| Any diagram | `/diagram <desc>` | diagram-agent -> mermaid-agent or excalidraw-agent |
| Web research | `/research <topic>` | 1-5x research-agent (parallel, configurable depth) |
| Quick search/lookup | `/search <topic>` | 1x research-agent (Sonnet, Opus in multi-mode) |
| Deep exhaustive research | `/deep-research <topic>` | 5x research-agent (alias for /research --depth=exhaustive) |
| Slack message | `/slack-compose` | — (uses Slack MCP) |
| Publish to Confluence | `/confluence-publish` | — (uses Confluence MCP) |
| Frontend design | `/frontend-design <desc>` | frontend-designer |
| Review changed code | `/simplify` | — |
| Test MCP connections | `/validate-mcp` | — |
| Create new skill | `/create-skill <name>` | research-agent |
| Multi-model mode | `/multi <task>` or `--multi` flag | consensus-agent |

### MCP Server Routing

| Context | MCP Server | Tools Prefix |
|---------|-----------|-------------|
| Confluence URLs (`*.atlassian.net/wiki/*`) | `atlassian-confluence` | `mcp__atlassian-confluence__*` |
| Bitbucket URLs (`bitbucket.org/*`) | `bitbucket` | `mcp__bitbucket__*` |
| Google Docs/Sheets/Slides/Drive | `google-drive` | `mcp__google-drive__*` |
| Slack operations | `claude_ai_Slack` | `mcp__claude_ai_Slack__*` |
| Email operations | `claude_ai_Gmail` | `mcp__claude_ai_Gmail__*` |
| Calendar operations | `claude_ai_Google_Calendar` | `mcp__claude_ai_Google_Calendar__*` |

Detailed routing rules are in [`settings/mcp-instructions.md`](settings/mcp-instructions.md).

### Quality Dimensions

All skills enforce these quality dimensions at Principal Engineer level:

- **Performance** — Optimize hot paths, lazy loading, caching with invalidation, pagination, batch operations, bundle size tracking
- **Security** — Input validation, auth/authz, no secrets committed, OWASP top 10, dependency auditing, rate limiting
- **Accessibility** — WCAG 2.1 AA, semantic HTML, keyboard navigation, color contrast (4.5:1), ARIA, screen reader testing
- **Maintainability** — Clear naming, DRY (3+ threshold), test coverage, documentation for public APIs, atomic commits
- **DX** — Typed APIs, helpful error messages, examples, quick starts, structured logging
- **Cost** — Bundle size budgets, query efficiency, resource utilization, TCO analysis for tool choices

## Skills

Skills are invocable workflows triggered with the `/` command in Claude Code.

### Code Review & Quality

| Skill | Command | Description |
|-------|---------|-------------|
| **PR Review** | `/pr-review <pr>` | Multi-agent code review for GitHub and Bitbucket. Spawns 5 parallel agents (guidelines, bugs, security, performance, architecture), deduplicates findings, and posts inline PR comments after your approval. |
| **Self-Review** | `/self-review` | Iterative self-review: reviews code, applies fixes, runs lint/test/build in a loop until clean. Configurable scope (`branch`, `staged`), fix mode (`prompt`, `auto`, `dry-run`), and max iterations. |
| **PR Describe** | `/pr-describe <pr>` | Generate and post PR descriptions from code changes. Analyzes diff, commits, and context. Supports GitHub and Bitbucket. Styles: `concise`, `detailed`, `conventional`. |
| **Review** | `/review` | Universal review orchestrator — auto-detects PR vs document and routes to the appropriate review skill. |

### Document Writing

| Skill | Command | Description |
|-------|---------|-------------|
| **Article** | `/article <topic>` | Write, review, or update deep technical articles. Exhaustive research, principal engineer voice, 3000–6000 words. Modes: `write`, `review`, `update`. |
| **Blog** | `/blog <topic>` | Write, review, or update blog posts. Narrative structure, opinion-driven content, 800–1500 words. Modes: `write`, `review`, `update`. |
| **Project Docs** | `/project-docs` | Write, review, or update project documentation from codebase scanning. Architecture diagrams, quick starts, API references. Modes: `write`, `review`, `update`. |
| **Doc Write** | `/doc-write <topic>` | Write comprehensive documents with research, diagrams, and code examples. Outputs to local markdown, Confluence, or Google Docs. |
| **Doc Review** | `/doc-review <url>` | Multi-agent document review. Spawns 5 parallel agents (structure, accuracy, clarity, code, consistency) and posts findings after your approval. |

### Diagrams

| Skill | Command | Description |
|-------|---------|-------------|
| **Diagram** | `/diagram <description>` | Generate technical diagrams. Auto-selects Mermaid (structured) or Excalidraw (freeform) based on diagram type. |
| **Mermaid** | `/mermaid <description>` | Generate Mermaid diagrams (20+ types: flowchart, sequence, class, ER, C4, etc.). Rendered SVG output. |
| **Excalidraw** | `/excalidraw <description>` | Generate Excalidraw diagrams. Hand-drawn aesthetic, best for architecture overviews. |

### Research & Communication

| Skill | Command | Description |
|-------|---------|-------------|
| **Research** | `/research <topic>` | Web research with citations. Depth: `light`/`standard` (default)/`deep`/`exhaustive`. Multi-agent execution with organized findings. |
| **Deep Research** | `/deep-research <topic>` | Exhaustive research with 5 parallel agents. Alias for `/research --depth=exhaustive`. |
| **Search** | `/search <topic>` | Quick lightweight research using Sonnet for speed. Alias for `/research --depth=light`. Uses Opus in multi-model mode. |
| **Slack Compose** | `/slack-compose <prompt>` | Compose Slack messages with channel/thread context awareness. Supports professional, casual, technical, and announcement tones. Draft-first by default. |
| **Confluence Publish** | `/confluence-publish` | Publish markdown documents to Confluence with full format conversion (diagrams, code, tables, attachments). |

### Frontend & Utility

| Skill | Command | Description |
|-------|---------|-------------|
| **Frontend Design** | `/frontend-design <desc>` | Generate 5 distinct design variations with self-contained HTML preview. Interactive selection, iteration, and production-ready code output. |
| **Create Skill** | `/create-skill <name>` | Create new devkit skills with iterative quality loops, agent delegation, and guideline compliance built in. |
| **Validate MCP** | `/validate-mcp [server]` | Test all MCP server connections and help with OAuth login flows. |
| **Multi** | `/multi <task>` | Run any task through multiple AI models (claude, codex, gemini, cursor) in parallel. Opus consensus merges results. Also available as `--multi` flag on any skill. |
| **Improve** | `/improve` | Audit and upgrade devkit skills, agents, guidelines, and integrations. |

### Skill Examples

```bash
# Review a GitHub PR with auto-detected guidelines
/pr-review 42

# Review a Bitbucket PR with explicit tags
/pr-review https://bitbucket.org/workspace/repo/pull-requests/15 --tags=ds

# Self-review before pushing
/self-review
/self-review --scope=staged --fix=auto

# Compose a Slack message
/slack-compose "Update the team on the v2.0 release status" --channel=engineering --tone=professional

# Generate an architecture diagram
/diagram "Microservices architecture for the payment system" --type=architecture

# Review a Confluence page
/doc-review https://yourcompany.atlassian.net/wiki/spaces/ENG/pages/12345 --focus=accuracy

# Write a deep-dive document to Confluence
/doc-write "Event-driven architecture patterns" --format=confluence --depth=deep-dive

# Write a new blog post
/blog "Why we migrated from REST to gRPC" --tone=opinionated

# Write a deep technical article
/article "Understanding the Linux scheduler" --depth=exhaustive

# Generate project docs from codebase
/project-docs --depth=comprehensive

# Standard research (default depth)
/research "Comparison of vector databases for RAG pipelines"

# Quick search (uses Sonnet for speed)
/search "what is the latest Next.js version"

# Deep exhaustive research (5 agents)
/deep-research "Kubernetes networking CNI comparison"

# Research with depth aliases
/research "event sourcing patterns" --depth=deep
/research "is bun faster than node" --depth=light

# Generate a PR description and post it
/pr-describe 42 --style=conventional

# Create a new skill
/create-skill deploy-preview --description="Deploy PR preview environments" --type=automation

# Generate frontend design variations
/frontend-design "Analytics dashboard with real-time charts" --framework=nextjs --style=tailwind
```

## Agents

Agents are specialized sub-processes spawned by skills via the Agent tool (Agentic Teams). Skills orchestrate agents — you invoke the skill, and it delegates to the right agents automatically.

| Agent | Model | Spawned By | Description |
|-------|-------|-----------|-------------|
| **code-reviewer** | Opus | `/pr-review`, `/self-review` | Multi-perspective code analysis covering bugs, security, performance, and architecture. Outputs structured findings with severity, confidence (0-100), and suggested fixes. |
| **doc-reviewer** | Opus | `/doc-review`, `/doc-write` | Multi-dimensional document analysis. Evaluates structure, accuracy (verified via web search), clarity, code quality, and consistency. |
| **research-agent** | Opus | `/research`, `/article`, `/blog`, `/doc-write` | Deep research specialist. Searches the web, cross-references sources, synthesizes findings, and provides full citations. |
| **diagram-agent** | Opus | `/diagram` | Diagram orchestrator. Selects Mermaid or Excalidraw based on diagram type and delegates to the appropriate specialist agent. |
| **mermaid-agent** | Opus | `diagram-agent` | Mermaid diagram specialist. Comprehensive reference for all Mermaid v11 diagram types with syntax validation and SVG rendering. |
| **excalidraw-agent** | Opus | `diagram-agent` | Excalidraw diagram specialist. Generates `.excalidraw` JSON files with proper arrow routing, layout, color palettes, and validation. |
| **code-snippet-agent** | Opus | `/doc-review`, `/article`, `/blog` | Expressive-code block specialist. Writes and reviews code blocks in documents with proper collapsing, highlighting, and titles. |
| **frontend-designer** | Opus | `/frontend-design` | UI design specialist. Creates distinctive, production-grade designs with WCAG 2.1 AA accessibility and responsive requirements. |
| **consensus-agent** | Opus | `/multi` | Synthesizes outputs from multiple AI models into unified consensus. Evaluates agreement, resolves disagreements, and attributes provenance. |

## Guidelines

Guidelines are reference documents loaded as context during reviews, code generation, and document writing. They define coding standards and quality expectations at Principal Engineer level.

### Coding Guidelines

Loaded during PR reviews and code generation. The general guideline is always loaded as a baseline; additional guidelines stack on top based on repo type.

| Guideline | File | Loaded When |
|-----------|------|-------------|
| **General** | `guidelines/coding/general.md` | Always loaded for all reviews |
| **Design System** | `guidelines/coding/design-system.md` | Loaded for `[ds]` tagged repos |
| **Frontend Next.js** | `guidelines/coding/frontend-nextjs.md` | Loaded for `[fe]` tagged repos |
| **JS/TS Library** | `guidelines/coding/js-ts-library.md` | Loaded for `[lib]` tagged repos |
| **Backend Java** | `guidelines/coding/backend-java.md` | Loaded for `[be]` tagged Java repos |
| **Backend Python** | `guidelines/coding/backend-python.md` | Loaded for `[be]` tagged Python repos |
| **Scripts** | `guidelines/coding/scripts.md` | Loaded for `[script]` tagged repos |
| **Expressive Code** | `guidelines/coding/expressive-code.md` | Loaded for code blocks in documents |

### Document Guidelines

Loaded during document writing and review. The general guideline is always loaded; type-specific guidelines load based on document type detection.

| Guideline | File | Loaded When |
|-----------|------|-------------|
| **General** | `guidelines/document/general.md` | Always loaded for all documents |
| **Technical Design Document** | `guidelines/document/tdd.md` | TDD writing/review |
| **High Level Design** | `guidelines/document/hld.md` | HLD writing/review |
| **Low Level Design** | `guidelines/document/lld.md` | LLD writing/review |
| **Product Requirements** | `guidelines/document/prd.md` | PRD writing/review |
| **Engineering Requirements** | `guidelines/document/erd.md` | ERD writing/review |
| **Tool Evaluation** | `guidelines/document/tool-evaluation.md` | Tool evaluation writing/review |
| **Technical Article** | `guidelines/document/article.md` | `/article` writing/review |
| **Blog Post** | `guidelines/document/blog.md` | `/blog` writing/review |
| **Project Documentation** | `guidelines/document/project.md` | `/project-docs` writing/review |
| **Appraisal** | `guidelines/document/appraisal.md` | Performance review documents |
| **Feedback** | `guidelines/document/feedback.md` | Feedback documents |
| **Community Guidelines** | `guidelines/document/community-guidelines.md` | Community/governance documents |
| **Coding Guidelines** | `guidelines/document/coding-guidelines.md` | Coding standards documents |

## Repo Configurations

Repo configurations are CLAUDE.md templates installed into the root of individual projects. They give Claude Code project-specific instructions.

| Template | Directory | Best For |
|----------|-----------|----------|
| **default** | `repo-configs/default/` | Any project. General best practices, skill usage guide, MCP reference. |
| **design-system** | `repo-configs/design-system/` | Design system repos. Enforces token usage, WCAG 2.1 AA accessibility, component API stability, layered architecture. |
| **frontend-nextjs** | `repo-configs/frontend-nextjs/` | Next.js apps. Server vs Client component rules, App Router patterns, Core Web Vitals targets, loading/error state requirements. |
| **library** | `repo-configs/library/` | JS/TS libraries. Public API management, bundle size budgets, tree-shaking rules, semantic versioning, TypeScript type quality. |
| **backend** | `repo-configs/backend/` | Java/Python backends. API design, error handling hierarchy, security standards, database practices, logging standards. |

Copy a repo configuration into any project:

```bash
cp /path/to/claude-devkit/repo-configs/design-system/CLAUDE.md /path/to/your/project/
```

Edit the installed `CLAUDE.md` freely to match your project's needs.

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

### MCP Server Installation

MCP server configurations are defined in `claude.json` at the repo root using `${ENV_VAR}` placeholders. During installation, the devkit:

1. Resolves placeholders using your shell environment variables (via `envsubst`)
2. Merges the resolved servers into `~/.claude.json` (Claude Code's internal config)
3. Preserves all existing keys and non-managed MCP servers in `~/.claude.json`

Uninstalling removes only the devkit-managed servers.

> **Note**: MCP server management requires either the `install.zsh` flow (developer setup) or the [`SETUP.md`](./SETUP.md) guided setup. The `/plugin install` command alone installs skills/agents/guidelines but does not configure MCP servers.

### Tool Routing

Claude automatically routes to the correct MCP server based on context:
- Confluence URLs (`*.atlassian.net/wiki/*`) -> `atlassian-confluence` MCP
- Bitbucket URLs (`bitbucket.org/*`) -> `bitbucket` MCP
- Google Docs/Sheets/Slides URLs -> `google-drive` MCP
- Slack operations -> `claude_ai_Slack` MCP
- Email operations -> `claude_ai_Gmail` MCP
- Calendar operations -> `claude_ai_Google_Calendar` MCP

Detailed routing rules are in [`settings/mcp-instructions.md`](settings/mcp-instructions.md).

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

## Prerequisites

claude-devkit is designed for macOS and expects specific tools to be installed. These are managed via the [dot-files](https://github.com/sujeet-pro/dot-files) Ansible setup.

> **Note**: The `/plugin install` method works without most of these tools. Full prerequisites are only needed for the developer setup (`zsh install.zsh`) or for skills that use specific CLI tools (e.g., `mmdc` for diagram rendering).

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

### Environment Variables

Add these to `~/.zshenv` based on which MCP integrations you use (see `dot-files/configs/shell/.zshenv.example`):

```bash
# Bitbucket MCP (for Bitbucket PR reviews)
export BITBUCKET_TOKEN="your-bitbucket-api-token"

# Confluence MCP (for Confluence operations)
export CONFLUENCE_URL="https://yoursite.atlassian.net/wiki"
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-atlassian-api-token"

# Google Drive MCP (run scripts/setup-google-drive.zsh after setting these)
export GOOGLE_MCP_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_MCP_CLIENT_SECRET="GOCSPX-your-secret"
export GOOGLE_DRIVE_OAUTH_CREDENTIALS="$HOME/.config/google-drive-mcp/gcp-oauth.keys.json"
```

All environment variables are optional. Only set the ones for services you use. Skills gracefully degrade when MCP servers are unavailable.

**OAuth-based services** (no env vars needed):
- **Google Drive MCP**: Run `scripts/setup-google-drive.zsh` to generate credentials and complete browser OAuth
- **Slack / Gmail / Calendar**: Claude.ai built-in integrations, connect via Claude Desktop -> Settings -> Integrations

### Verify Setup

```bash
# Check all prerequisites
zsh scripts/check-prerequisites.zsh

# Check environment variables
zsh scripts/check-env.zsh

# Validate MCP server configurations
zsh scripts/validate-mcp.zsh

# Test actual MCP connectivity (inside Claude Code)
/validate-mcp
```

## Developer Setup

For contributors who want to edit devkit files and see changes immediately:

```bash
# Clone to your preferred location
git clone https://github.com/sujeet-pro/claude-devkit.git ~/personal/claude-devkit

# Install (creates symlinks + merges MCP servers + configures context instructions)
cd ~/personal/claude-devkit
zsh install.zsh
```

Symlinks point from `~/.claude/` back to the repo. Any file you edit is immediately reflected in Claude Code sessions — no rebuild or re-install needed. MCP servers from `claude.json` are resolved and merged into `~/.claude.json`. Context instructions from `settings/base-settings.json` are merged into `~/.claude/settings.json`.

Skills installed via `/plugin` coexist with symlinked devkit items.

To verify:

```bash
ls -la ~/.claude/skills/
ls -la ~/.claude/agents/
ls -la ~/.claude/guidelines/
cat ~/.claude.json | jq '.mcpServers | keys'
```

## Selective Plugin Install

> **Recommended**: Use `devkit-full` instead. Individual skill installation works but comes with caveats.

If you want only specific skills, you can install them individually:

```bash
/plugin marketplace add sujeet-pro/claude-devkit
/plugin install pr-review@claude-devkit
```

### Available Plugins

| Plugin | Slash Command | Description |
|--------|---------------|-------------|
| `devkit-full` | (all skills) | **Recommended.** Full devkit: all skills, agents, and guidelines. |
| `devkit-guidelines` | — | Coding and document review guidelines only. |
| `devkit-agents` | — | Agent definitions only. |
| `pr-review` | `/pr-review` | Multi-agent PR code review. |
| `pr-describe` | `/pr-describe` | Generate and post PR descriptions. |
| `self-review` | `/self-review` | Iterative self-review with lint/test/build. |
| `blog` | `/blog` | Blog post writing, review, and update. |
| `article` | `/article` | Deep technical articles. |
| `project-docs` | `/project-docs` | Project documentation from codebase. |
| `doc-write` | `/doc-write` | General-purpose document writer. |
| `doc-review` | `/doc-review` | Multi-agent document review. |
| `review` | `/review` | Auto-detect PR or document review. |
| `diagram` | `/diagram` | Mermaid or Excalidraw diagrams. |
| `research` | `/research` | Web research with citations (standard depth). |
| `deep-research` | `/deep-research` | Exhaustive research (alias for /research --depth=exhaustive). |
| `search` | `/search` | Quick lightweight research using Sonnet. |
| `slack-compose` | `/slack-compose` | Slack message composition. |
| `frontend-design` | `/frontend-design` | 5 UI design variations. |
| `create-skill` | `/create-skill` | Create new devkit skills. |
| `confluence-publish` | `/confluence-publish` | Publish markdown to Confluence. |
| `validate-mcp` | `/validate-mcp` | Test MCP server connections. |
| `multi` | `/multi` | Multi-model mode for any task. |

### Caveats of Selective Install

1. **Missing dependencies** — Most skills depend on `devkit-guidelines` and `devkit-agents`. Without them, skills still work but with reduced quality: guideline checks fall back to general best practices, and agent delegation gracefully degrades.

2. **No MCP server configuration** — `/plugin install` copies skill files only. It does NOT configure MCP servers in `~/.claude.json`. For MCP setup, use the [`SETUP.md`](./SETUP.md) guided flow or configure manually (see [MCP Integrations](#mcp-integrations)).

3. **No context instructions** — The full install via `zsh install.zsh` merges capability routing instructions into `~/.claude/settings.json`, which helps Claude automatically select the right skill for any task. Plugin install does not include these — Claude may not auto-suggest skills as effectively.

4. **No auto-updates** — Plugin-installed skills are static copies. To update, run `/plugin update <plugin>@claude-devkit`.

5. **Sub-skill dependencies** — Some skills depend on other skills. For example, `/diagram` delegates to `/mermaid` or `/excalidraw`; `/article` delegates to `/research` and `/diagram`. Installing a skill without its sub-skill dependencies may cause those delegations to fail silently.

**If in doubt, install `devkit-full`.** It's the simplest path and ensures everything works together.

## Updating

### Plugin install

```bash
/plugin update devkit-full@claude-devkit
```

### Symlink install

After pulling changes or editing local files, re-run the installer:

```bash
cd /path/to/claude-devkit
git pull               # optional — get latest from remote
zsh install.zsh           # re-links skills + reconfigures MCP from current env vars
```

Also re-run `zsh install.zsh` after updating environment variables (e.g. rotated tokens in `~/.zshenv`).

## Uninstalling

### Plugin install

```bash
/plugin uninstall devkit-full@claude-devkit
```

### Symlink install

```bash
zsh /path/to/claude-devkit/uninstall.zsh
```

Removes symlinks from `~/.claude/` and managed MCP servers from `~/.claude.json`. Skills installed via `/plugin` are not affected. For non-interactive uninstall:

```bash
zsh /path/to/claude-devkit/uninstall.zsh --yes
```

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
zsh install.zsh --list
```

## Contributing

### Project Structure

```
claude-devkit/
├── .claude-plugin/         # Plugin marketplace manifest
│   └── marketplace.json
├── claude.json             # MCP server template (merged into ~/.claude.json)
├── install.zsh              # Idempotent installer: symlinks + MCP config (for contributors)
├── uninstall.zsh            # Removes symlinks + MCP servers
├── SETUP.md                # Auto-install instructions (for Claude Code to follow)
├── CLAUDE.md               # Instructions for devkit contributors
├── skills/                 # Skill definitions (each in its own directory)
│   └── <skill-name>/
│       └── SKILL.md
├── agents/                 # Agent definitions (markdown files)
│   └── <agent-name>.md
├── guidelines/             # Guideline documents (organized by category)
│   ├── coding/             # Code review guidelines
│   └── document/           # Document review guidelines
├── settings/               # Settings and capability routing
│   ├── base-settings.json  # Context instructions (merged into settings.json)
│   └── mcp-instructions.md # Skill, agent, and MCP routing reference
├── profiles/               # Repo type detection
│   ├── detect.md
│   └── README.md
└── repo-configs/           # Per-repo CLAUDE.md templates
    ├── default/CLAUDE.md
    ├── design-system/CLAUDE.md
    ├── frontend-nextjs/CLAUDE.md
    ├── library/CLAUDE.md
    └── backend/CLAUDE.md
```

### Adding a New Skill

1. Create a directory: `skills/my-skill/`
2. Add `SKILL.md` with frontmatter (name, description, arguments) and workflow instructions
3. Ensure the skill delegates to agents via the Agent tool (Agentic Teams pattern)
4. Add the skill to `.claude-plugin/marketplace.json` if it should be installable individually
5. Test: `zsh install.zsh`, then invoke `/my-skill` in Claude Code

### Adding a New Agent

1. Create a file: `agents/my-agent.md`
2. Include frontmatter (name, description, model, tools) and system instructions
3. Test: `zsh install.zsh`, then verify the agent is available

### Adding a New Guideline

1. Determine the category: `guidelines/coding/` or `guidelines/document/`
2. Create a new markdown file in the appropriate directory
3. Follow existing guideline structure: numbered sections, actionable rules, review checklist
4. Update `profiles/detect.md` if the guideline should be auto-loaded for a repo type
5. Update the relevant skill's guideline loading table if needed

### Conventions

- Skills use `SKILL.md` format inside a named directory under `skills/`
- Agents are single `.md` files under `agents/`
- Guidelines are `.md` files organized under `guidelines/coding/` and `guidelines/document/`
- Settings files go under `settings/`
- All markdown files use ATX-style headers (`#`, `##`, etc.)
- Shell scripts start with `#!/usr/bin/env zsh` and use `set -euo pipefail`
- Scripts must work on both macOS (darwin) and Linux
- All skills delegate to agents via the Agent tool (Agentic Teams pattern)

### Testing Your Changes

```bash
# Install (creates symlinks)
zsh install.zsh

# Open a real project and verify skills/agents/guidelines work
# Test uninstall
zsh uninstall.zsh
```

---

## License

See [LICENSE](./LICENSE) for details.
