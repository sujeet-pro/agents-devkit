---
title: "code-review-pr"
description: PR, local, or branch code review with fix, describe, and finalize actions
skill_name: code-review-pr
category: task
workflow_tier: full
---

# code-review-pr

Reviews pull requests (GitHub/Bitbucket), local uncommitted changes, or branch diffs. Supports reviewing, fixing, describing, and finalizing PRs.

## When to Use

- Review someone else's PR
- Self-review your local changes before creating a PR
- Generate a PR title and description
- Check PR merge readiness

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<target>` | PR URL, branch name, or empty | local changes | What to review |
| `--action` | `describe`, `fix`, `finalize`, `status` | review | PR management action instead of review |
| `--fix` | flag | off | Auto-fix issues found during review |
| `--focus` | `security`, `performance`, `deps`, `ui`, `codebase` | all dimensions | Narrow the review focus |
| `--mode` | `auto`, `standard`, `interactive`, `followup` | `auto` | Review interaction style |
| `--skip-repo` | flag | off | Review only the PR diff (no local repo needed) |
| `--cross` | flag | off | Multi-model cross-review for higher confidence |
| `--publish` | flag | off | Post review comments to the PR platform |
| `--ui` | flag | off | Include UI/UX review dimension |
| `--confidence` | flag | off | Show confidence ratings per finding |
| `--context` | URL(s) | — | Additional context URLs (specs, designs) |
| `--branch` | branch name | — | Review a branch diff |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameters |

## Workflow

Full 6-phase workflow for reviews. Abbreviated (phases 2–5 skipped) for PR management actions (`describe`, `fix`, `finalize`, `status`).

| Phase | Action |
|-------|--------|
| 0. Intent | Detect source type (PR URL, local, branch), confirm scope |
| 1. Research | Fetch diff, detect stack, load coding guidelines via `coding` skill |
| 2. Approach | Present review dimensions, user selects focus |
| 3. Planning | Break review into waves for parallel agents |
| 4. Execute | Run review with parallel child agents per dimension |
| 5. Validate | Merge findings, deduplicate, assign severity and confidence |

### Source Detection

| Input | Detected As |
|-------|-------------|
| GitHub/Bitbucket URL | Remote PR review |
| Branch name with `--branch` | Branch diff review |
| No arguments | Local uncommitted changes |

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `review-standards`, `principal-engineer` (medium+), `agentic-teams`, `interaction`, `github`/`bitbucket` (for remote PRs), `coding` (loads stack-specific guidelines).

## Examples

```text
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:code-review-pr https://github.com/org/repo/pull/42 --focus security --publish
/adk:code-review-pr --branch feature/auth
/adk:code-review-pr --fix
/adk:code-review-pr --action describe --publish
/adk:code-review-pr https://github.com/org/repo/pull/42 --cross
/adk:code-review-pr https://github.com/org/repo/pull/42 --action finalize
```
