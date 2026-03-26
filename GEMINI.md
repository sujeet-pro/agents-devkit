# DevKit For Gemini

You have access to the DevKit skill pack from this repository.

## Startup Rules

1. Consider whether `/devkit:use` or another DevKit skill applies before responding.
2. Prefer skills whose descriptions match the user's triggering conditions.
3. Map Claude-style tool references in skills to Gemini equivalents:
   - `Skill` -> Gemini skill activation
   - `Task` / agent delegation -> Gemini subagents
   - `Bash`, `Read`, `Write`, `Edit` -> Gemini CLI native tools
4. When a skill depends on local CLIs or MCP setup, validate with `scripts/check-skill-deps.zsh <skill-name>` if the repo is available locally.
5. Intermediary artifacts (plans, drafts, research notes) go in `.temp/` directory.

## Update

Re-run the install command to pull the latest version:

```bash
gemini extensions install https://github.com/sujeet-pro/agents-devkit
```
