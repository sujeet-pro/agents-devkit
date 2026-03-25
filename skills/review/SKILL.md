---
name: review
description: Use when you need DevKit to route a review request to the correct `review-*` skill without mutating the source content
user_invocable: true
arguments:
  - name: target
    description: "PR number or URL, file path, repository path, Confluence URL, or Google Docs URL"
    required: true
  - name: tags
    description: "Optional repo or document tags such as frontend, backend, design-system, project, hld, lld"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100)"
    required: false
---

# Review

Use `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, and `skills/_references/preflight-validations.md`.

## Routing Rules

- GitHub PR or Bitbucket PR -> `/devkit:review-pr`
- local document, Confluence page, or Google Doc -> `/devkit:review-doc`
- staged, unstaged, branch-local, or recently committed branch changes -> `/devkit:review-local`
- local repository path or phrases like "entire repo" -> `/devkit:review-codebase`

Always preserve `tags` and `confidence` when forwarding.
The routed skill owns the preflight check and must run it before launching child agents.

Review skills never update the source directly. When comments cannot be posted inline, the routed skill must produce a markdown review document instead.
