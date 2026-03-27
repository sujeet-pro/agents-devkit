---
name: manage-setup
description: Use to check, validate, and install all CLI tools, packages, and MCP servers needed by DevKit skills — idempotent, safe to run repeatedly
user_invocable: true
arguments:
  - name: no-auto-install
    description: "When set, only report missing tools without installing (default: false — auto-install is ON)"
    required: false
  - name: refresh-mcp
    description: "Re-read ~/.zshenv and refresh MCP server configuration from current env vars (default: false)"
    required: false
---

# DevKit Setup

Use `skills/_references/preflight-validations.md`.

## Overview

Checks all CLI tools, npm packages, runtime managers, and MCP server connections needed by DevKit skills. By default, auto-installs missing required tools. This skill is **idempotent** — safe to run any number of times. Each run re-checks everything from scratch.

On start, log:

```
DevKit Setup (auto-install: ON)
To run without auto-install: /devkit:manage-setup no-auto-install=true
```

## Flow

### 1. Check CLI Tools

Check availability and version for each tool. Report whether a better alternative is available.

#### Required

| Tool | Purpose | Install |
|------|---------|---------|
| `node` | JavaScript runtime | `brew install node` |
| `npm` | Package manager | ships with node |
| `git` | Version control | `brew install git` |
| `gh` | GitHub CLI | `brew install gh` |
| `jq` | JSON processor | `brew install jq` |
| `rg` | Fast search (ripgrep) | `brew install ripgrep` |
| `envsubst` | Template variable substitution | `brew install gettext` |

#### Recommended

| Tool | Purpose | Replaces | Install |
|------|---------|----------|---------|
| `fd` | Fast file finder | `find` | `brew install fd` |
| `bat` | Syntax-highlighted cat | `cat` | `brew install bat` |
| `eza` | Modern ls | `ls` | `brew install eza` |
| `delta` | Syntax-highlighted diff | `diff` | `brew install git-delta` |
| `fzf` | Fuzzy finder | -- | `brew install fzf` |
| `sd` | Simple find-and-replace | `sed` | `brew install sd` |
| `yq` | YAML processor | -- | `brew install yq` |
| `tokei` | Code statistics | -- | `brew install tokei` |
| `tree` | Directory tree | -- | `brew install tree` |
| `shellcheck` | Shell script linter | -- | `brew install shellcheck` |
| `trivy` | Security scanner | -- | `brew install trivy` |
| `gitleaks` | Secret scanner | -- | `brew install gitleaks` |
| `actionlint` | GitHub Actions linter | -- | `brew install actionlint` |
| `lazygit` | Terminal git UI | -- | `brew install lazygit` |
| `watchexec` | File watcher | -- | `brew install watchexec` |
| `pre-commit` | Git hook manager | -- | `brew install pre-commit` |

### 2. Check Global npm Packages

#### Required

| Package | Purpose | Install |
|---------|---------|---------|
| `diagramkit` | Diagram rendering | `npm install -g diagramkit` |
| `@mermaid-js/mermaid-cli` | Mermaid diagrams | `npm install -g @mermaid-js/mermaid-cli` |
| `excalidraw-cli` | Excalidraw rendering | `npm install -g excalidraw-cli` |

#### Recommended

| Package | Purpose | Install |
|---------|---------|---------|
| `npm-check-updates` | Dependency updates | `npm install -g npm-check-updates` |
| `vite-plus` | Dev server | `npm install -g vite-plus` |

### 3. Check Runtime Managers

Check for Node.js version managers in preference order:

1. `mise` (preferred -- manages multiple runtimes)
2. `nvm`
3. `fnm`

Report which is available and whether the active Node.js version matches the project's `.node-version` or `.nvmrc` if present.

### 4. Validate MCP Connections

Check `~/.claude.json` for configured MCP servers and validate:

- GitHub MCP -- required for PR workflows
- Bitbucket MCP -- if configured
- Confluence MCP -- if configured
- Google Drive MCP -- if configured

