---
title: Getting Started
description: Install ADK on your machine, run the setup skill, and execute your first /adk:auto task.
order: 0
---

# Getting Started

ADK is a Claude Code plugin first, but reaches Cursor, Codex, Gemini, and Antigravity through a parallel `agents-skills/adk-<name>` symlink farm. This section walks you through choosing an install path, finishing setup, and running your first skill.

## Pages in order

1. **[Installation](./installation.md)** — Pick one of four install paths (Claude plugin, npm, clone, npx skills) and finish with `/adk:setup` (or `npx adk`) to register MCP servers and wire your user memory.
2. **[First skill](./first-skill.md)** — Run `/adk:auto` (or `adk-auto`) on a real task and see the four-phase requirements → scoping → dispatch → aggregate flow.

## TL;DR

```text
# In Claude Code:
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@sujeet-pro-adk
/reload-plugins
/adk:setup
```

```bash
# Or from any shell, with no Claude:
npx --yes agents-devkit adk
```

```bash
# Or contributing to ADK itself:
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
node bin/adk-setup
```
