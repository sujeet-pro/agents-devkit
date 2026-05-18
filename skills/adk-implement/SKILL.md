---
name: adk-implement
description: |
  Implement, build, add, write, ship, code-up, wire-up code in an existing repo. Triggers on: Jira URL or KEY-NUM (specialized from-jira sub-flow — the most common path), GitHub issue URL or #N (from-issue), Confluence TDD URL (from-tdd), Slack thread permalink (from-slack-thread), or a freeform description (greenfield). Git mandatory; GitHub MCP optional but enables PR-by-URL flow. Every run: question-first (3 questions max), advisor-strategy plan with 2–4 trade-off options, edit-format discipline (SEARCH/REPLACE blocks per shared/edit-format.md), repo-native typecheck+lint+narrow-tests on each checkpoint. Writes plan/steps/diffs/report under `<repo>/.temp/<task-slug>/`. Pushes only after explicit confirmation; never force-pushes; never merges; never touches a protected branch. Pulls Jira context via adk-mcp-atlassian, GitHub context via adk-mcp-github, and optional RAG via adk-mcp-rag. Supports --plan (read-only planning) → --act (writes). Sub-flows under references/.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<input-url-or-description> [--auto|-i] [--plan|--act] [--scope vertical-slice|full|spike] [--no-push]"
metadata:
  category: code
  kind: task
  layer: 1
  paths: ["**/*.{ts,tsx,js,jsx,py,go,rs,java,rb,php,cs,kt,swift,c,cpp,h,hpp,sh,sql,yaml,yml,json,toml}"]
  model: opus
  effort: high
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: [adk-mcp-github]
  needs_mcp_optional: [adk-mcp-atlassian, adk-mcp-slack, adk-mcp-rag]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [scope, approach, test-framework, pr-strategy, commit-style, linter-tolerance, breaking-change-policy, mode]
---

# adk-implement — write code from any input

Polymorphic on input. **Git mandatory; GitHub MCP optional** (enables PR-by-URL flow).

## References (loaded as needed)

| Aspect | File |
|---|---|
| Input dispatch (which sub-flow) | `references/dispatch.md` |
| Workflow (Phase 0–4) | `references/workflow.md` |
| Fork IDs (defaults trained by `/adk-improve`) | `references/forks.md` |
| Hard rules + refusals | `references/rules.md` |
| Sub-flow detail | `references/<sub-flow>.md` — authored on first use of each sub-flow |

## Cross-skill dependencies

- Edit-format: `shared/edit-format.md`
- Plan/Act mode: `shared/plan-act-mode.md`
- Constitution: `shared/constitution.md`
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`

## Sub-flow status

| Sub-flow | Status |
|---|---|
| from-jira | spec is `references/from-jira.md` — authored on first real use |
| from-issue | spec is `references/from-issue.md` — authored on first real use |
| from-tdd / from-confluence / from-slack-thread / greenfield | authored on first real use |

The skill self-authors a sub-flow reference on its first invocation, asks the user to confirm, then saves it for future runs. This avoids filler content written without real signal.
