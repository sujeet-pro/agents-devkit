---
name: adk-implement
description: |
  Implement, build, add, write, ship, code-up, wire-up code in an existing repo. Triggers on: Jira URL or KEY-NUM (specialized from-jira sub-flow — the most common path), GitHub issue URL or #N (from-issue), Confluence TDD URL (from-tdd), Slack thread permalink (from-slack-thread), or a freeform description (greenfield). Git mandatory; GitHub MCP optional but enables PR-by-URL flow. Every run: question-first (3 questions max), advisor-strategy plan with 2–4 trade-off options, edit-format discipline (SEARCH/REPLACE blocks per shared/edit-format.md), repo-native typecheck+lint+narrow-tests on each checkpoint. Writes plan/steps/diffs/report under `<repo>/.temp/adk/implement/<task>/`. Pushes only after explicit confirmation; never force-pushes; never merges; never touches a protected branch. Pulls Jira context via adk-mcp-atlassian, GitHub context via adk-mcp-github, and optional RAG via adk-mcp-rag. Supports --plan (read-only planning) → --act (writes). Sub-flows under references/.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<input-url-or-description> [-i|--interactive] [--plan|--act] [--scope vertical-slice|full|spike] [--no-push] [--detailed] [--deep]"
metadata:
  category: code
  kind: task
  layer: 1
  paths: ["**/*.{ts,tsx,js,jsx,py,go,rs,java,rb,php,cs,kt,swift,c,cpp,h,hpp,sh,sql,yaml,yml,json,toml}"]
  model: sonnet
  effort: medium
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: [adk-mcp-github]
  needs_mcp_optional: [adk-mcp-atlassian, adk-mcp-slack, adk-mcp-rag]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [scope, approach, test-framework, pr-strategy, commit-style, linter-tolerance, breaking-change-policy, mode, model-depth]
---

# adk-implement — write code from any input

Polymorphic on input. **Git mandatory; GitHub MCP optional** (enables PR-by-URL flow).

**Repo-bound skill** — must run from inside a repo (or `--repo <path>`). Artifacts go to `<repo>/.temp/adk/implement/<task>/` (per `shared/paths.md`).

`--detailed` asks the skill to gather richer programmatic context before editing (for example, broader code-index queries or supporting docs). `--deep` asks the harness to use its stronger model profile per `shared/model-depth.md`. Auto-select `--deep` for ambiguous architecture choices, cross-module changes, migrations, auth/security/payments/permissions work, or large blast radius.

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
- Model depth: `shared/model-depth.md`
- Constitution: `shared/constitution.md`
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`
- Code index (TDD sub-flow): `shared/guidelines/code-index.md` — when drafting a TDD from a Jira ticket, call `from scripts.lib.code_index.query import open_index, similar, callers` to surface related code patterns + blast-radius estimates. Fail open on `IndexNotBuilt` (prompt the user to run `adk repo add <git-url>`). Surface `indexed_sha` + `age_days` in the draft.

## Sub-flow status

| Sub-flow | Status |
|---|---|
| from-jira | spec is `references/from-jira.md` — authored on first real use |
| from-issue | spec is `references/from-issue.md` — authored on first real use |
| from-tdd / from-confluence / from-slack-thread / greenfield | authored on first real use |

The skill self-authors a sub-flow reference on its first invocation, asks the user to confirm, then saves it for future runs. This avoids filler content written without real signal.
