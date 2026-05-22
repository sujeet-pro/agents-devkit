---
title: 'adk-review'
description: 'Review, audit, look-at, sanity-check, check any review-able target. Triggers on: GitHub PR URL (specialized review-pr — most common), `.` or local path (review-code-changes against the working tree), markdown file or...'
skill: 'adk-review'
source: 'skills/adk-review/SKILL.md'
group: 'skills'
order: 1007
---
# adk-review

Review, audit, look-at, sanity-check, check any review-able target. Triggers on: GitHub PR URL (specialized review-pr — most common), `.` or local path (review-code-changes against the working tree), markdown file or Confluence URL (review-doc), comment-thread URL (review-comments), repo path with --audit (audit-repo), PR URL with --audit (audit-pr). Read-only by default. Produces severity-tiered findings (blocker / critical / should / may / nit) with `path:line` + ≤15-word evidence quotes from the actual file. Six dimensions in order: correctness → tests → security → performance → readability → consistency. Loads adk-agent-code-reviewer always, adk-agent-security-reviewer when diff touches auth/input/crypto/deps. Under --fix: applies accepted findings locally + pushes after confirm (never force, never merges, never protected branches). Under -i: walks each finding. Under --plan: read-only review-and-recommend; no edits. Refuses single-pass for diffs >5000 LOC.

## Source

`skills/adk-review/SKILL.md`

## Frontmatter

```yaml
name: adk-review
description: |
  Review, audit, look-at, sanity-check, check any review-able target. Triggers on: GitHub PR URL (specialized review-pr — most common), `.` or local path (review-code-changes against the working tree), markdown file or Confluence URL (review-doc), comment-thread URL (review-comments), repo path with --audit (audit-repo), PR URL with --audit (audit-pr). Read-only by default. Produces severity-tiered findings (blocker / critical / should / may / nit) with `path:line` + ≤15-word evidence quotes from the actual file. Six dimensions in order: correctness → tests → security → performance → readability → consistency. Loads adk-agent-code-reviewer always, adk-agent-security-reviewer when diff touches auth/input/crypto/deps. Under --fix: applies accepted findings locally + pushes after confirm (never force, never merges, never protected branches). Under -i: walks each finding. Under --plan: read-only review-and-recommend; no edits. Refuses single-pass for diffs >5000 LOC.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<target> [-i|--interactive] [--fix] [--audit] [--plan|--act] [--severity blocker|critical|should]"
metadata:
  category: code
  kind: task
  layer: 1
  paths: ["**/*.{ts,tsx,js,jsx,py,go,rs,java,rb,php,cs,kt,swift,c,cpp,h,hpp,sh,sql,yaml,yml,json,toml,md}"]
  model: opus
  effort: high
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-atlassian]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [severity-bar, dimensions, auto-post-policy, confidence-threshold, nit-tolerance, mode]
```

## Workflow body

# adk-review — review any target (lightweight)

Polymorphic on target. Read-only by default; `--fix` extends to apply + push (never force, never merge, never to protected branches).

**Lightweight by design** — no worktree, no embeddings, no SCIP. For a deep PR review with code-context retrieval (worktree + LanceDB embeddings + SCIP + feature-flag tracing), use `/adk-pr-review`.

**Hybrid path** — repo-bound (`<repo>/.temp/adk/review/<task>/`) when reviewing local code (`.`, `--audit`, a doc in the cwd repo); global (`~/.agents-devkit/reviews/<task>/`) when reviewing a remote PR URL from outside the relevant repo. Path resolved per `shared/paths.md`.

## References (loaded as needed)

| Aspect | File |
|---|---|
| Target dispatch (which sub-flow) | `references/dispatch.md` |
| Workflow (Phase 0–4) | `references/workflow.md` |
| Fork IDs | `references/forks.md` |
| Hard rules + refusals | `references/rules.md` |
| Sub-flow detail | `references/<sub-flow>.md` — authored on first real use |

## Cross-skill dependencies

- Personas: `shared/personas/{code-reviewer,security-reviewer,test-engineer}.md`
- Plan/Act mode: `shared/plan-act-mode.md`
- Code index (light path): `shared/guidelines/code-index.md` — `similar()` over each diff hunk to surface adjacent code the diff alone doesn't show. Heavy PR review with full embedding + reranking is `/adk-pr-review`, not this skill.
- Constitution: `shared/constitution.md`
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`

## References shipped

- `references/dispatch.md` — see [`/adk-review/references/dispatch.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-review/references/dispatch.md)
- `references/forks.md` — see [`/adk-review/references/forks.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-review/references/forks.md)
- `references/rules.md` — see [`/adk-review/references/rules.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-review/references/rules.md)
- `references/workflow.md` — see [`/adk-review/references/workflow.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-review/references/workflow.md)
