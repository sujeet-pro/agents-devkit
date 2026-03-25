---
name: pr-describe
description: Generate or update a PR description from the actual diff, commits, docs impact, and review risks for GitHub or Bitbucket
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: style
    description: "Description style: concise, detailed, conventional (default: detailed)"
    required: false
  - name: template
    description: "Optional repo template name or path"
    required: false
  - name: publish
    description: "Where to send the result: markdown, source, both (default: source)"
    required: false
---

# PR Description

Use `skills/_references/agentic-teams.md`, `skills/_references/source-routing.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before diff analysis or template filling, run:

`zsh scripts/check-skill-deps.zsh pr-describe pr=<pr> publish=<publish>`

Then do a lightweight read through the matching GitHub or Bitbucket MCP before launching child agents.

## Required Child Agents

Run at least these child agents in parallel:

- `code-reviewer` for behavior, risk, and test impact
- `doc-reviewer` for migration notes, rollout notes, and reviewer guidance
- `source-publisher` if the PR body should be updated directly

## Output

Base the description on the real diff, commits, and repository context. Include:

- what changed
- why it changed
- risk and rollback notes
- tests and docs impact
- follow-up items if they exist

Post back through the GitHub or Bitbucket MCP when `publish` includes source updates.
