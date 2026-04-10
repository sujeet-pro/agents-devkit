---
name: dev-commit
description: "adk - [full] [dev] Create commits or PR descriptions — analyzes changes, generates conventional commit messages"
user-invocable: true
disable-model-invocation: true
argument-hint: "[--action commit|pr-describe|changelog] [--convention conventional|gitmoji|plain] [--auto] [--help]"
allowed-tools: [Glob, Grep, Read, Bash, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: quick-action
---

# Commit & PR

Generate meaningful commit messages, PR descriptions, and changelogs from analyzed code changes. Understands the semantic intent of changes beyond just the diff.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family quick-action` | always | Quick Action workflow: confirm → execute → verify. For narrow tasks with single execution path. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Concrete specifics. No preamble. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, plan approval. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--action` | `commit`, `pr-describe`, `changelog` | `commit` | What to generate |
| `--convention` | `conventional`, `gitmoji`, `plain` | auto-detect from repo | Commit message format |
| `--scope` | `<module>` | auto-detect | Scope tag for conventional commits |
| `--auto` | flag | off | Skip confirmation, commit directly |
| `--amend` | flag | off | Amend the last commit instead of creating a new one |
| `--staged` | flag | off | Only consider staged changes |

### Behavior Variations

- **`commit`** (default): analyze changes, generate commit message, confirm, commit
- **`pr-describe`**: analyze all commits on the branch, generate a structured PR description
- **`changelog`**: generate changelog entries from recent commits
- **Auto-detect convention**: scan recent git log for existing patterns (conventional, gitmoji, plain)

### Examples

```text
/adk:dev-commit
/adk:dev-commit --convention conventional --scope auth
/adk:dev-commit --action pr-describe
/adk:dev-commit --action changelog
/adk:dev-commit --auto --amend
```

---

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

If any declared dependency is missing, stop and tell the user what to install before proceeding.

## Commit Message Generation

### 1. Analyze Changes

- Read the staged diff (or all uncommitted changes if nothing staged)
- Categorize the change: feature, fix, refactor, docs, test, chore, perf, style, build, ci
- Identify the primary scope (module, component, or file area)
- Detect breaking changes

### 2. Generate Message

#### Conventional Commit Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Type mapping:**
- `feat`: new feature or capability
- `fix`: bug fix
- `refactor`: code restructuring without behavior change
- `docs`: documentation changes
- `test`: adding or updating tests
- `chore`: maintenance, dependencies, configs
- `perf`: performance improvement
- `style`: formatting, linting (no logic change)
- `build`: build system or dependency changes
- `ci`: CI/CD configuration changes

**Rules:**
- Description is imperative mood, lowercase, no period: "add user authentication"
- Body explains *why*, not *what* (the diff shows what)
- Footer includes `BREAKING CHANGE:` when applicable
- Scope is optional but recommended

#### Gitmoji Format

```
:emoji: <description>
```

Common mappings: `:sparkles:` feat, `:bug:` fix, `:recycle:` refactor, `:memo:` docs, `:white_check_mark:` test

#### Plain Format

```
<Description>

<Optional body>
```

### 3. Confirm

Present the generated message and ask for confirmation:

```
## Commit Message

```
feat(auth): add OAuth2 login with Google provider

Implements the OAuth2 authorization code flow with PKCE.
Adds Google as the first social login provider with profile sync.
```

> **approve**, **edit: <changes>**, or **cancel**
```

### 4. Commit

Execute `git commit` with the approved message.

---

## PR Description Generation

### 1. Analyze Branch

- Find all commits since the branch diverged from the base
- Group commits by type and scope
- Identify the overall purpose of the branch
- List files changed with summary of changes

### 2. Generate Description

```markdown
## Summary

<1-3 sentences explaining what this PR does and why>

## Changes

### <Category 1>
- Change description with file references

### <Category 2>
- Change description with file references

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests passing
- [ ] Manual testing completed

## Breaking Changes

<None, or description of breaking changes>
```

### 3. Confirm

Present the generated PR description and ask for confirmation:

```
## PR Description

<rendered description>

> **approve**, **edit: <changes>**, or **cancel**
```

---

## Adjacent Skills

- `/adk:dev-build` for implementing the changes before committing
- `/adk:code-review-pr` for reviewing the PR after creating it
- `/adk:docs-write --type changelog` for detailed changelog generation
