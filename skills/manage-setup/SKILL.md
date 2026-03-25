---
name: manage-setup
description: Use to check, report on, and optionally install all CLI tools and packages needed by DevKit skills
user_invocable: true
arguments:
  - name: fix
    description: "When true, auto-install missing tools via brew and npm (default: false)"
    required: false
---

# DevKit Setup

Use `skills/_references/preflight-validations.md`.

## Overview

Checks all CLI tools, npm packages, runtime managers, and MCP server connections needed by DevKit skills. Reports results in a table and optionally installs missing dependencies.

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

Delegate to `/devkit:manage-validate` patterns for:

- GitHub MCP -- required for PR workflows
- Bitbucket MCP -- if configured
- Confluence MCP -- if configured
- Google Drive MCP -- if configured

Report connectivity status for each configured server.

### 5. Results Report

Present a combined results table:

```
## DevKit Setup Report

### CLI Tools
| Tool | Status | Version | Category | Action Needed |
|------|--------|---------|----------|---------------|
| node | OK | v20.11.0 | required | -- |
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
| mise | OK | 2024.1.0 |
...

### MCP Servers
| Server | Status | Notes |
|--------|--------|-------|
| GitHub | OK | authenticated |
...

### Tool Upgrade Recommendations
| Default | Better Alternative | Benefit |
|---------|--------------------|---------|
| find | fd | Faster, simpler syntax, respects .gitignore |
| grep | rg | Faster, respects .gitignore |
| cat | bat | Syntax highlighting, line numbers |
| ls | eza | Better formatting, git integration |
| diff | delta | Syntax highlighting, side-by-side view |
| sed | sd | Simpler regex syntax |
```

### 6. Auto-Install (when `fix=true`)

<HARD-GATE>
Do not install anything unless `fix=true` is explicitly set.
</HARD-GATE>

When `fix=true`:

1. Install missing **required** CLI tools via `brew install <tool>`
2. Install missing **required** npm packages via `npm install -g <package>`
3. Show progress for each installation
4. After all installations, run `diagramkit warmup` to verify diagram rendering
5. Run preflight validation for all configured MCPs
6. Re-run the results report to confirm everything is resolved

Do not auto-install recommended tools. Report them as suggestions only.

### 7. Post-Install Verification

After installation (or when all tools are already present):

1. Run `diagramkit warmup` to ensure diagram rendering pipeline works
2. Run MCP preflight checks via `zsh scripts/check-skill-deps.zsh manage-validate`

## Adjacent Skills

- `/devkit:manage-validate` for MCP-only validation
- `/devkit:manage-update` for updating DevKit itself
