---
name: review-codebase
description: Use when you need a non-mutating whole-repository review that produces a prioritized engineering improvement document instead of editing code directly
user_invocable: true
arguments:
  - name: repo
    description: "Repository root to review (default: current directory)"
    required: false
  - name: focus
    description: "Optional focus area: architecture, frontend, backend, design-system, docs, tests, performance, security"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
  - name: publish
    description: "Where to post the result: none, google-doc, confluence (default: none)"
    required: false
---

# Codebase Review

Use the shared DevKit child-agent contract in `skills/_references/agentic-teams.md`, the review flow in `skills/_references/review-pipeline.md`, the source routing rules in `skills/_references/source-routing.md`, and the output rules in `skills/_references/output-formats.md`.

This skill is review-only. Do not update repository files in place. Produce a review artifact or publish that artifact to a document destination.

## Required Team

Run at least these child agents in parallel:

- `repo-auditor` for system-level architecture and maintainability
- `code-reviewer` for correctness, security, performance, and code patterns
- `doc-reviewer` for docs drift, onboarding quality, and examples
- one domain specialist based on the detected repo type: frontend, backend, or design system

## Scope

Review:

- repository structure and ownership boundaries
- build, test, and release ergonomics
- public APIs and documentation quality
- code patterns, duplication, and modernization opportunities
- missing diagrams or architecture docs

## Output

Always produce:

- an executive summary
- a prioritized improvement backlog
- quick wins vs. strategic initiatives
- documentation and diagram follow-ups
- clear next steps that another agent can use to plan implementation

If `publish` is set, publish the final markdown artifact to the requested document source after the review completes.
