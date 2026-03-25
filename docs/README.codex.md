# DevKit for Codex

DevKit uses Codex native skill discovery.

## Quick Install

Tell Codex:

```text
Fetch and follow instructions from https://raw.githubusercontent.com/sujeet-pro/agents-devkit/refs/heads/main/.codex/INSTALL.md
```

This clones the repo to `~/.devkit` and symlinks `skills/` into `~/.agents/skills/devkit`.

## Manual Install

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
mkdir -p ~/.agents/skills
ln -s ~/.devkit/skills ~/.agents/skills/devkit
```

Restart Codex so it re-discovers skills.

## Verify

```bash
ls -la ~/.agents/skills/devkit
```

## Update

```bash
cd ~/.devkit && git pull
```

## Remove

```bash
rm ~/.agents/skills/devkit
```
