---
name: review-code
description: Use when you need DevKit to route a code review request to the correct `review-code-*` skill without mutating the source content
user_invocable: true
arguments:
  - name: target
    description: "PR number or URL, file path, repository path, or scope (staged, branch, worktree)"
    required: true
  - name: tags
    description: "Optional repo tags such as frontend, backend, design-system, library, scripts"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100)"
    required: false
---

# Code Review Router

Use `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/source-routing.md`, and `skills/_references/preflight-validations.md`.

## Routing Rules

- GitHub PR or Bitbucket PR -> `/devkit:review-code-pr`
- staged, unstaged, branch-local, or recently committed branch changes -> `/devkit:review-code-local`
- local repository path or phrases like "entire repo" -> `/devkit:review-codebase`

Always preserve `tags` and `confidence` when forwarding.
The routed skill owns the preflight check and must run it before launching child agents.

Code review skills never update the source directly. When comments cannot be posted inline, the routed skill must produce a markdown review document instead.
