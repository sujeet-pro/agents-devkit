---
name: write-project-docs
description: Use when you need to draft or directly revise professional project documentation by scanning a repository and updating the docs in place
user_invocable: true
arguments:
  - name: repo
    description: "Repository root (default: current directory)"
    required: false
  - name: source
    description: "Existing documentation path for direct revision"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
  - name: depth
    description: "Depth: quick, standard, comprehensive (default: standard)"
    required: false
---

# Project Docs

Use `skills/_references/agentic-teams.md`, `skills/_references/review-pipeline.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly refresh project documentation. If you only want review findings, use `/devkit:review-doc` or `/devkit:review-codebase`.

## Preflight

Before scanning the repo or generating diagrams, run:

`zsh scripts/check-skill-deps.zsh write-project-docs format=<format> source=<source>`

If the output destination is Confluence or Google Docs, verify the matching MCP with a lightweight read before the doc team starts. If diagrams are required, inherit the `/devkit:diagram` preflight first.

## Required Child Agents

Run at least these child agents in parallel:

- `repo-auditor` for architecture and module boundaries
- `research-agent` for external dependencies and official references
- `code-snippet-agent` for setup, API, and workflow examples
- `doc-reviewer` for structure and onboarding quality
- `/devkit:diagram` for architecture, flow, or ownership diagrams

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/project.md`
- `skills/_references/guidelines/document/research-and-fact-checking.md`
- `skills/_references/guidelines/coding/general.md`
- `skills/_references/guidelines/coding/architecture.md`

## Coverage

Project documentation should cover:

- architecture and package layout
- setup and verification steps
- main workflows and commands
- public APIs, extension points, or integration surfaces
- diagrams that match the actual codebase

Make the final deliverable professional and maintainable. Use `/devkit:review-codebase` first when the repo needs a broad improvement audit before documentation work.
