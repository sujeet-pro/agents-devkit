---
title: Getting Started
description: Install ADK and run your first skill
order: 1
---

# Getting Started

ADK (Agent Development Kit) is a Claude plugin that provides principal-engineer-grade skills for software development agents. 49 skills covering code review, documentation, research, diagrams, audits, planning, migrations, refactoring, and more.

## Installation

### Claude Code (Recommended)

```bash
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@adk-marketplace
```

Skills become available as `/adk:<skill-name>` immediately.

### skills.sh (Claude / Codex)

```bash
npx skills add sujeet-pro/agents-devkit
```

To install specific skills:

```bash
npx skills add sujeet-pro/agents-devkit/skills/code-review-pr
npx skills add sujeet-pro/agents-devkit/skills/dev-build
```

When installed via skills.sh, skills are prefixed with `adk-` (e.g., `/adk-code-review-pr`, `/adk-dev-build`). Works with Claude Code, Codex, and other skills.sh-compatible agents. Visit [skills.sh](https://skills.sh) for more details.

### Local Development

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
claude --plugin-dir ~/.devkit
```

## Your First Skill

The easiest way to start is through the `/adk:use` orchestrator:

```text
/adk:use review this codebase for architecture and code quality
```

This will:

1. **Expand your intent** — clarify what "review" means, identify the scope
2. **Identify the right skills** — routes to `/adk:code-review-repo` for full-codebase review
3. **Confirm the plan** — shows you what it will do before starting
4. **Execute** — runs the review with parallel child agents
5. **Validate** — produces a prioritized improvement plan

## Direct Skill Invocation

When you know which skill you need, invoke it directly:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:dev-build implement user authentication with OAuth2
/adk:diagram --engine mermaid auth flow sequence diagram
/adk:docs-write --type adr caching strategy decision
```

Every skill supports `--help` to see all parameters:

```text
/adk:code-review-pr --help
/adk:dev-build --help
```

## Auto Mode

By default, skills pause for your approval at key decision points. Pass `--auto` to skip confirmations:

```text
/adk:use --auto fix the failing tests and update the docs
```

## Recommended System Prompt

After installing, add this to your project's `CLAUDE.md` (or `~/.claude/CLAUDE.md` for global use) to enable skill-first routing on every prompt:

```markdown
## ADK Skill Routing

On every user prompt, follow this workflow before doing any work:

1. **Expand intent** — restate the goal in one line, surface assumptions, estimate complexity
2. **Identify skills** — check installed ADK skills (`/adk:use` or `/adk-use`) and select the minimum pipeline
3. **Show phase summary** — display a concise phase plan:
   - Goal (one line)
   - Skills to use (with brief rationale)
   - Phases that will run (based on complexity)
   - Complexity level (Trivial/Small/Medium/Large)
4. **Confirm with user** — wait for approval before executing (unless `--auto`)
5. **Execute with concise output** — lead with conclusions, offer to elaborate
6. **Validate** — verify the result, self-review, simplify if possible

Output is concise by default. After completing a task, show the short summary and ask:
"Need a detailed breakdown?" — only elaborate when the user says yes.
```

Run `/adk:setup --type config` to apply this automatically.

## Setup (Optional)

Run the setup skill to install optional tools and configure MCP servers:

```text
/adk:setup
```

This checks for and installs: git, node, npm, diagramkit (for diagram rendering), and configures GitHub MCP for PR operations.

## Update

### Claude Code

```bash
/plugin update adk
```

### skills.sh

```bash
npx skills update sujeet-pro/agents-devkit
```

## Uninstall

### Claude Code

```bash
/plugin uninstall adk

# Remove the marketplace (optional)
/plugin marketplace remove adk-marketplace
```

### skills.sh

```bash
npx skills remove sujeet-pro/agents-devkit
```

## What's Next?

- **[Philosophy & Design](/guide/philosophy/)** — core principles, output style, lazy loading
- **[Skills Overview](/guide/skills/)** — browse all 49 skills by category
- **[Workflow](/guide/workflow/)** — understand the 6-phase workflow
- **[Skill Reference](/reference/skills/)** — detailed documentation for each skill
