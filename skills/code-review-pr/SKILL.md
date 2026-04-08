---
name: code-review-pr
description: "adk - [full] [code-review] PR, local, or branch code review — review, fix, describe, finalize with conditional stages"
user-invocable: true
argument-hint: "<target> [--fix] [--action describe|fix|finalize|status] [--focus security|performance|deps|ui|codebase] [--mode auto|standard|interactive|followup] [--skip-repo] [--verbosity short|standard|detailed] [--cross] [--context <url>...] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3, gh, curl, jq]
  mcp-servers: [detect-from-input]
workflow-tier: full
maturity: stable
workflow-family: complex-build
workflow-family-overrides:
  describe: quick-action
  fix: quick-action
  finalize: quick-action
  status: quick-action
---

# Review

This skill is the single entry point for all code review workflows — PR review, local change review, branch review, PR management (describe, fix, finalize), and report generation.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always, family varies by action | Complex Build (full review), Quick Action (`--action describe,fix,finalize,status`). `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. Cross-platform markdown safe for GitHub + Bitbucket. |
| `/adk:review-standards` | always (review skills) | Pipeline: intake → ingestion → parallel review → consolidation → output → postback. Canonical comment template with severity, confidence, concern, depth, dimension, guideline. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |
| `/adk:github` | when target is GitHub | GitHub operations via `gh` CLI — PR details, diff, reviews, comments, thread resolution. Validates `gh` install and auth. |
| `/adk:bitbucket` | when target is Bitbucket | Bitbucket REST API via `curl` — PR details, diff, comments, tasks. Uses `BITBUCKET_USERNAME`+`BITBUCKET_TOKEN` from `~/.zshenv`. |
| `/adk:coding` | during guideline loading | Detect repo languages, frameworks, and tools. Load matching coding guidelines for the detected stack. Pass changed files for scoped detection. |

Key review behaviors:
- **Smart parameter detection**: Infers `--mode`, `--action`, and `--focus` from prompt context and PR state (e.g., existing comments trigger re-review mode automatically)
- **Comment consolidation**: Multiple findings on the same line are merged into a single comment; multiple replies to the same thread are combined
- **Praise**: Recognizes well-crafted code with specific, genuine praise (1-3 per review, never forced)
- **Visual clarity**: Comments use icons and concise metadata for easy scanning on PR platforms
- **Context-aware**: Reads PR description, linked Jira tickets, Google Docs, Confluence pages, and other context documents before reviewing code
- **10 review dimensions**: Syntax, correctness, security, performance, design, reliability, testing, documentation, UI/UX (conditional), spec compliance (conditional)
- **Dual tagging**: Every comment carries both a Concern domain (what area) and Review Depth (how deep) classification
- **Platform-adaptive**: Uses italic pipe-separated metadata that renders cleanly on both GitHub and Bitbucket

---

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<target>` | PR URL, branch name, or omitted | (current changes) | What to review |
| `--fix` | flag | off | After review, apply fixes locally (non-PR) or fix PR comments (PR + author) |
| `--action` | `describe`, `fix`, `finalize`, `status` | auto-detect | Force a specific PR management action |
| `--focus` | `security`, `performance`, `deps`, `ui`, `codebase` | all | Weight review toward a specific concern |
| `--mode` | `auto`, `standard`, `interactive`, `followup` | `auto` | Review interaction mode |
| `--skip-repo` | flag | off | Bypass local repository requirements. Run PR review as diff-only using source APIs/MCP, and post validated comments directly. |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--cross` | flag | off | Enable multi-model peer review (built-in cross-review mode) |
| `--publish` | flag | off | Post comments to the PR source |
| `--ui` | flag | auto-detect | Force UI review pass |
| `--confidence` | number | 80 | Minimum confidence threshold for findings (only findings at or above this score are shown) |
| `--context` | URL(s) | none | Additional context URLs (Google Docs, Confluence, Jira tickets, markdown files) to read before reviewing. Multiple URLs separated by spaces |

### Behavior Variations

- **PR URL provided, you are NOT the author**: reviews the PR, posts comments or produces markdown
- **PR URL provided, you ARE the author**: manages the PR (fix comments, describe, finalize)
- **Branch name provided**: reviews branch diff against base
- **No target**: reviews local staged/unstaged changes
- **`--focus security`**: delegates to `/adk:audit --focus security`
- **`--focus performance`**: delegates to `/adk:audit --focus performance`
- **`--focus deps`**: delegates to `/adk:audit --focus dependency`
- **`--focus ui`**: runs built-in UI/UX visual audit (6-pillar review covering layout, typography, color, responsiveness, accessibility, interaction states)
- **`--focus codebase`**: delegates to `/adk:audit --focus codebase`
- **`--cross`**: runs built-in multi-model peer review with consensus scoring
- **`--skip-repo`**: PR review from anywhere (including outside a git repo). Uses source-native MCP/API diff only, skips worktree/full-file pass, and posts comments directly.

### Examples

```
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:code-review-pr https://github.com/org/repo/pull/42 --mode interactive
/adk:code-review-pr https://github.com/org/repo/pull/42 --skip-repo
/adk:code-review-pr https://github.com/org/repo/pull/42 --action fix
/adk:code-review-pr https://github.com/org/repo/pull/42 --action describe
/adk:code-review-pr https://github.com/org/repo/pull/42 --action finalize
/adk:code-review-pr https://github.com/org/repo/pull/42 --context https://docs.google.com/document/d/abc123 https://jira.company.com/browse/PROJ-456
/adk:code-review-pr feature/auth-v2
/adk:code-review-pr --fix
/adk:code-review-pr --focus security
/adk:code-review-pr
```

---

## Preflight & MCP Resolution

Before reading the PR or launching child agents, attempt source-native connector/MCP/API access first, then fall back gracefully.

### Step 1: Detect Provider

Detect GitHub or Bitbucket from:
- The PR URL (if provided)
- The git remote origin (`git remote get-url origin`)

### Step 2: Check MCP

Run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

Then do one lightweight read through the matching source-native MCP to confirm it is connected:

- GitHub -> `mcp__github__*`
- Bitbucket -> `mcp__bitbucket__*`

### Step 3: MCP Fallback -- Direct API or Git

If the MCP is **not configured** or the connectivity check fails, fall back in this order:

#### 3a. Direct API via CLI

Check for the required token in `~/.zshenv`:

- **GitHub**: `GITHUB_PAT` -- use `gh` CLI or `curl` with the GitHub REST API
- **Bitbucket**: `BITBUCKET_USERNAME` + `BITBUCKET_TOKEN` -- use `curl` with the Bitbucket REST API

Read the token:

```bash
grep '^export GITHUB_PAT=' ~/.zshenv | sed 's/^export GITHUB_PAT=//' | tr -d '"'"'"
# or for Bitbucket:
grep '^export BITBUCKET_TOKEN=' ~/.zshenv | sed 's/^export BITBUCKET_TOKEN=//' | tr -d '"'"'"
```

If the token exists, proceed with API-based review. The review operates identically but uses REST API calls instead of MCP tools for reading PR data and posting comments.

**GitHub API fallback commands:**

```bash
# PR metadata
gh pr view <number> --json title,body,baseRefName,headRefName,files,reviews,comments,state

