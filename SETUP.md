# DevKit Setup For Claude Code

Use this file when you want Claude Code to install the full DevKit pack for the user.

## Recommended Path

1. Register the repo as a Claude marketplace:

   ```bash
   /plugin marketplace add sujeet-pro/agents-devkit
   ```

2. Install the full plugin:

   ```bash
   /plugin install devkit@devkit-marketplace
   ```

3. If the user also wants local helper scripts, MCP setup, and live-edit symlinks, run:

   ```bash
   zsh install.zsh
   ```

   Or in copy mode (no symlinks):

   ```bash
   zsh install.zsh --copy
   ```

## Dependency Validation

Before configuring integrations, run:

```bash
zsh scripts/check-prerequisites.zsh
zsh scripts/check-env.zsh
```

If the user wants a specific workflow checked, run:

```bash
zsh scripts/check-skill-deps.zsh <skill-name>
```

## MCP Setup

DevKit's core MCP workflows are GitHub, Bitbucket, Confluence, and Google Drive.

Typical flow:

1. Ensure required env vars are set in `~/.zshenv`.
2. Configure the MCP entries described in `settings/mcp-setup.md`.
3. Verify with:

   ```bash
   zsh scripts/validate-mcp.zsh
   ```

4. Inside Claude Code, validate connectivity with:

   ```text
   /devkit:manage-validate
   ```

## Update

To update DevKit after installation:

```text
/devkit:manage-update
```

Or standalone: `zsh scripts/update-devkit.zsh`

## Notes

- The plugin install brings in the full skill pack.
- The local installer is mainly for contributor-style setups and MCP configuration.
- The active DevKit catalog covers reviews, docs, research, diagrams, and engineering workflows.
