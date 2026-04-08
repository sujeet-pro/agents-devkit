---
title: "code-review-pr"
description: PR, local, or branch code review with fix, describe, and finalize actions
skill_name: code-review-pr
category: task
workflow_tier: full
user_invocable: true
---

# code-review-pr

Single entry point for all code review workflows: PR review, local change review, branch review, and PR management (describe, fix, finalize). Auto-detects source type, loads coding guidelines for the detected stack, and reviews across 10 dimensions with confidence-scored findings.

## When to Use

- Review a pull request (GitHub or Bitbucket) as a reviewer
- Fix PR review comments as the PR author
- Generate or update a PR description
- Finalize a PR for merge (checklists, draft status)
- Review local staged/unstaged changes before committing
- Review a branch diff against its base
- Run a focused review (security, performance, dependencies, UI)
- Run multi-model peer review with consensus scoring

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<target>` | PR URL, branch name, or omitted | current changes | What to review. PR URL triggers PR workflow; branch name triggers branch diff; omitted reviews local changes |
| `--fix` | flag | off | After review, apply fixes locally (non-PR) or fix PR comments (PR + author). When the reviewer runs this on a PR they authored, it reads unresolved comments and applies code fixes |
| `--action` | `describe` \| `fix` \| `finalize` \| `status` | auto-detect | Force a specific PR management action. `describe` generates PR description; `fix` fixes review comments; `finalize` prepares for merge; `status` manages draft state |
| `--focus` | `security` \| `performance` \| `deps` \| `ui` \| `codebase` | all | Weight review toward a specific concern. `security`/`performance`/`deps`/`codebase` delegate to `/adk:audit`; `ui` runs built-in 6-pillar visual audit |
| `--mode` | `auto` \| `standard` \| `interactive` \| `followup` | `auto` | Review interaction mode. `auto` picks based on context; `interactive` enables per-finding discussion; `followup` re-reviews after fixes |
| `--skip-repo` | flag | off | Run PR review without local repository. Uses source API/MCP diff only, skips worktree/full-file pass, posts comments directly. Fails fast if API unavailable |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level. `short` = summary only; `detailed` = full findings with code snippets |
| `--cross` | flag | off | Multi-model peer review with consensus scoring across independent reviewers |
| `--publish` | flag | off | Post review comments to the PR source (GitHub/Bitbucket) |
| `--ui` | flag | auto-detect | Force UI/UX review pass. Auto-enabled when changes touch frontend files |
| `--confidence` | number | 80 | Minimum confidence threshold (0-100). Only findings at or above this score are included in output |
| `--context` | URL(s) | none | Additional context URLs to read before reviewing: Google Docs, Confluence pages, Jira tickets, or markdown files. Space-separated for multiple |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **PR URL, you are NOT the author** | Reviews the PR across all dimensions, optionally posts comments |
| **PR URL, you ARE the author** | Manages the PR: fixes comments, generates description, finalizes for merge |
| **Branch name provided** | Reviews branch diff against auto-detected or specified base branch |
| **No target** | Reviews local staged/unstaged changes or commits since branch diverged |
| `--focus security` | Delegates to `/adk:audit --focus security` for OWASP-based security audit |
| `--focus performance` | Delegates to `/adk:audit --focus performance` for performance analysis |
| `--focus deps` | Delegates to `/adk:audit --focus dependency` for dependency review |
| `--focus ui` | Runs built-in 6-pillar UI/UX visual audit (layout, typography, color, responsiveness, accessibility, interaction states) |
| `--focus codebase` | Delegates to `/adk:audit --focus codebase` for architecture review |
| `--cross` | Runs built-in multi-model peer review with independent reviewers and consensus |
| `--skip-repo` | No local repo needed. Diff-only from source API. Posts findings directly. Fails fast if no API access |

## Priorities

The skill reviews across **10 dimensions**, weighted by severity:

1. **Syntax** -- parse errors, invalid syntax, type mismatches, import resolution
2. **Correctness** -- logic errors, off-by-one, null access, race conditions, resource leaks
3. **Security** -- injection, auth bypasses, secrets in code, insecure deps, CSRF/SSRF
4. **Performance** -- N+1 queries, missing indexes, memory leaks, bundle size, caching gaps
5. **Design** -- design pattern violations, circular deps, API contract breaks, abstraction mismatches
6. **Reliability** -- error handling, edge cases, failure modes, retry logic
7. **Testing** -- missing tests for changed paths, test quality, coverage gaps
8. **Documentation** -- missing/stale docs, API doc drift, ADR updates needed
9. **UI/UX** (conditional) -- layout, accessibility, responsiveness, interaction states
10. **Spec compliance** (conditional) -- adherence to linked specs, Jira tickets, design docs

Every finding carries a **severity** (Blocker > Critical > Should Have > May Have > Nitpick > Question), a **confidence score** (0-100), a **concern domain**, and a **review depth** tag.

## Key Behaviors

- **Smart parameter detection**: infers `--mode`, `--action`, and `--focus` from prompt context and PR state
- **Comment consolidation**: multiple findings on the same line merge into one comment; multiple thread replies combine
- **Praise**: recognizes well-crafted code with specific, genuine praise (1-3 per review, never forced)
- **Context-aware**: reads PR description, linked Jira tickets, Google Docs, Confluence pages before reviewing
- **Dual tagging**: every comment carries both Concern domain and Review Depth classification
- **Platform-adaptive**: metadata renders cleanly on both GitHub and Bitbucket

## Workflow

Follows the 6-phase workflow for full reviews. PR management actions (describe, fix, finalize) use abbreviated workflow (phases 0-1 only).

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, detect source type, identify tools needed |
| 1. Research & Options | yes | Analyze diff, detect stack, load coding guidelines |
| 2. Approach Selection | yes | Present review strategy options (for full reviews) |
| 3. Planning | yes | Break into parallel review tasks for agent teams |
| 4. Execute | yes | Run selected stage workflow (review, describe, fix, finalize) |
| 5. Validate & Learn | yes | Validate output quality and completeness |

## Source Detection

| Input | Review Type | Stage |
|-------|-------------|-------|
| GitHub/Bitbucket PR URL | PR review with dual-diff | `stages/pr-review.md` |
| Branch name | Branch-to-base diff review | `stages/branch-review.md` |
| `--focus ui` | 6-pillar UI/UX visual audit | `stages/ui-review.md` |
| `--cross` | Multi-model peer review | `stages/cross-review.md` |
| No target | Local staged/unstaged changes | `stages/local-review.md` |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `review-standards` | always | Review pipeline and canonical comment template |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct review roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |
| `github` | target is GitHub | PR details, diff, comments via `gh` CLI |
| `bitbucket` | target is Bitbucket | PR details, diff, comments via REST API |
| `coding` | guideline loading | Detect stack, load matching coding guidelines |

## Output Format

All output is markdown. Every review includes:

- Severity-ordered findings (Blocker → Critical → Should Have → May Have → Nitpick → Question → Praise)
- Confidence scores, concern domain, and review depth tags per finding
- Review dimension attribution per finding
- Source tag (`[diff-only]`, `[full-context]`, `[both]`) when applicable
- Context documents consumed (Jira, Google Docs, Confluence)
- Open questions and assumptions
- Comment reconciliation summary (carried-forward, resolved, reopened, skipped)

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:audit` | Full codebase quality audit (security, performance, dependency) |
| `/adk:code-review-repo` | Review an entire repository, not just a PR |
| `/adk:code-review-fix` | Fix PR comments without re-reviewing |
| `/adk:dev-build --mode verify` | Standalone verification before finalizing |
| `/adk:docs-write --type changelog` | Release changelogs after merge |
| `/adk:setup` | Configure tools and MCP servers for review |

## Examples

```
/adk:code-review-pr https://github.com/org/repo/pull/42
/adk:code-review-pr https://github.com/org/repo/pull/42 --mode interactive
/adk:code-review-pr https://github.com/org/repo/pull/42 --skip-repo
/adk:code-review-pr https://github.com/org/repo/pull/42 --action fix
/adk:code-review-pr https://github.com/org/repo/pull/42 --action describe
/adk:code-review-pr https://github.com/org/repo/pull/42 --action finalize
/adk:code-review-pr https://github.com/org/repo/pull/42 --context https://docs.google.com/document/d/abc123
/adk:code-review-pr feature/auth-v2
/adk:code-review-pr --fix
/adk:code-review-pr --focus security
/adk:code-review-pr
```
