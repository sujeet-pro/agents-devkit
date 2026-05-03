---
title: adk Marketplace
description: Principal Engineer workflow plugins for Claude Code and Claude Desktop.
layout: home
tagline: Focused Claude plugins for coding, reviewing, docs, and production investigations.
install:
  lang: text
  title: Claude Code
  frame: terminal
  code: |
    /plugin marketplace add sujeet-pro/agents-devkit
    /plugin install adk-core@adk
    /plugin install adk-code@adk
    /plugin install adk-review@adk
    /plugin install adk-docs@adk
    /plugin install adk-investigate@adk
    /adk-core:setup
actions:
  - text: Install
    link: /guide/getting-started/installation/
    theme: brand
  - text: Philosophy
    link: /guide/philosophy/
    theme: alt
features:
  - title: Five focused plugins
    details: adk-core provides shared contracts and setup. adk-code, adk-review, adk-docs, and adk-investigate add focused skill packs around the main Principal Engineer workflows.
  - title: Dependency-aware skills
    details: Every non-trivial skill starts with a preflight that separates required-now dependencies from optional capabilities, then reports skipped checks and residual risk.
  - title: Pagesmith-native docs
    details: The docs site uses @pagesmith/docs conventions for home-page feature cards, guide/reference sections, series metadata, Pagefind search, and schema-backed frontmatter.
  - title: Plugin/type reference groups
    details: Generated reference pages are grouped as core-skills, code-agents, review-mcp, docs-plugins, and other plugin/component pairs so readers can scan by capability.
  - title: Claude Code and Desktop ready
    details: Claude Code can load plugin .mcp.json files. Claude Desktop cannot, so skills tell the user which connector or custom MCP to configure before continuing.
  - title: Generated reference
    details: Reference pages are generated from the marketplace source so every skill, agent, plugin, MCP server, and helper binary has a matching markdown page.
---

## Install

`adk` is a Claude Code marketplace. Register the marketplace, install the
plugins you need, reload, then run setup:

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk-core@adk
/plugin install adk-code@adk
/plugin install adk-review@adk
/plugin install adk-docs@adk
/plugin install adk-investigate@adk
/reload-plugins
/adk-core:setup
```

See the full [Installation](./guide/getting-started/installation.md) guide for
local clone, SSH, HTTPS, update, verification, and uninstall paths.

## What This Site Covers

`adk` is a Claude plugin marketplace for a Principal Engineer workflow: code writing, code review, documentation, and production investigations.

The reference section is generated from the repository source. To update it after editing a skill, agent, plugin manifest, MCP config, or helper binary, run:

```bash
npm run docs:reference
```

For local development:

```bash
npm install
npm run docs:dev
```

## New here? Read in this order

1. **[Philosophy](./guide/philosophy.md)** — the operating principles behind every plugin and skill.
2. **[Installation](./guide/getting-started/installation.md)** — add the Claude marketplace and install plugins.
3. **[Getting Started](./guide/getting-started/)** — shortest setup and validation path.
4. **[Claude Code and Desktop](./guide/usage/desktop-and-cli.md)** — host differences and MCP preflight behavior.
5. **[Reference](./reference/)** — generated pages grouped by plugin and component type.
