# Installing DevKit For Codex

Enable DevKit in Codex via native skill discovery.

## Install

1. Clone the repo somewhere stable:

   ```bash
   git clone https://github.com/sujeet-pro/claude-devkit.git ~/.devkit
   ```

2. Expose the shared skills folder to Codex:

   ```bash
   mkdir -p ~/.agents/skills
   ln -s ~/.devkit/skills ~/.agents/skills/devkit
   ```

3. Restart Codex so it re-discovers skills.

## Verify

```bash
ls -la ~/.agents/skills/devkit
```

## Update

```bash
cd ~/.devkit && git pull
# Or use the update skill: /devkit:manage-update
```

## Remove

```bash
rm ~/.agents/skills/devkit
```
