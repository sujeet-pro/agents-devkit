---
name: write-adr
description: Use when you need to draft or directly revise a professional Architecture Decision Record from a PR, discussion notes, or codebase analysis
user_invocable: true
arguments:
  - name: source
    description: "Source material: a PR URL, path to discussion notes, or 'codebase' to derive decisions from repository state"
    required: true
  - name: title
    description: "Short title for the architecture decision"
    required: true
  - name: output-dir
    description: "Directory to write the ADR file (default: docs/adr/)"
    required: false
---

# Architecture Decision Record

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly refresh the ADR. If you only want comments on an existing ADR, use `/devkit:review-doc`.

## Preflight

Before reading any source material or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-adr`

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

When `skills/_references/guidelines/document/adr.md` exists, load it as the primary ADR format guide. Otherwise fall back to the standard ADR template: Title, Status, Context, Decision, Consequences.

## Numbering

Scan `output-dir` (default `docs/adr/`) for existing ADR files. Determine the next sequence number by finding the highest existing `NNNN-*.md` prefix and incrementing by one. If the directory is empty or does not exist, start at `0001`. Name the output file `<NNNN>-<kebab-case-title>.md`.

## Required Child Agents

Run at least these child agents in parallel:

- Source analyst: reads the PR diff, discussion notes, or codebase depending on `source`. Extracts the key technical facts, constraints, and stakeholder concerns that drive the decision.
- Decision mapper: identifies the specific decision points, alternatives considered, and the rationale for the chosen approach. Cross-references with existing ADRs in `output-dir` to check for superseded or related decisions.
- Consequence reviewer: evaluates short-term and long-term consequences of the decision including risks, trade-offs, migration impact, and reversibility.

Save intermediary artifacts to `.temp/write-adr/`.
