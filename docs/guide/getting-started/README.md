---
title: Getting Started
description: Install ADK and run your first skill
order: 1
---

# Getting Started

ADK (Agent Development Kit) is a Claude plugin that provides principal-engineer-grade skills for software development agents. It covers code review, documentation, research, diagrams, audits, planning, and more.

## Installation

### Claude Code (Recommended)

```bash
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@adk-marketplace
```

All skills become available as `/adk:<skill-name>` immediately. Run `/reload-plugins` if you've just installed.

### skills.sh

```bash
npx skills add sujeet-pro/agents-devkit
```

This installs all 27 skills. To install specific skills:

```bash
npx skills add sujeet-pro/agents-devkit/skills/code-review-pr
npx skills add sujeet-pro/agents-devkit/skills/dev-build
```

### Local Development

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
claude --plugin-dir ~/.devkit
```

## Your First Skill

The easiest way to start is through the orchestrator:

```text
/adk:use review this codebase for architecture and code quality
```

The `/adk:use` orchestrator will:

1. **Expand your intent** — clarify what "review" means, identify the scope
2. **Identify the right skills** — routes to `/adk:code-review-repo` for full-codebase review
3. **Confirm the plan** — shows you what it will do before starting
4. **Execute** — runs the review with parallel child agents
5. **Validate** — produces a prioritized improvement plan

## Direct Skill Invocation

You can also invoke skills directly when you know which one you need:

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

## Setup (Optional)

Run the setup skill to install optional tools and configure MCP servers:

```text
/adk:setup
```

This checks for and installs: git, node, npm, diagramkit (for diagram rendering), and configures GitHub MCP for PR operations.

## What's Next?

- **[Skills Overview](/guide/skills/)** — browse all 27 skills by category
- **[Workflow](/guide/workflow/)** — understand the 6-phase workflow
- **[Skill Reference](/reference/skills/)** — detailed documentation for each skill