Report connectivity status for each configured server.

### 5. Check Environment Variables

Check whether required MCP environment variables are set. Read from current shell environment and `~/.zshenv`:

| Variable | Purpose | Required For |
|----------|---------|-------------|
| `CONFLUENCE_URL` | Confluence base URL | Confluence MCP |
| `CONFLUENCE_USERNAME` | Confluence user | Confluence MCP |
| `CONFLUENCE_API_TOKEN` | Confluence token | Confluence MCP |
| `BITBUCKET_URL` | Bitbucket base URL | Bitbucket MCP |
| `BITBUCKET_USERNAME` | Bitbucket user | Bitbucket MCP |
| `BITBUCKET_WORKSPACE` | Bitbucket workspace | Bitbucket MCP |
| `BITBUCKET_TOKEN` | Bitbucket token | Bitbucket MCP |
| `GOOGLE_DRIVE_OAUTH_CREDENTIALS` | Google Drive OAuth | Google Drive MCP |

For any missing environment variables that are needed by configured MCP servers:
- Report which variables are missing and which MCP server needs them
- Ask the user to add them to `~/.zshenv` and then run `/devkit:manage-setup refresh-mcp=true`

### 6. Results Report

Present a combined results table:

```
## DevKit Setup Report

### CLI Tools
| Tool | Status | Version | Category | Action Needed |
|------|--------|---------|----------|---------------|
| node | OK | v24.14.0 | required | -- |
| fd | MISSING | -- | recommended | brew install fd |
...

### npm Packages
| Package | Status | Version | Category | Action Needed |
|---------|--------|---------|----------|---------------|
| diagramkit | OK | 1.2.0 | required | -- |
...

### Runtime Managers
| Manager | Status | Version |
|---------|--------|---------|
| mise | OK | 2026.3.13 |
...

### MCP Servers
| Server | Status | Notes |
|--------|--------|-------|
| GitHub | OK | authenticated |
...

### Environment Variables
| Variable | Status | Used By |
|----------|--------|---------|
| CONFLUENCE_URL | OK | Confluence MCP |
| BITBUCKET_TOKEN | MISSING | Bitbucket MCP |
...
```

### 7. Auto-Install (default behavior)

Unless `no-auto-install=true` is passed:

1. Log: `Auto-installing missing required tools...`
2. Install missing **required** CLI tools via `brew install <tool>`
3. Install missing **required** npm packages via `npm install -g <package>`
4. Show progress for each installation in real time
5. After installations, run `diagramkit warmup` to verify diagram rendering
6. Re-run the results report to confirm everything is resolved
7. Do NOT auto-install recommended tools — report them as suggestions only

When `no-auto-install=true`:
- Only report missing tools, do not install anything
- Log: `Setup check complete (auto-install: OFF). To install missing tools, run: /devkit:manage-setup`

### 8. MCP Configuration Refresh (when `refresh-mcp=true`)

When the user has updated environment variables in `~/.zshenv`:

1. Log: `Refreshing MCP configuration from ~/.zshenv...`
2. Read the DevKit `claude.json` template
3. Resolve environment variables using `envsubst`
4. Update MCP server entries in `~/.claude.json`
5. Log which servers were reconfigured and what changed
6. Validate connectivity for each reconfigured server
7. If any env vars are still missing, list them and ask the user to add them

This is useful when:
- API tokens have been rotated
- A new MCP server was added in the update
- The user wants to reconfigure without re-running the full installer

### 9. Post-Install Verification

After everything (whether auto-installed or already present):

1. Run `diagramkit warmup` to ensure diagram rendering pipeline works
2. Run MCP preflight checks
3. Log final summary: `Setup complete. N required tools OK, N MCP servers configured.`

## Adjacent Skills

- `/devkit:manage-validate` for MCP-only validation
- `/devkit:manage-update` for updating DevKit itself (calls this skill after update)
