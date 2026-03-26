---
name: write-system-design
description: Use when creating a Tech Spec or Technical Design Document that covers architecture (HLD), detailed design (LLD), data models, APIs, and operational concerns
user_invocable: true
arguments:
  - name: title
    description: "Title or subject of the technical design"
    required: true
  - name: scope
    description: "Scope boundary: what is in and out of scope for this design"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
  - name: weight
    description: "Template weight: lightweight (1-3 pages, single-team), heavyweight (10-20 pages, cross-team). Default: auto-detect from scope."
    required: false
---

# Tech Spec / Technical Design Document

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly revise a Tech Spec (also called Technical Design Document, TDD, or Design Doc). A Tech Spec answers the question "how exactly will we build and operate this?" It includes both high-level design (HLD) and detailed design (LLD) as sections within a single document.

For pre-alignment on direction before committing to a design, use `/devkit:write-rfc`. To record a single durable decision after the spec is written, use `/devkit:write-adr`. For other document types, use `/devkit:write-doc`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-system-design format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team. If diagrams are needed, inherit the `/devkit:diagram` preflight before rendering assets.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/document-metadata.md`
- `skills/_references/guidelines/document/tdd.md`

When the HLD or LLD sections require deep treatment, also load:

- `skills/_references/guidelines/document/hld.md`
- `skills/_references/guidelines/document/lld.md`

Load coding guidelines when the design includes architecture or code analysis:

- `skills/_references/guidelines/coding/architecture.md`
- `skills/_references/guidelines/coding/general.md`

Load `skills/_references/guidelines/document/research-and-fact-checking.md` for research-heavy work.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for relevant standards, prior art, and ecosystem constraints
- `code-snippet-agent` for grounding the design in actual repository code and APIs
- `doc-reviewer` for structure, clarity, and completeness against the Tech Spec guideline checklist
- a diagram pass through `/devkit:diagram` for architecture, component, data model, and deployment visuals
- `source-publisher` if the final output is Confluence or Google Docs

## Document Structure

The Tech Spec must follow the structure defined in `skills/_references/guidelines/document/tdd.md`. The document scales naturally based on the `weight` argument.

### Metadata Block

Standard metadata header with document ID (TS-NNN), status, owner, dates, tracking links, and related docs. Follow the format in `document-metadata.md`. Use the Tech Spec status lifecycle: Draft -> In Review -> Approved -> Implementing -> Implemented.

### Review Tracker

Review tracking table with named reviewers, roles, and status. Follow the format in `document-metadata.md`. Identify reviewers before moving to "In Review" status.

### 1. Summary

One paragraph on what is changing and why. Must stand on its own.

### 2. Context / Problem Statement

Current situation, pain point, and business or technical driver. Link to the originating RFC, PRD, or feature request.

### 3. Goals

Specific, measurable goals that define the success criteria for the implementation.

### 4. Non-Goals

What this design deliberately excludes and why.

### 5. Requirements and Constraints

Functional requirements, non-functional requirements with quantified targets, compliance constraints, timeline, and dependencies.

### 6. Current State

Existing architecture, behavior, or workflow being changed. Include a diagram if the change is non-trivial.

### 7. Proposed Design — High-Level (HLD)

Architecture overview with diagram. Major components, responsibilities, data flow, external dependencies. Follow `hld.md` content standards. This covers "what" and "why" at the system level.

### 8. Detailed Design (LLD)

Component internals, API contracts with typed schemas, data model with migration plans, state transitions, error handling with enumerated error codes, configuration parameters. Follow `lld.md` content standards. This covers "how" at the component level.

### 9. Alternatives Considered

At least two genuine alternatives with pros, cons, and rejection rationale.

### 10. Security / Privacy / Compliance

Mandatory. Auth, data protection, trust boundaries, compliance requirements.

### 11. Reliability / Scalability / Performance

Capacity math, scaling strategy, failure modes with blast radius and recovery.

### 12. Observability

Metrics, logging, tracing, alerting thresholds tied to SLO targets, dashboards.

### 13. Testing Strategy

Unit, integration, e2e, load testing with acceptance criteria for each level.

### 14. Migration / Rollout / Rollback

Deployment phases with success criteria, feature flags, rollback plan including data migration rollback.

### 15. Risks and Mitigations

Known risks with likelihood, impact, and mitigation plan.

### 16. Open Questions

Unresolved decisions with owners and target resolution dates.

### 17. Decision Log / ADR Links

Key decisions made during design, linked to ADRs.

### 18. Appendix

Detailed examples, extended schemas, benchmarks, additional diagrams.

## Lightweight vs Heavyweight

When `weight=lightweight` or the scope suggests a single-team, moderate-complexity change:
- Fill only: Metadata, Summary, Context, Goals, Non-Goals, Proposed Design (HLD), Testing Strategy, Rollout, Open Questions.
- Keep LLD minimal — a brief API description and schema change is sufficient.
- Target 1-3 pages.

When `weight=heavyweight` or the scope suggests a cross-team, high-impact change:
- Fill all sections in depth.
- Use appendices for detailed schemas, benchmarks, and extended examples.
- Target 10-20 pages.

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- Default to markdown as the source of truth unless the destination requires a native format.
- When describing real code, inspect the repository first instead of inventing APIs.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams. Use Graphviz only when maintaining existing `.dot` assets.
- Use only free or open tooling for conversion and rendering.
- Ground all architecture decisions in concrete constraints, not abstract best practices.
- Every "we will use X" must be followed by "because Y."
- HLD covers "what" and "why" at the system level; LLD covers "how" at the component level. Do not mix these concerns.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff. Verify the document against the review checklist in `skills/_references/guidelines/document/tdd.md`.

## Adjacent Skills

- `/devkit:write-rfc` for RFC documents (pre-alignment on direction)
- `/devkit:write-adr` for recording individual architecture decision records
- `/devkit:write-doc` for other document types (PRD, article, blog)
- `/devkit:diagram` for standalone architecture diagrams
- `/devkit:publish-confluence` for publishing to Confluence
