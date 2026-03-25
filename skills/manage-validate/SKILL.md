---
name: manage-validate
description: Validate the MCP servers used by DevKit's code and document workflows, with emphasis on GitHub, Bitbucket, Confluence, and Google Drive
user_invocable: true
arguments:
  - name: server
    description: "Specific server to validate: github, bitbucket, confluence, google-drive, all (default: all)"
    required: false
---

# Validate MCP

Use `skills/_references/preflight-validations.md`.

Run targeted checks in two stages:

- config validation through `zsh scripts/check-skill-deps.zsh manage-validate server=<server>`
- lightweight live MCP reads in parallel for the requested servers

## Preferred Scope

- GitHub MCP for PR read and comment workflows
- Bitbucket MCP for PR read and comment workflows
- Confluence MCP for page read and comment workflows
- Google Drive MCP for Google Docs read and write workflows

## Result Format

For each server, report:

- connectivity status
- which DevKit skills depend on it
- auth or config issues that block review or publishing

Prefer the source-specific server that matches the real input instead of checking unrelated MCPs first.
