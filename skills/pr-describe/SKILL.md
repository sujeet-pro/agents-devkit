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

Then do a lightweight read through the matching GitHub or Bitbucket MCP to confirm connectivity.

## Source Handling

Detect GitHub or Bitbucket from the PR URL or repository remote:

- GitHub -> `mcp__github__pull_request_read` for PR metadata, diff, and commits
- Bitbucket -> `mcp__bitbucket__getPullRequest` and `mcp__bitbucket__getPullRequestDiff`

## Required Child Agents

Run at least these child agents in parallel:

- **Diff analyzer** (`code-reviewer`): reads the full diff and commit history. Identifies what changed, categorizes changes (feature, fix, refactor, test, docs), assesses risk areas, and flags breaking changes or rollback considerations. Produces a structured change summary.
- **Docs impact reviewer** (`doc-reviewer`): checks whether the changes affect documentation, migration notes, API contracts, or configuration. Identifies missing docs updates. Produces a docs impact brief with follow-up recommendations.
- **Publisher** (`source-publisher`): formats the final description and posts it to the PR through the matching MCP when `publish` includes source updates.

## Workflow

1. **Read PR.** Fetch metadata, diff, and commit history through the source MCP.
2. **Check for template.** If `template` is provided, load it. Otherwise, check for `.github/pull_request_template.md` or equivalent.
3. **Launch child agents.** Run diff analyzer and docs reviewer in parallel.
4. **Draft description.** Compose the PR description based on the `style`:
   - **concise**: 3-5 bullet points covering what and why
   - **detailed**: full sections with what, why, risk, tests, docs, follow-ups
   - **conventional**: follows conventional commit format with scope and type
5. **Publish.** Post through the MCP or output as markdown based on `publish`.

## Output

A PR description containing:

- **What changed**: summary of code changes with key files
- **Why**: motivation and context
- **Risk and rollback**: breaking changes, deployment notes, rollback steps if applicable
- **Tests and docs impact**: test coverage, docs updates needed
- **Follow-up items**: remaining work or known issues

## Adjacent Skills

- `/devkit:pr-finalize` for full branch finalization with verification and review
- `/devkit:review-code-pr` for a full code review of the PR
- `/devkit:write-changelog` for release changelogs
