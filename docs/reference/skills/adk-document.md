---
title: 'adk-document'
description: 'Document, write, draft, write-up, summarize. Generates any professional markdown artifact: runbook, ADR, RCA, PR body, commit message, changelog, Mermaid diagram, README, migration guide, API reference, experiment...'
skill: 'adk-document'
source: 'skills/adk-document/SKILL.md'
group: 'skills'
order: 1000
---
# adk-document

Document, write, draft, write-up, summarize. Generates any professional markdown artifact: runbook, ADR, RCA, PR body, commit message, changelog, Mermaid diagram, README, migration guide, API reference, experiment report, incident summary, onboarding doc, design doc, handoff doc. Markdown-first; repo-bound: output goes to `<repo>/.temp/adk/document/<task>/draft.md` (or repo-canonical path with --write-to). Does NOT publish — that's /adk-sync. Composable: any other adk skill can call this to generate a writeup, then call /adk-sync to push it. Cites every non-trivial claim to a repo path or quoted source; no filler phrases (anti-pattern grep enforced). Audience-tuned (engineer / pm / exec / mixed) — voice doesn't mix. Loads adk-agent-doc-writer always; loads relevant shared/guidelines (observability for runbook/RCA, api-design for api-reference, security for RCA, accessibility for UI docs) by --type. Quotes from external sources capped at 15 words.

## Source

`skills/adk-document/SKILL.md`

## Frontmatter

```yaml
name: adk-document
description: |
  Document, write, draft, write-up, summarize. Generates any professional markdown artifact: runbook, ADR, RCA, PR body, commit message, changelog, Mermaid diagram, README, migration guide, API reference, experiment report, incident summary, onboarding doc, design doc, handoff doc. Markdown-first; repo-bound: output goes to `<repo>/.temp/adk/document/<task>/draft.md` (or repo-canonical path with --write-to). Does NOT publish — that's /adk-sync. Composable: any other adk skill can call this to generate a writeup, then call /adk-sync to push it. Cites every non-trivial claim to a repo path or quoted source; no filler phrases (anti-pattern grep enforced). Audience-tuned (engineer / pm / exec / mixed) — voice doesn't mix. Loads adk-agent-doc-writer always; loads relevant shared/guidelines (observability for runbook/RCA, api-design for api-reference, security for RCA, accessibility for UI docs) by --type. Quotes from external sources capped at 15 words.
allowed-tools: [Read, Edit, Write, Grep, Glob, Bash, WebFetch, Agent]
argument-hint: "<intent-or-source> --type <artifact-type> [--audience engineer|pm|exec|mixed] [--write-to <path>] [-i|--interactive]"
metadata:
  category: docs
  kind: task
  layer: 1
  paths: ["**/*.md"]
  model: opus
  effort: medium
  user-invocable: true
  disable-model-invocation: false
  needs_mcp_required: []
  needs_mcp_optional: [adk-mcp-github, adk-mcp-atlassian, adk-mcp-rag]
  needs_meta_info: [workspaces, repos]
  forks_emitted: [tone, audience, template, length-target, citation-density]
```

## Workflow body

# adk-document — generate any markdown artifact

Markdown-first; never publishes (that's `/adk-sync`). Cites every non-trivial claim.

**Repo-bound skill** — must run from inside a repo (or `--repo <path>`). Drafts go to `<repo>/.temp/adk/document/<task>/draft.md`; `--write-to <path>` overrides to a canonical repo path. Per `shared/paths.md`.

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
- Guidelines (auto-load by `--type`): observability / api-design / security / accessibility / data-modeling
- Advisor + question-first: `shared/advisor.md`, `shared/question-first.md`, `shared/narration.md`

## References shipped

- `references/dispatch.md` — see [`/adk-document/references/dispatch.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-document/references/dispatch.md)
- `references/forks.md` — see [`/adk-document/references/forks.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-document/references/forks.md)
- `references/rules.md` — see [`/adk-document/references/rules.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-document/references/rules.md)
- `references/workflow.md` — see [`/adk-document/references/workflow.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/adk-document/references/workflow.md)
