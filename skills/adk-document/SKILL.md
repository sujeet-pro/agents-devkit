---
name: adk-document
description: |
  Document, write, draft, write-up, summarize. Generates any professional markdown artifact: runbook, ADR, RCA, PR body, commit message, changelog, Mermaid diagram, README, migration guide, API reference, experiment report, incident summary, onboarding doc, design doc, handoff doc. Markdown-first; repo-bound: output goes to `<repo>/.temp/adk/document/<task>/draft.md` (or repo-canonical path with --write-to). Does NOT publish — that's /adk-sync. Composable: any other adk skill can call this to generate a writeup, then call /adk-sync to push it. Cites every non-trivial claim to a repo path or quoted source; no filler phrases (anti-pattern grep enforced). Audience-tuned (engineer / pm / exec / mixed) — voice doesn't mix. Loads adk-agent-doc-writer always; loads relevant shared/guidelines (observability for runbook/RCA, api-design for api-reference, security for RCA, accessibility for UI docs) by --type. Quotes from external sources capped at 15 words.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<intent-or-source> --type <artifact-type> [--audience engineer|pm|exec|mixed] [--write-to <path>] [-i|--interactive] [--detailed] [--deep]"
metadata:
  category: docs
  kind: task
  layer: 1
  paths: ["**/*.md"]
  model: sonnet
  effort: medium
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-atlassian, adk-mcp-rag]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [tone, audience, template, length-target, citation-density, model-depth]
---

# adk-document — generate any markdown artifact

Markdown-first; never publishes (that's `/adk-sync`). Cites every non-trivial claim.

**Repo-bound skill** — must run from inside a repo (or `--repo <path>`). Drafts go to `<repo>/.temp/adk/document/<task>/draft.md`; `--write-to <path>` overrides to a canonical repo path. Per `shared/paths.md`.

`--detailed` increases evidence gathering and citation density. `--deep` selects the stronger model profile per `shared/model-depth.md`; use it for ADRs, RCAs, migration guides, ambiguous design docs, or docs that synthesize multiple systems.

## References (loaded as needed)

| Aspect | File |
|---|---|
| Type dispatch (which template) | `references/dispatch.md` |
| Workflow (Phase 0–4) | `references/workflow.md` |
| Fork IDs | `references/forks.md` |
| Hard rules + refusals | `references/rules.md` |
| Per-type template detail | `references/<type>.md` — authored on first real use |

## Cross-skill dependencies

- Persona: `shared/personas/doc-writer.md`
- Model depth: `shared/model-depth.md`
- Guidelines (auto-load by `--type`): observability / api-design / security / accessibility / data-modeling
- Code index (runbook / ADR / migration): `shared/guidelines/code-index.md` — `similar()` to find related modules the doc must reference; `defs()`/`callers()` to enumerate the API surface a migration touches.
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`
