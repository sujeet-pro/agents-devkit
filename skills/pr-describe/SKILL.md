---
name: pr-describe
description: Generate and post a PR description based on code changes for GitHub or Bitbucket pull requests
user_invocable: true
arguments:
  - name: pr
    description: "PR number or URL"
    required: true
  - name: style
    description: "Description style: concise, detailed, conventional (default: detailed)"
    required: false
  - name: template
    description: "Custom template name from repo's .github/PULL_REQUEST_TEMPLATE.md or similar (optional)"
    required: false
---

# PR Description Generator

Generate a comprehensive PR description from the actual code changes and post it to GitHub or Bitbucket. This skill analyzes the diff, commit history, and codebase context to produce a well-structured description that helps reviewers understand the what, why, and how of the change.

## Agent & Skill Delegation

**Always use the devkit's own agents and skills:**

| Task | Delegate To |
|------|-------------|
| Research (if PR touches unfamiliar patterns) | `/research` skill (spawns **research-agent**) |
| Diagram generation (for architectural changes) | `/diagram` skill → **diagram-agent** |

---

## Phase 1: Pre-flight

### 1a. Detect VCS platform

Read the git remote URL to determine GitHub or Bitbucket:

```bash
git remote get-url origin
```

| Remote URL pattern | Platform |
|-|-|
| Contains `github.com` | **GitHub** |
| Contains `bitbucket.org` | **Bitbucket** |
| Contains `bitbucket` (e.g. Server / Data Center) | **Bitbucket** |
| Otherwise | Ask the user |

For Bitbucket, extract `workspace` and `repo_slug` from the remote URL.
For GitHub, extract `owner` and `repo` from the remote URL.

### 1b. Parse PR identifier

The `$ARGUMENTS.pr` value may be:
- A bare number (e.g. `42`) — treat as PR number in the detected repo
- A full GitHub URL (e.g. `https://github.com/org/repo/pull/42`)
- A full Bitbucket URL (e.g. `https://bitbucket.org/workspace/repo/pull-requests/42`)

Normalize to a numeric `PR_NUMBER`.

### 1c. Check for PR template

Look for a PR description template in the repo:

```
.github/PULL_REQUEST_TEMPLATE.md
.github/pull_request_template.md
docs/pull_request_template.md
PULL_REQUEST_TEMPLATE.md
.bitbucket/pull_request_template.md
```

If found, use it as the structural skeleton for the description. If `$ARGUMENTS.template` is specified, use that specific template.

---

## Phase 2: Gather Context

Fetch all data needed to understand the change. Execute these in parallel where possible.

### For GitHub

```bash
# PR metadata
gh pr view $PR_NUMBER --json title,body,headRefName,baseRefName,author,labels,milestone

# Full diff
gh pr diff $PR_NUMBER

# Commits
gh pr view $PR_NUMBER --json commits

# Changed files summary
gh pr view $PR_NUMBER --json files
```

### For Bitbucket

1. `mcp__bitbucket__getPullRequest` — title, description, source/destination branches, author
2. `mcp__bitbucket__getPullRequestDiff` — full unified diff
3. `mcp__bitbucket__getPullRequestCommits` — commit history
4. `mcp__bitbucket__getPullRequestDiffStat` — file change summary (added/modified/deleted counts)

### Local context

Also gather local context to enrich the description:

```bash
# Switch to PR branch
git fetch origin <source_branch>
git checkout <source_branch>
```

- Read modified files in full (not just the diff) to understand the broader context
- Check if any tests were added/modified
- Check if any config or migration files changed
- Look for related issue references in commit messages

---

## Phase 3: Analyze Changes

Categorize and understand the changes:

### 3a. Change classification

Classify the overall PR:

| Signal | Classification |
|--------|---------------|
| New files in feature directories | **New Feature** |
| Modified existing logic, bug-related commit messages | **Bug Fix** |
| Moved/renamed files, no behavior change | **Refactoring** |
| Only test files changed | **Test Improvement** |
| Only docs/comments changed | **Documentation** |
| Config, CI, build file changes | **Infrastructure / DevOps** |
| Dependency updates | **Dependency Update** |
| Multiple categories | **Mixed** — list all |

### 3b. Impact analysis

For each changed file, determine:
- What component/module it belongs to
- Whether the change is behavioral (affects runtime) or structural (refactoring, types)
- Whether it's a public API change (breaking or non-breaking)
- Whether it touches critical paths (auth, payments, data, etc.)

