---
title: 'adk-core'
description: 'adk universal baseline: prompt routing (auto), setup of ~/.config/adk/*.md, meta-info reader, mode contract, .temp/ layout, the universal Bash safety hook, and the canonical interaction contract. Required by every other adk plugin.'
plugin: 'adk-core'
source: 'plugins/adk-core/.claude-plugin/plugin.json'
group: 'Plugins'
order: 500
---
# adk-core

adk universal baseline: prompt routing (auto), setup of ~/.config/adk/*.md, meta-info reader, mode contract, .temp/ layout, the universal Bash safety hook, and the canonical interaction contract. Required by every other adk plugin.

## Source

`plugins/adk-core/.claude-plugin/plugin.json`

## Dependencies

None declared.

## Skills

- [`auto`](../skills/adk-core-auto.md)
- [`context-gather`](../skills/adk-core-context-gather.md)
- [`info`](../skills/adk-core-info.md)
- [`mode-contract`](../skills/adk-core-mode-contract.md)
- [`prompt-expand`](../skills/adk-core-prompt-expand.md)
- [`setup`](../skills/adk-core-setup.md)
- [`temp-folder`](../skills/adk-core-temp-folder.md)

## Agents

- [`context-gatherer`](../agents/adk-core-context-gatherer.md)
- [`dispatcher`](../agents/adk-core-dispatcher.md)
- [`prompt-expander`](../agents/adk-core-prompt-expander.md)

## Helper Binaries

- [`adk-info`](../bin/adk-core-adk-info.md)
- [`adk-mcp-health`](../bin/adk-core-adk-mcp-health.md)
- [`adk-task-slug`](../bin/adk-core-adk-task-slug.md)
