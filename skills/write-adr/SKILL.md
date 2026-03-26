---
name: write-adr
description: Use when you need to draft or directly revise a professional Architecture Decision Record from a PR, discussion notes, or codebase analysis
user_invocable: true
arguments:
  - name: source
    description: "Source material: a PR URL, path to discussion notes, or 'codebase' to derive decisions from repository state"
    required: true
  - name: title
    description: "Short title for the architecture decision (imperative verb phrase)"
    required: true
  - name: output-dir
    description: "Directory to write the ADR file (default: docs/adr/)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence (default: markdown)"
    required: false
---

# Architecture Decision Record

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly refresh an ADR. An ADR answers the question "what decision did we make, and why?" ADRs are short (0.5-2 pages), durable, and immutable after acceptance.

If you only want comments on an existing ADR, use `/devkit:review-doc`. For pre-alignment on direction, use `/devkit:write-rfc`. For implementation detail, use `/devkit:write-system-design` (Tech Spec).

## Preflight

Before reading any source material or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-adr format=<format>`

If the ADR will be published to Confluence or Google Docs in addition to the repository, verify MCP connectivity.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/document-metadata.md`
- `skills/_references/guidelines/document/adr.md`

## Numbering

Scan `output-dir` (default `docs/adr/`) for existing ADR files. Determine the next sequence number by finding the highest existing `NNNN-*.md` prefix and incrementing by one. If the directory is empty or does not exist, start at `0001`. Name the output file `<NNNN>-<kebab-case-title>.md`.

## Required Child Agents

Run at least these child agents in parallel:

- **Source analyst**: reads the PR diff, discussion notes, or codebase depending on `source`. Extracts the key technical facts, constraints, and stakeholder concerns that drive the decision.
- **Decision mapper**: identifies the specific decision points, alternatives considered, and the rationale for the chosen approach. Cross-references with existing ADRs in `output-dir` to check for superseded or related decisions.
- **Consequence reviewer**: evaluates short-term and long-term consequences of the decision including risks, trade-offs, migration impact, and reversibility.
- `source-publisher` if the final output is Confluence or Google Docs in addition to markdown.

Save intermediary artifacts to `.temp/write-adr/`.

## ADR Structure

The ADR must follow the structure defined in `skills/_references/guidelines/document/adr.md`. Every ADR includes:

### Title

Format: `ADR-NNNN: <Imperative verb phrase>`. The title describes the decision, not the problem. Keep it under 80 characters.

### Metadata

Compact metadata block with status, date, owner, decision-makers, consulted, informed, and related docs.

### Review Tracker

Include for significant or cross-team decisions. Follow the format in `document-metadata.md`. Omit for lightweight, single-team decisions where the decision-makers are already listed in the metadata.

### Context and Problem Statement

The forces at play and the problem requiring a decision. Objective — does not argue for a solution. Links to related RFCs, Tech Specs, tickets, and prior ADRs.

### Decision Drivers

Bullet list of key factors that influenced the choice: quality attributes, constraints, team expertise, timeline pressures, compliance requirements.

### Considered Options

At least two options that were seriously evaluated, each with a brief description.

### Decision

The chosen option with specific, actionable detail. Named technologies, patterns, and approaches. Justification referencing the decision drivers.

### Consequences

Three categories — Positive, Negative, and Neutral. Must include operational consequences. Honest about trade-offs.

### Links

Related RFCs, Tech Specs, ADRs, and tracking tickets.

## Writing Rules

- ADRs should be short and durable — 0.5-2 pages. If it grows beyond that, the detail belongs in a Tech Spec.
- State decisions specifically. "We will use caching" is not a decision; name the cache, the strategy, and the data.
- ADRs are immutable after acceptance. To change a decision, create a new ADR and mark the old one as Superseded.
- Be honest about negative consequences. An ADR with only positive consequences is incomplete.
- Default to markdown as the source of truth. ADRs live in the code repository under `docs/adr/`.
- When the ADR describes real code, inspect the repository first instead of inventing APIs.

## Final Step

Before publishing, verify the ADR against the review checklist in `skills/_references/guidelines/document/adr.md`. Ensure the ADR number is sequential, the status includes a date, and all sections are complete.

## Adjacent Skills

- `/devkit:write-rfc` for RFC documents (pre-alignment on direction)
- `/devkit:write-system-design` for Tech Spec / Technical Design Documents (implementation detail)
- `/devkit:review-doc` for comment-only review of existing ADRs
- `/devkit:publish-confluence` for publishing to Confluence
