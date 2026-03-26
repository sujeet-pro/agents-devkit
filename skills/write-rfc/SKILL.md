---
name: write-rfc
description: Use when you need to draft or directly revise an RFC (Request for Comments) document for proposing significant technical changes
user_invocable: true
arguments:
  - name: title
    description: "Title of the RFC"
    required: true
  - name: scope
    description: "Optional scope or domain such as backend, frontend, infrastructure, data"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# RFC Writing

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly revise an RFC. An RFC answers the question "should we do this, and which direction should we choose?" For lighter decision proposals, use `/devkit:write-proposal`. For implementation detail, use `/devkit:write-system-design` (Tech Spec). To record the final decision after an RFC is accepted, use `/devkit:write-adr`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-rfc format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If the document needs diagrams, inherit the `/devkit:diagram` preflight before rendering assets.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/document-metadata.md`
- `skills/_references/guidelines/document/rfc.md`

Load `skills/_references/guidelines/document/research-and-fact-checking.md` for research-heavy work and the matching coding guidance from `skills/_references/guidelines/coding/` when the RFC covers implementation details.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for prior art, official docs, industry standards, and competing approaches
- `code-snippet-agent` for examples grounded in the repository or ecosystem
- `doc-reviewer` for structure, clarity, and completeness against the RFC guideline checklist
- a diagram pass through `/devkit:diagram` for architecture and flow diagrams
- `source-publisher` if the final output is Confluence or Google Docs

## RFC Structure

The RFC must follow the structure defined in `skills/_references/guidelines/document/rfc.md`. Every RFC includes:

### Metadata Block

Standard metadata header with document ID, status, owner, dates, and tracking links. Follow the format in `document-metadata.md`.

### Review Tracker

Review tracking table with named reviewers, roles, and status. Follow the format in `document-metadata.md`. Identify reviewers before moving the RFC to "In Review" status.

### 1. Summary

A one-paragraph executive summary readable by any engineer in the organization. Must convey the problem, the proposed direction, and the expected outcome.

### 2. Motivation / Problem Statement

Why this change is needed. What is the current pain point or gap? Include quantitative data when available. Be objective — present the problem without arguing for a specific solution.

### 3. Goals

Specific, verifiable goals that define the success criteria for the proposal.

### 4. Non-Goals

What this RFC explicitly does not address. Prevents scope creep during review and implementation.

### 5. Proposal

The recommended direction with enough detail to evaluate. Include 1-2 architecture or flow diagrams (use `/devkit:diagram` skills). Stay at the "direction" level — defer implementation-level detail to a Tech Spec.

### 6. Alternatives Considered

At least two genuine alternative approaches with pros, cons, and rejection rationale for each. Strawman alternatives undermine the document.

### 7. Impact Analysis

Impact across five dimensions: Engineering, Product/Business, Security/Compliance, Cost/Infrastructure, and Operational. Use a structured table.

### 8. Rollout Approach

High-level phases for introducing the change. Feature flags, backward compatibility, kill-switch strategy. Detailed rollout planning belongs in the Tech Spec.

### 9. Open Questions

Unresolved questions with owners and target resolution dates. Each question must be specific and actionable.

### 10. Decision Requested

Explicitly state what decision the reviewers are being asked to make.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Keep the RFC concise — typically 2-5 pages. If it grows beyond that, the detail likely belongs in a Tech Spec.
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets or when strict layout control clearly requires it.
- Use only free or open tooling for conversion and rendering.
- When the RFC describes real code, inspect the repository first instead of inventing APIs.
- The Motivation section must present the problem objectively without arguing for the proposed solution.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff. Verify the document against the review checklist in `skills/_references/guidelines/document/rfc.md`.

## Adjacent Skills

- `/devkit:write-system-design` for Tech Spec / Technical Design Documents (implementation detail)
- `/devkit:write-adr` for Architecture Decision Records (recording decisions)
- `/devkit:write-proposal` for lighter decision proposals
- `/devkit:diagram` for standalone architecture diagrams
- `/devkit:publish-confluence` for publishing to Confluence
