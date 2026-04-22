# `setup` — examples

## First-run on a fresh Mac

```
/adk:setup
```

Sees: brew missing → prompt → user installs → continue. gh / jq / fd / ripgrep / fzf / node missing → install each (gated). claude already installed. `gh auth status` not authed → tells user to run `gh auth login`. `~/.zshenv` has GITHUB_PAT but no DD_API_KEY. Surface missing var. MCP installer enables `github` only (datadog skipped). Doctor: 1 warning. Report printed.

## Repeat run after adding env var

```
/adk:setup --target mcp --auto
```

Skips CLI checks (target = mcp). Reads `.mcp.json`. Sees DD_API_KEY now present. Enables datadog MCP. Doctor: 0 warnings. Done.

## CI provisioning

```
/adk:setup --mode fix --auto --target cli
```

In `--mode fix --auto` it installs every missing CLI tool without asking. Skips MCP entirely (CI doesn't have user creds in `~/.zshenv`).
