# Stage: Tech Spec / Technical Design Document

A Tech Spec answers the question "how exactly will we build and operate this?" It includes both high-level design (HLD) and detailed design (LLD) as sections within a single document.

For pre-alignment on direction before committing to a design, use the `rfc` stage. To record a single durable decision after the spec is written, use the `adr` stage.

## Type-Specific Phase Guidance

### Exploration
- Research the current architecture and the systems being changed
- Identify integration points, data flows, and failure modes
- Scan for related RFCs, ADRs, and existing design documents
- Load coding guidelines when the design includes architecture or code analysis

### Execute
- Write the Tech Spec following the document structure below
- Use `--weight` to determine depth: `lightweight` (1-3 pages) vs. `heavyweight` (10-20 pages)
- Include architecture diagrams using `/diagram`

## Document Structure

### Metadata Block
Standard metadata header with document ID, status, owner, dates, and tracking links.

### Review Tracker
Review tracking table with named reviewers, roles, and status. Identify reviewers before moving to "In Review" status.

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

### 7. Proposed Design -- High-Level (HLD)
Architecture overview with diagram. Major components, responsibilities, data flow, external dependencies. This covers "what" and "why" at the system level.

### 8. Detailed Design (LLD)
Component internals, API contracts with typed schemas, data model with migration plans, state transitions, error handling with enumerated error codes, configuration parameters. This covers "how" at the component level.

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
- Keep LLD minimal -- a brief API description and schema change is sufficient.
- Target 1-3 pages.

When `weight=heavyweight` or the scope suggests a cross-team, high-impact change:
- Fill all sections in depth.
- Use appendices for detailed schemas, benchmarks, and extended examples.
- Target 10-20 pages.

## Writing Rules

- Ground all architecture decisions in concrete constraints, not abstract best practices.
- Every "we will use X" must be followed by "because Y."
- HLD covers "what" and "why" at the system level; LLD covers "how" at the component level. Do not mix these concerns.
- When describing real code, inspect the repository first instead of inventing APIs.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.

## Type-Specific Output Format

Markdown file. Invoke `/doc-writing --type tdd` to load TDD writing guidelines for validation.

## Validation Checklist

- All mandatory sections are present
- HLD and LLD are clearly separated
- Architecture diagrams are included and accurate
- Alternatives section has genuine options (not strawmen)
- Security section is complete
- Testing strategy has acceptance criteria
- Rollback plan is documented
- Weight matches scope (lightweight for simple, heavyweight for complex)

## Adjacent Skills

- `rfc` stage for RFC documents (pre-alignment on direction)
- `adr` stage for recording individual architecture decision records
- `/diagram` for standalone architecture diagrams
