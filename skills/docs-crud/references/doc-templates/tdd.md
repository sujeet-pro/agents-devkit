# TS-NNN: [Title]

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Tech Spec |
| Document ID | TS-NNN |
| Status | Draft |
| Owner | [name] |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Project / Initiative | [name or N/A] |
| Tracking Link(s) | [Jira / GitHub / Linear / N/A] |
| Target Milestone / Release | [milestone or N/A] |
| Related Docs | [links to RFC, ADRs, PRDs] |
| Repositories / Services | [repo or service names] |

## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## Summary

[One paragraph: what is changing and why. A reader who only reads this paragraph should understand the full scope.]

## Context / Problem Statement

[Current situation, pain point, business or technical driver. Quantify the impact where possible: error rates, latency, revenue loss, customer complaints. Link to the originating RFC, PRD, or feature request.]

## Goals

- [Specific, measurable goal with success criteria]
- [Each goal must be verifiable — "improve performance" is not a goal; "reduce p99 latency to under 200ms" is]

## Non-Goals

- [What is explicitly excluded] — [why it is deferred]

## Requirements and Constraints

### Functional Requirements

- [What the system must do, described as testable behaviors]

### Non-Functional Requirements

| Requirement | Target | Basis |
|-------------|--------|-------|
| Latency | p99 < [X]ms | [Current SLO / projected peak] |
| Throughput | [X] req/sec | [Projected peak load] |
| Availability | [X]% uptime | [SLA commitment] |

### Constraints

- [Infrastructure, budget, timeline, backward-compatibility constraints]

## Current State

[Existing architecture, behavior, or workflow being changed. Include a diagram for non-trivial changes.]

<!-- DIAGRAM: Current state architecture showing existing components and data flow -->

## Proposed Design — High-Level (HLD)

### Architecture Overview

[Architecture diagram showing major components, their responsibilities, and data flow between them. Focus on "what" and "why", not "how".]

<!-- DIAGRAM: Proposed architecture with major components and data flow -->

### Component Boundaries

| Component | Responsibility | Inputs | Outputs |
|-----------|---------------|--------|---------|
| [Name] | [One sentence] | [Data consumed] | [Data produced] |

### External Dependencies

| System | Protocol | Failure Mode | Fallback |
|--------|----------|-------------|----------|
| [Name] | [REST/gRPC/queue] | [What happens when unavailable] | [Degraded behavior] |

## Detailed Design (LLD)

### Component: [Name]

[Responsibility, internal structure, interfaces, dependencies.]

### API Contracts

[Full endpoint specifications with method, path, request/response schemas, error codes, auth requirements.]

### Data Model

[Schema definitions, indexes, constraints, migrations. Include ER diagram for complex models.]

<!-- DIAGRAM: Entity-Relationship diagram for the data model -->

### State Transitions

[State machine for entities with complex lifecycles.]

<!-- DIAGRAM: State transition diagram -->

### Error Handling

| Error Code | HTTP Status | Condition | User Message | Recovery |
|------------|-------------|-----------|-------------|----------|
| [CODE] | [4xx/5xx] | [When this occurs] | [User-facing message] | [Recovery action] |

### Configuration

| Parameter | Type | Default | Constraints | Restart Required |
|-----------|------|---------|-------------|-----------------|
| [name] | [type] | [value] | [range] | [yes/no] |

## Alternatives Considered

### Alternative 1: [Name]

[Approach, advantages, disadvantages, why rejected.]

### Alternative 2: [Name]

[Approach, advantages, disadvantages, why rejected.]

## Security / Privacy / Compliance

[Authentication, authorization, input validation, data encryption (at rest and in transit), PII handling, audit logging. Identify trust boundaries. Reference applicable compliance requirements.]

## Reliability / Scalability / Performance

[Capacity estimates with back-of-envelope math. Horizontal vs vertical scaling strategy. Failure modes with blast radius, detection, and recovery. Cascading failure mitigation.]

<!-- CHART: bar | Capacity projections: current vs 6-month vs 12-month load -->

## Observability

[Key metrics per component (latency percentiles, error rates, throughput). Logging strategy. Distributed tracing. Alerting thresholds tied to SLO targets. Dashboard definitions.]

## Testing Strategy

| Level | Scope | Approach | Acceptance Criteria |
|-------|-------|----------|-------------------|
| Unit | [scope] | [approach] | [criteria] |
| Integration | [scope] | [approach] | [criteria] |
| E2E | [scope] | [approach] | [criteria] |
| Load | [scope] | [approach] | [criteria] |

## Migration / Rollout / Rollback

### Deployment Phases

1. [Phase name] — [success criteria, rollback trigger]

### Feature Flags

- [Flag name] — [purpose, kill-switch behavior]

### Rollback Plan

[How to revert each phase, including data migration rollback.]

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| [Risk description] | [Low/Medium/High] | [Low/Medium/High] | [Mitigation plan] |

## Open Questions

| # | Question | Owner | Target Date | Resolution |
|---|----------|-------|-------------|------------|
| 1 | [Specific, actionable question] | [name] | [date] | [pending] |

## Decision Log / ADR Links

| Decision | ADR | Date |
|----------|-----|------|
| [Decision made during design] | [ADR-NNN link] | [date] |

## Appendix

[Detailed examples, extended schemas, benchmarks, additional diagrams.]
