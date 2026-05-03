---
title: 'adk-code'
description: 'adk code-authoring plugin: write features, fix bugs (with reproducer + regression test first), refactor without behavior change, migrate frameworks, write/expand tests, diagnose perf, design APIs, harden security. One skill per verb. All skills follow the universal --auto / -i mode contract.'
plugin: 'adk-code'
source: 'plugins/adk-code/.claude-plugin/plugin.json'
group: 'Plugins'
order: 1500
---
# adk-code

adk code-authoring plugin: write features, fix bugs (with reproducer + regression test first), refactor without behavior change, migrate frameworks, write/expand tests, diagnose perf, design APIs, harden security. One skill per verb. All skills follow the universal --auto / -i mode contract.

## Source

`plugins/adk-code/.claude-plugin/plugin.json`

## Dependencies

- `adk-core` ^2.0.0

## Skills

- [`code-api`](../skills/adk-code-code-api.md)
- [`code-bugfix`](../skills/adk-code-code-bugfix.md)
- [`code-migrate`](../skills/adk-code-code-migrate.md)
- [`code-perf`](../skills/adk-code-code-perf.md)
- [`code-refactor`](../skills/adk-code-code-refactor.md)
- [`code-security`](../skills/adk-code-code-security.md)
- [`code-test`](../skills/adk-code-code-test.md)
- [`code-write`](../skills/adk-code-code-write.md)

## Agents

- [`implementer`](../agents/adk-code-implementer.md)
- [`test-engineer`](../agents/adk-code-test-engineer.md)

## Helper Binaries

No helper binaries.