# PR diff
gh pr diff <number>

# PR review comments
gh api repos/{owner}/{repo}/pulls/{number}/comments

# Post a review comment (after user confirmation)
gh api repos/{owner}/{repo}/pulls/{number}/reviews -f body="..." -f event="COMMENT"
```

**Bitbucket API fallback commands:**

```bash
# PR metadata
curl -s -u "${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}"

# PR diff
curl -s -u "${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/diff"

# PR comments
curl -s -u "${BITBUCKET_USERNAME}:${BITBUCKET_TOKEN}" \
  "https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments"
```

#### 3b. Git-Only Fallback (No Token Available, and `--skip-repo` is NOT set)

If no token is found in `~/.zshenv`:

1. **Tell the user** which token is missing and ask them to add it:
   ```text
   GitHub PAT not found. Add to ~/.zshenv:
     export GITHUB_PAT="your-token"
   Then re-source: source ~/.zshenv
   ```

2. **In parallel**, ask the user for branch info to start the review immediately:
   ```text
   While you add the token, I can start reviewing the code locally.

   Which branch is the PR from? (default: current branch)
   Which branch is the PR targeting? (default: auto-detect from git)
   ```

3. **Start the git-based review** without waiting for the token. Use the git diff approach described in the Dual Diff Review section of the pr-review stage.

4. In this mode, the output is a **markdown file only** (`.temp/pr-review/pr-<number>-review.md`) containing all findings in the canonical comment template format. The user can manually post these comments or re-run with the token configured.

#### 3c. Skip-Repo Strict Mode (`--skip-repo`)

When `--skip-repo` is set:

1. Do not require local repository context.
2. Do not run git worktree or local git diff operations.
3. Review only the PR diff and metadata fetched from source-native MCP/API.
4. Post validated findings directly to the PR (comments enabled by default in this mode).
5. If source-native MCP/API access is unavailable, fail fast with actionable setup instructions (do not switch to git-only markdown fallback).

---

## Stage Selection

After preflight, select the primary stage and action stage.

### Primary Stage (mutually exclusive)

| Signal | Stage File | Description |
|--------|-----------|-------------|
| PR URL provided | `stages/pr-review.md` | Full PR review with dual-diff, child agents, interactive loop |
| Source branch name provided (no PR) | `stages/branch-review.md` | Branch-to-branch diff review |
| `--focus security` | Delegate to `/adk:audit --focus security` | Security-focused audit |
| `--focus performance` | Delegate to `/adk:audit --focus performance` | Performance-focused audit |
| `--focus deps` | Delegate to `/adk:audit --focus dependency` | Dependency-focused audit |
| `--focus ui` | `stages/ui-review.md` | Built-in 6-pillar UI/UX visual audit |
| `--focus codebase` | Delegate to `/adk:audit --focus codebase` | Full codebase review |
| `--cross` | `stages/cross-review.md` | Built-in multi-model peer review with consensus |
| Default (no target, no focus) | `stages/local-review.md` | Review staged/unstaged/branch-local changes |

### Action Stage (runs after primary, when applicable)

| Signal | Stage File | Description |
|--------|-----------|-------------|
| PR + current user is NOT the author | `stages/post-pr-comments.md` | Post review comments to the PR |
| PR + current user IS the author + `--action fix` or unresolved comments | `stages/pr-fix-comments.md` | Read and fix review comments |
| PR + `--action describe` | `stages/pr-describe.md` | Generate or update PR description |
| PR + `--action finalize` | `stages/pr-finalize.md` | Finalize PR for merge |
| PR + `--action status` | `stages/pr-finalize.md` | Manage draft status |
| No PR + `--fix` | `stages/fix-locally.md` | Apply review fixes to local code |
| No PR + no fix | `stages/generate-report.md` | Produce markdown review artifact |

Load the selected stage file(s) and follow their instructions.

---

---

## Source Detection & Guideline Loading

### Source Detection

Determine the review target:

1. **PR URL**: extract owner, repo, PR number. Detect provider (GitHub/Bitbucket).
2. **Branch name**: find the branch, determine base branch for diff.
3. **Default**: detect staged changes, unstaged changes, or commits since branch diverged from base.

### Target Branch Detection

Determine the target (base) branch for diff comparison:

1. **From PR metadata** (MCP or API): use the PR's base ref directly.
2. **From git history** (git-only fallback): detect the branch the PR branch was created from:
   ```bash
   for base in main master develop; do
     if git rev-parse --verify "$base" &>/dev/null; then
       MERGE_BASE=$(git merge-base HEAD "$base" 2>/dev/null)
       if [ -n "$MERGE_BASE" ]; then
         echo "$base"
         break
       fi
     fi
   done
   ```
3. **User override**: if provided via argument or prompt, use that directly.

### Guideline Loading

Invoke `/adk:coding` to detect repo frameworks and load matching coding guidelines. Pass the list of changed files from the diff for scoped detection.

Also load repo-local coding guidance when present.

---

## Output Format

All output is markdown by default. Structure varies by stage -- see the stage-specific sections for exact format.

Every review output includes:

- severity-ordered findings (Must Fix -> Suggestion -> Note -> Praise)
- confidence scores, Concern domain, and Review Depth tags per finding
- review dimension attribution (which sub-agent identified the issue)
- source tag (`[diff-only]`, `[full-context]`, `[both]`) per finding (when applicable)
- auto-validation summary (when applicable)
- context documents consumed (linked Jira tickets, Google Docs, Confluence pages)
- open questions and assumptions
- summary of what was posted back to the PR (or saved to markdown)
- comment reconciliation summary covering carried-forward, resolved, reopened, and skipped threads

---

## Adjacent Skills

- `/adk:audit` for codebase quality audits (security, performance, dependency)
- `/adk:setup` to configure tools and MCP servers
- `/adk:dev-build --mode verify` for standalone verification before finalizing
- `/adk:docs-write --type changelog` for release changelogs after merge
