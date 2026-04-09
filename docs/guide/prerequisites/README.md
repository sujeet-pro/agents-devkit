---
title: Prerequisites
description: Everything you need before using ADK skills — tools, API tokens, and MCP servers
order: 0
---

# Prerequisites

This guide walks you through everything you need to set up before using ADK skills. It covers macOS only — all tools are installed via [Homebrew](https://brew.sh).

Most of this setup is **one-time**. After the initial setup, you can run `/adk:setup` at any time to verify everything is working or install missing pieces.

## Quick Start (Automated)

If you already have Claude Code installed and ADK added as a plugin:

```text
/adk:setup
```

This will check every tool and MCP server listed below, install what's missing, and report what needs manual action (like API tokens). You can run it as many times as you want — it's idempotent.

**But first**, you need to set up your API tokens in `~/.zshenv` (see [Step 2](#step-2-api-tokens)) — the setup skill reads tokens from there.

---

## Step 1: Install Homebrew

Homebrew is the package manager for macOS. Open the **Terminal** app (search for "Terminal" in Spotlight) and paste:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the on-screen instructions. When it finishes, close and reopen Terminal.

To verify it worked:

```bash
brew --version
```

You should see something like `Homebrew 4.x.x`.

---

## Step 2: API Tokens

ADK skills connect to GitHub, Bitbucket, Confluence, and Google Drive. Each service needs API tokens stored in a file called `~/.zshenv` — a configuration file that your shell loads automatically.

### What is `~/.zshenv`?

It's a hidden file in your home folder that sets environment variables. These are name-value pairs that programs can read. Think of it as a secure place to store your API passwords so skills can use them without you typing them every time.

### Editing `~/.zshenv`

Open it in a text editor from Terminal:

```bash
open -e ~/.zshenv
```

If the file doesn't exist yet, create it:

```bash
touch ~/.zshenv
open -e ~/.zshenv
```

Add the lines below for each service you use. **Replace the placeholder values** with your actual tokens.

### GitHub (for PR reviews, issues, code operations)

```bash
export GITHUB_PAT="ghp_your_personal_access_token_here"
```

**How to get it:**

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens?type=beta)
2. Click **Generate new token** (Fine-grained token recommended)
3. Give it a name like "ADK"
4. Set expiration (90 days recommended; re-generate when it expires)
5. Select the repositories you want to access (or "All repositories")
6. Under **Repository permissions**, enable:
   - **Contents** — Read
   - **Pull requests** — Read and write
   - **Issues** — Read and write
   - **Metadata** — Read (auto-selected)
7. Click **Generate token** and copy it into `~/.zshenv`

This token is used by:
- The **GitHub MCP server** — the plugin's `.mcp.json` reads it via `${env:GITHUB_PAT}`
- The **`gh` CLI** — as a fallback (though `gh auth login` is preferred for CLI auth)
- **Direct API calls** — connector skill scripts that use `curl`

> **Also recommended:** Install the `gh` CLI (see [Step 3](#step-3-install-tools)) and run `gh auth login`. This provides browser-based OAuth authentication that works independently of the PAT, giving you a second auth path if the token expires.

### Bitbucket (for PR reviews, comments, repository access)

```bash
export BITBUCKET_USERNAME="your-bitbucket-username"
export BITBUCKET_TOKEN="your-app-password"
```

**How to get it:**

1. Go to [bitbucket.org/account/settings/app-passwords](https://bitbucket.org/account/settings/app-passwords/)
2. Click **Create app password**
3. Give it a label like "ADK"
4. Select permissions: **Repositories** (read), **Pull requests** (read, write)
5. Click **Create** and copy the password into `~/.zshenv`
6. Your username is your Bitbucket username (not email)

### Confluence (for documentation read/write, page comments)

```bash
export CONFLUENCE_URL="https://your-company.atlassian.net"
export CONFLUENCE_USERNAME="your-email@company.com"
export CONFLUENCE_API_TOKEN="your-api-token"
```

**How to get it:**

1. Go to [id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)
2. Click **Create API token**
3. Give it a label like "ADK"
4. Copy the token into `~/.zshenv`
5. Your URL is your Atlassian site URL (e.g., `https://mycompany.atlassian.net`)
6. Your username is the email you use to log in to Atlassian

### Google Drive (for document access — optional)

Google Drive requires OAuth credentials instead of a simple token.

```bash
export GOOGLE_DRIVE_OAUTH_CREDENTIALS="~/.config/google-drive-mcp/gcp-oauth.keys.json"
```

**How to get it:**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create a project (or select an existing one)
3. Enable the Google Drive API
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Select **Desktop app**, give it a name
6. Download the JSON file and save it to `~/.config/google-drive-mcp/gcp-oauth.keys.json`

### After editing `~/.zshenv`

Save the file and reload it in your current terminal:

```bash
source ~/.zshenv
```

Or simply close and reopen Terminal — it loads automatically on new sessions.

---

## Step 3: Install Tools

These are the command-line tools that ADK skills use. You can install them all at once, or let `/adk:setup` handle it.

### Required Tools

These are needed for core ADK functionality:

```bash
brew install git python node jq gh
```

| Tool | What it does |
|------|-------------|
| `git` | Version control — used by nearly every skill |
| `python` | Runs preflight checks and setup scripts |
| `node` | Runs diagram rendering and documentation tools |
| `jq` | Parses JSON responses from Bitbucket, Confluence, and Jira APIs |
| `gh` | GitHub CLI — handles all GitHub operations (PRs, issues, reviews) |

> `curl` and `npm` are pre-installed on macOS. `npm` is bundled with Node.js.

### GitHub CLI Login

After installing `gh`, you need to sign in **once**:

```bash
gh auth login
```

Follow the prompts — it will open your browser to authenticate. This is required before any GitHub operations will work.

To verify:

```bash
gh auth status
```

### Optional Tools

Install these only if you use the specific skills that need them:

```bash
brew install graphviz                    # For Graphviz diagrams (/adk:diagram-graphviz)
brew install --cask docker               # For GitHub MCP server (Docker variant)
curl -LsSf https://astral.sh/uv/install.sh | sh   # For Confluence MCP server
```

### Global npm Packages

These are installed via npm (which comes with Node.js):

```bash
npm install -g diagramkit                # For diagram rendering (Mermaid, Excalidraw, draw.io)
npm install -g @pagesmith/docs           # For documentation generation (CLI)
```

---

## Step 4: MCP Servers

MCP (Model Context Protocol) servers let your AI agent interact with external services like GitHub, Bitbucket, and Confluence directly. Setting them up is optional but recommended — skills fall back to direct API calls (using tokens from `~/.zshenv`) if MCP is not configured.

### Cursor (Plugin MCP)

The ADK plugin ships with a `.mcp.json` that auto-configures MCP servers. After installing the plugin, you'll see these servers in **Settings > MCP**:

| Service | Server Name | How it runs | Required in `~/.zshenv` |
|---------|------------|-------------|------------------------|
| GitHub | `plugin-adk-github` | Docker (stdio) | `GITHUB_PAT` |
| Bitbucket | `plugin-adk-bitbucket` | npx bitbucket-mcp (stdio) | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `plugin-adk-atlassian-confluence` | uvx mcp-atlassian (stdio) | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Atlassian (all products) | `plugin-adk-atlassian` | HTTP (OAuth, browser-based) | — none — |

All stdio servers use `zsh -c` wrappers, which auto-source `~/.zshenv` on every launch — so env vars are always available, even when Cursor is started from the Dock or Spotlight.

**Atlassian HTTP MCP** uses OAuth — Cursor opens a browser window to authenticate with your Atlassian account on first use. No tokens needed. This single server provides access to Jira, Confluence, and Bitbucket via the Atlassian Rovo API.

### Claude Code (Automated)

```text
/adk:setup --type mcps
```

This reads your API tokens from `~/.zshenv` and configures MCP servers in `~/.claude.json`. If tokens are missing, it tells you exactly what to add.

| Service | MCP Server Key | How it runs | Required tokens in `~/.zshenv` |
|---------|---------------|-------------|-------------------------------|
| GitHub | `github` | Docker `ghcr.io/github/github-mcp-server` | `GITHUB_PAT` |
| Bitbucket | `bitbucket` | `npx bitbucket-mcp` | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `atlassian-confluence` | `uvx mcp-atlassian` | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Atlassian | `atlassian` | HTTP (OAuth, browser-based) | — none — |
| Google Drive | `google-drive` | `npx @piotr-agier/google-drive-mcp` | OAuth credentials file |

### Direct API Fallback

When MCP is not available (or fails), connector skills fall back to direct API calls using `curl`. These always read tokens from `~/.zshenv`:

| Service | Variables |
|---------|----------|
| GitHub | `gh` CLI (via `gh auth login`) — preferred; `GITHUB_PAT` as fallback |
| Bitbucket | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Jira | `JIRA_URL`, `JIRA_USERNAME`, `JIRA_API_TOKEN` |

### Manual MCP Setup

If you prefer to configure MCP servers manually, add them to `~/.claude.json` (Claude Code) or `~/.cursor/mcp.json` (Cursor) under the `mcpServers` key.

---

## Step 5: Install ADK

### Option A: Claude Code Plugin (Recommended)

In Claude Code, run:

```text
/plugin marketplace add sujeet-pro/agents-devkit
/plugin install adk@adk-marketplace
```

Skills appear as `/adk:skill-name` (with a colon).

### Option B: skills.sh (Claude Code / Codex)

```bash
npx skills add sujeet-pro/agents-devkit
```

Skills appear as `/skill-name` (with a hyphen). Works with Claude Code, Codex, and other [skills.sh](https://skills.sh)-compatible agents.

### Option C: Local Clone

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
claude --plugin-dir ~/.devkit
```

Skills appear as `/adk:skill-name` (with a colon), same as Option A.

---

## Step 6: Verify Everything

Run the setup skill to check that everything is properly configured:

```text
/adk:setup --check-only
```

This reports the status of every tool, MCP server, and configuration item without making any changes. If anything is missing, it tells you exactly how to fix it.

To fix everything automatically:

```text
/adk:setup
```

---

## Naming: `/adk:` vs `/`

You may notice skills appearing with two different invocation styles:

| Install Method | Invocation | Example |
|----------------|------------|---------|
| Claude Plugin or local `--plugin-dir` | `/adk:<skill-name>` | `/adk:code-review-pr` |
| skills.sh (`npx skills`) | `/<skill-name>` | `/code-review-pr` |

**Both invoke the same skill.** The difference is only in how ADK was installed. The Claude Plugin uses the `adk:` namespace automatically; skills.sh uses the skill's `name` field directly. If you see a mix (e.g., `/adk:setup` and `/setup`), you have both installation methods active. Pick one — the Claude Plugin (`/adk:`) is recommended as ADK is designed for Claude Code.

> **Note:** Some ADK features require Claude Code: custom sub-agents with persistent memory, hooks that validate frontmatter and check task completion, and plugin-scoped MCP server configurations. When installed via `npx skills`, core skill workflows function but these advanced features are unavailable.

---

## Troubleshooting

### "command not found" after installing a tool

Close and reopen Terminal, or run:

```bash
source ~/.zshenv
```

### MCP server not connecting

1. Check that your tokens in `~/.zshenv` are correct
2. Run `/adk:setup --type mcps --check-only` to see what's wrong
3. Run `/adk:setup --type mcps` to reconfigure

### GitHub CLI says "not authenticated"

Run:

```bash
gh auth login
```

Follow the browser prompts. This is required once per machine.

### Bitbucket or Confluence API returning 401

Your token has expired or has insufficient permissions. Generate a new one (see [Step 2](#step-2-api-tokens)), update `~/.zshenv`, then run:

```text
/adk:setup --type mcps
```

This syncs the new tokens into your MCP configuration.

### `/adk:setup` says "Homebrew not installed"

Install Homebrew first (see [Step 1](#step-1-install-homebrew)), then re-run `/adk:setup`.

---

## Summary

| What | How | One-time? |
|------|-----|-----------|
| Homebrew | Terminal command | Yes |
| API tokens in `~/.zshenv` | Manual text edit | Yes (update when tokens rotate) |
| CLI tools (git, node, gh, etc.) | `brew install` or `/adk:setup` | Yes |
| `gh auth login` | Terminal command | Yes |
| MCP servers | `/adk:setup --type mcps` | Yes (re-run to sync tokens) |
| ADK plugin | `/plugin install` | Yes |

After the initial setup, the only maintenance is updating tokens when they expire. Run `/adk:setup` at any time to check the health of your setup — it's safe to run repeatedly and will only fix what's broken.