### 3c. Extract key decisions

From commit messages and code patterns, identify:
- Why was this approach chosen over alternatives?
- What trade-offs were made?
- What's intentionally NOT included (scope limits)?

---

## Phase 4: Generate Description

Generate the PR description based on the `style` argument.

### Style: `detailed` (default)

```markdown
## Summary

<1-3 sentence high-level summary of what this PR does and why>

## Changes

<Grouped list of changes by component/area. Each group has a heading and bullet points explaining what changed and why.>

### <Component/Area 1>
- Change description with context on why

### <Component/Area 2>
- Change description with context on why

## Testing

<Description of how the changes were tested>
- Unit tests added/updated: <list>
- Manual testing steps (if applicable)
- Edge cases covered

## Impact

- **Breaking changes**: <none, or description>
- **Migration needed**: <none, or steps>
- **Performance impact**: <none, or description>
- **Security considerations**: <none, or description>

## Related

- Closes #<issue> (if referenced in commits)
- Related to #<issue> (if contextually related)
- Depends on #<PR> (if applicable)
```

### Style: `concise`

```markdown
## Summary

<1-2 sentence summary>

## Changes

- <bullet point per logical change>

## Testing

- <bullet point per test approach>
```

### Style: `conventional`

Uses Conventional Commits format for the title and a structured body:

```markdown
<type>(<scope>): <short description>

## What

<Brief description of the changes>

## Why

<Motivation and context>

## How

<Implementation approach and key decisions>

## Testing

<How it was verified>
```

Where `type` is one of: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `perf`, `ci`, `build`.

### Template-based

If a PR template was found (Phase 1c), fill in each section of the template with the analyzed content. Preserve the template's structure exactly — fill sections, don't restructure them.

---

## Phase 5: Iterative Quality Loop

Self-review the generated description before presenting. **Max 2 iterations.**

```
iteration = 0
max_iterations = 2

while iteration < max_iterations:
    iteration += 1
    issues = review_description()
    if no issues: break
    fix(issues)
    if no fixes applied this iteration: break
```

**Quality checklist:**

| Check | Severity | Action |
|---|---|---|
| Every statement is verifiable from the diff | CRITICAL | Remove or correct unverifiable claims |
| No sensitive data (secrets, internal URLs) | CRITICAL | Remove immediately |
| All referenced files actually exist in the diff | WARNING | Correct file references |
| Issue references match commit messages | WARNING | Fix issue numbers |
| Test section is present and accurate | WARNING | Add or correct |
| Breaking changes are called out | WARNING | Add missing breaking change notes |
| Description fits the template structure (if template found) | WARNING | Restructure to match |
| Summary is concise (readable in < 2 min) | INFO | Trim verbose sections |

**Convergence rules:** Same pattern — max 2 iterations, stuck detection.

---

## Phase 6: Present & Post

### 6a. Preview

Show the generated description to the user:

```
## Generated PR Description

<rendered description>

---

Post this description to PR #<number>? (yes/edit/cancel)
```

- `yes` — Post as-is
- `edit` — User provides feedback, regenerate
- `cancel` — Abort without posting

### 6b. Post

#### For GitHub

```bash
gh pr edit $PR_NUMBER --body "<description>"
```

If the PR title should also be updated (e.g., `conventional` style generates a better title):

```bash
gh pr edit $PR_NUMBER --title "<new title>" --body "<description>"
```

#### For Bitbucket

Use `mcp__bitbucket__updatePullRequest` to update the PR description (and optionally the title).

### 6c. Confirm

After posting, confirm:

```
PR #<number> description updated successfully.
View: <PR URL>
```

---

## Rules

1. **Accuracy**: Every statement in the description must be verifiable from the diff or commit history. Never fabricate changes.
2. **Conciseness**: Be thorough but not verbose. Reviewers should understand the PR in under 2 minutes of reading.
3. **Context over code**: Explain the *why* and *impact*, not just the *what*. The diff already shows what changed.
4. **No sensitive data**: Never include secrets, credentials, or internal URLs in the description.
5. **Preserve existing content**: If the PR already has a description with manual notes from the author, ask before overwriting. Offer to merge/append instead.
6. **Respect templates**: If the repo has a PR template, follow its structure exactly.
7. **Link issues**: If commits reference issues (e.g., `fixes #123`, `JIRA-456`), include those references.
8. **Mention tests**: Always note what testing was done or is needed. If no tests were added for a behavioral change, flag it.
