---
title: "dev-commit"
description: Create commits or PR descriptions — analyzes changes, generates conventional commit messages
skill_name: dev-commit
category: task
workflow_tier: full
user_invocable: true
---

# dev-commit

Generate meaningful commit messages, PR descriptions, and changelogs from analyzed code changes. Understands the semantic intent of changes beyond just the diff.

## When to Use

- Create a well-structured commit message from staged or unstaged changes
- Generate a PR description summarizing all branch commits
- Produce changelog entries from recent commits
- Amend the last commit with an improved message
- Commit with a specific convention (conventional, gitmoji, plain)

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--action` | `commit` \| `pr-describe` \| `changelog` | `commit` | What to generate |
| `--convention` | `conventional` \| `gitmoji` \| `plain` | auto-detect from repo | Commit message format |
| `--scope` | `<module>` | auto-detect | Scope tag for conventional commits |
| `--auto` | flag | off | Skip confirmation, commit directly |
| `--amend` | flag | off | Amend the last commit instead of creating a new one |
| `--staged` | flag | off | Only consider staged changes |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Action | Behavior |
|--------|----------|
| `commit` (default) | Analyze changes, generate commit message, confirm, commit |
| `pr-describe` | Analyze all commits on the branch, generate a structured PR description |
| `changelog` | Generate changelog entries from recent commits |

| Context | Behavior |
|---------|----------|
| Auto-detect convention | Scans recent git log for existing patterns (conventional, gitmoji, plain) and matches |
| `--amend` | Amends the last commit instead of creating a new one |
| `--staged` | Only considers staged changes, ignoring unstaged modifications |
| `--auto` | Skips confirmation prompt and commits directly |

## Commit Message Generation

### 1. Analyze Changes

- Read the staged diff (or all uncommitted changes if nothing staged)
- Categorize the change: feature, fix, refactor, docs, test, chore, perf, style, build, ci
- Identify the primary scope (module, component, or file area)
- Detect breaking changes

### 2. Generate Message

Supports three formats:

**Conventional Commit** (`--convention conventional`):
```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Type mapping: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`, `build`, `ci`. Description is imperative mood, lowercase, no period. Body explains *why*, not *what*. Footer includes `BREAKING CHANGE:` when applicable.

**Gitmoji** (`--convention gitmoji`):
```
:emoji: <description>
```

Common mappings: `:sparkles:` feat, `:bug:` fix, `:recycle:` refactor, `:memo:` docs, `:white_check_mark:` test.

**Plain** (`--convention plain`):
```
<Description>

<Optional body>
```

### 3. Confirm

Presents the generated message and asks for confirmation: **approve**, **edit: \<changes\>**, or **cancel**.

### 4. Execute

Runs `git commit` with the approved message.

## PR Description Generation

### 1. Analyze Branch

- Find all commits since the branch diverged from the base
- Group commits by type and scope
- Identify the overall purpose of the branch
- List files changed with summary of changes

### 2. Generate Description

Produces a structured PR description with Summary, Changes (grouped by category), Testing checklist, and Breaking Changes sections.

## Key Behaviors

- **Semantic analysis**: understands the intent of changes beyond raw diff content
- **Convention auto-detection**: scans recent git log to match the project's existing commit style
- **Change categorization**: automatically classifies changes into type (feat, fix, refactor, etc.) and scope
- **Breaking change detection**: identifies and flags breaking changes in commit footers
- **Interactive confirmation**: presents the generated message for approval before committing

## Workflow

Uses the 6-phase workflow at trivial complexity — direct execution for commits, fuller workflow for PR descriptions and changelogs.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm action, detect convention |
| 1. Research & Options | yes | Analyze diff, scan git log for conventions |
| 2. Approach Selection | commit: no; pr-describe/changelog: if needed | Present format options for complex PRs |
| 3. Planning | no | Direct generation |
| 4. Execute | yes | Generate message, confirm, commit |
| 5. Validate & Learn | yes | Verify commit succeeded |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase workflow. For commits, trivial complexity — direct execution. |
| `communication` | always | Lead with conclusion. Concrete specifics. No preamble. |
| `preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `output-format` | producing output | short/standard/detailed verbosity. |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `interaction` | NOT --auto | Inline protocols for intent confirmation, plan approval. |

## Output Format

**Commit**: the generated commit message displayed for confirmation, then the git commit output.

**PR Description**: structured markdown with Summary, Changes (grouped by category), Testing checklist, and Breaking Changes sections.

**Changelog**: grouped entries by type with descriptions.

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:dev-build` | Implementing the changes before committing |
| `/adk:code-review-pr` | Reviewing the PR after creating it |
| `/adk:docs-write --type changelog` | Detailed changelog generation |

## Examples

```
/adk:dev-commit
/adk:dev-commit --convention conventional --scope auth
/adk:dev-commit --action pr-describe
/adk:dev-commit --action changelog
/adk:dev-commit --auto --amend
```
