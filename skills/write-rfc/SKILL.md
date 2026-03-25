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

Use this skill when the agent should create or directly revise an RFC. For lighter decision proposals, use `/devkit:write-proposal`. To record the final decision after an RFC is accepted, use `/devkit:write-adr`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-rfc format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If the document needs diagrams, inherit the `/devkit:diagram` preflight before rendering assets.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

Load RFC-specific guidance when available. Also load `skills/_references/guidelines/document/research-and-fact-checking.md` for research-heavy work and the matching coding guidance from `skills/_references/guidelines/coding/` when the RFC covers implementation details.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for prior art, official docs, industry standards, and competing approaches
- `code-snippet-agent` for examples grounded in the repository or ecosystem
- `doc-reviewer` for structure, clarity, and completeness
- a diagram pass through `/devkit:diagram` for architecture and flow diagrams
- `source-publisher` if the final output is Confluence or Google Docs

## RFC Structure

The RFC must include these sections:

### 1. Summary
A one-paragraph executive summary of the proposal.

### 2. Motivation
Why this change is needed. What problem does it solve? What is the current pain point or gap?

### 3. Detailed Design
The technical design in full detail. Include:
- Architecture diagrams (use `/devkit:diagram` skills)
- API contracts and data models where applicable
- Interaction flows and sequence diagrams
- Configuration and deployment considerations

### 4. Alternatives Considered
At least two alternative approaches with pros and cons for each. Explain why they were not chosen.

### 5. Migration Plan
How to migrate from the current state to the proposed state. Include:
- Phased rollout plan
- Backward compatibility considerations
- Rollback strategy
- Data migration steps if applicable

### 6. Open Questions
Unresolved questions that need stakeholder input before or during implementation.

### 7. Timeline
Estimated timeline with milestones.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets or when strict layout control clearly requires it.
- Use only free or open tooling for conversion and rendering.
- When the RFC describes real code, inspect the repository first instead of inventing APIs.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.
