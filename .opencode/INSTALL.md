# Installing DevKit For OpenCode

Add DevKit as a git-backed plugin in `opencode.json`:

```json
{
  "plugin": ["devkit@git+https://github.com/sujeet-pro/agents-devkit.git"]
}
```

Restart OpenCode after updating the config.

The included plugin bridge injects the DevKit bootstrap skill and registers the shared `skills/` directory so OpenCode can discover the full pack.

## Update

Restart OpenCode to pull the latest version, or run `/devkit:manage-update` from within a session.
