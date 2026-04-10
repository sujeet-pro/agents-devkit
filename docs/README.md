---
title: Agent Development Kit
description: Principal-engineer-grade skills for software development agents
layout: DocHome
tagline: Skills that think like a principal engineer
actions:
  - text: Get Started
    link: /guide/getting-started/
    theme: brand
  - text: Use Cases
    link: /guide/code-reviews/
    theme: alt
features:
  - title: 52 Skills
    details: Code review, documentation, diagrams, research, audits, planning, migrations, refactoring — all composable.
  - title: Human-in-the-Loop
    details: Every non-trivial task follows a 6-phase workflow with approval gates. You stay in control.
  - title: Lazy Loading
    details: Only ~200-500 lines load per task out of ~42,000 total. Each skill loads only the relevant stage and reference files.
  - title: Principal Engineer Lens
    details: Before committing to significant work, skills challenge the approach — do we need this? What's simplest?
  - title: Self-Contained
    details: Each skill works independently with inline fallbacks. Skills invoke other skills by name, never by file reference.
  - title: MCP-Native
    details: Built-in integrations with GitHub, Bitbucket, Confluence, and Jira via MCP.
---

## Install

### Claude Code (Recommended)

```bash
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@adk-marketplace
```

Update with `/plugin update adk`.

### skills.sh (Claude / Codex)

```bash
npx skills add sujeet-pro/agents-devkit
```

Works with Claude Code, Codex, and other [skills.sh](https://skills.sh)-compatible agents. Skills are invoked as `/<skill-name>`.

## Use

Route any prompt through the orchestrator:

```text
/adk:use review this PR for security issues
```

Or invoke a skill directly:

```text
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:dev-build implement user authentication with OAuth2
/adk:diagram-mermaid auth flow sequence diagram
```

Every skill supports `--help` and `--auto` (skip confirmations).
