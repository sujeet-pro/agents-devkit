# DevKit for OpenCode

DevKit integrates with OpenCode via its git-backed plugin system.

## Install

Add DevKit to your `opencode.json`:

```json
{
  "plugin": ["devkit@git+https://github.com/sujeet-pro/agents-devkit.git"]
}
```

Restart OpenCode after updating the config.

The plugin bridge (`.opencode/plugins/akit.js`) registers the shared `skills/` directory and injects the DevKit bootstrap skill into each chat session.

## Update

Restart OpenCode to pull the latest version, or run `/devkit:manage-update` from within a session.

## Remove

Remove the `devkit@git+...` entry from `opencode.json` and restart OpenCode.
