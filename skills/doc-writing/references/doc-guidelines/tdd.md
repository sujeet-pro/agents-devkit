# Tech Spec / Technical Design Document Guidelines

Guidelines for writing and reviewing Technical Design Documents (also called Tech Specs, TDDs, or Design Docs). A Tech Spec describes how a feature or system will be built, with enough detail that reviewers can evaluate trade-offs and implementers can begin work with minimal ambiguity.

**This is the main implementation document.** It subsumes what some organizations call HLD and LLD by including both as sections within a single document. Separate HLD/LLD documents are only warranted when the system is large enough to require different review audiences.

**Audience**: Engineers, tech leads, and architects who will build, review, or maintain the proposed system.

**When to use**: Use a Tech Spec when the question is "how exactly will we build and operate this?" For pre-alignment on direction, use an RFC. For recording a single durable decision, use an ADR.

**References**:
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [A Practical Guide to Writing Technical Specs — Stack Overflow Blog](https://stackoverflow.blog/2020/04/06/a-practical-guide-to-writing-technical-specs/)
- [How to Write a Good Software Design Document — Angela Zhang (freeCodeCamp)](https://www.freecodecamp.org/news/how-to-write-a-good-software-design-document-66fcf019569c/)
- [Scaling Engineering Teams via RFCs — Gergely Orosz](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- [HLD vs LLD — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/difference-between-high-level-design-and-low-level-design/)

---

## 1. Required Sections

Every Tech Spec must include the following sections in order. Omitting a section requires an explicit justification in the document itself. The document scales naturally: lightweight specs (1-3 pages) keep sections brief; heavyweight specs (10-20 pages) expand sections that need depth.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Metadata | Standard header with review tracking (see `document-metadata.md`) |
| 2 | Summary | One paragraph on what is changing and why |
| 3 | Context / Problem Statement | Current situation, pain point, and business or technical driver |
| 4 | Goals | What this design achieves, stated specifically and measurably |
| 5 | Non-Goals | What this design deliberately excludes |
| 6 | Requirements and Constraints | Functional, non-functional, compliance, timeline, dependencies |
| 7 | Current State | Existing architecture, behavior, or workflow being changed |
| 8 | Proposed Design — High-Level (HLD) | Architecture overview, major components, data flow, diagrams |
| 9 | Detailed Design (LLD) | Component internals, APIs, schemas, state transitions, error handling |
| 10 | Alternatives Considered | Other approaches evaluated and why they were rejected |
| 11 | Security / Privacy / Compliance | Threat model, auth, data protection, regulatory |
| 12 | Reliability / Scalability / Performance | How the system handles growth and failure |
| 13 | Observability | Metrics, logs, traces, alerts, dashboards |
| 14 | Testing Strategy | Unit, integration, e2e, load, canary, validation |
| 15 | Migration / Rollout / Rollback | Backfill, compatibility, deployment stages, kill switch |
| 16 | Risks and Mitigations | What can go wrong and how to handle it |
| 17 | Open Questions | Unresolved decisions with owners and target dates |
| 18 | Decision Log / ADR Links | Key decisions made during design, linked to ADRs |
| 19 | Appendix | Detailed examples, diagrams, schemas, benchmarks |

---

## 2. Content Standards

### Metadata

Follow the standard metadata block and review tracking table defined in `document-metadata.md`. Use the Tech Spec status lifecycle: Draft -> In Review -> Approved -> Implementing -> Implemented.

### Summary

- One paragraph that a new team member can read to understand what is changing and why.
- Must stand on its own — a reader who only reads the Summary should know the scope.

### Context / Problem Statement

- Describe the problem from the user or system perspective, not the solution.
- Include quantitative impact where possible: error rates, latency, revenue loss, customer impact.
- Link to the originating RFC, PRD, incident report, or feature request.
- Reference any previous attempts to solve this problem.

### Goals

- Goals must be specific and verifiable. "Improve performance" is not a goal; "Reduce p99 latency to under 200ms" is.
- Goals define the success criteria for the implementation.

### Non-Goals

- Explicitly state what this design does not address.
- Non-goals prevent scope creep during review and implementation.
- Explain why each non-goal is deferred, not just what it is.

### Requirements and Constraints

- Separate into **functional requirements** (what the system does) and **non-functional requirements** (how well it does it).
- Quantify every non-functional requirement with measurable targets.
- State compliance, regulatory, and timeline constraints.
- List hard dependencies on other teams, systems, or timelines.

### Current State

- Describe the existing architecture, behavior, or workflow that is being changed.
- Include a diagram of the current state if the change is non-trivial.
- This section gives reviewers the baseline to understand the proposed change.

### Proposed Design — High-Level (HLD)

This is the architecture section. It covers "what" and "why" at the system level.

- Include an architecture overview diagram showing major components and their relationships.
- Show data flow direction on all connections between components.
- For each component: state its responsibility (one sentence), inputs and outputs, and boundaries.
- Include a system context diagram (C4 Level 1 or equivalent) if the system interacts with external actors.
- Show read and write paths separately if they differ.
- Keep diagrams to 5-10 components. If more are needed, group into subsystems.
- For integration points: document protocol, data format, failure modes, and SLA expectations.

See `hld.md` for detailed HLD content standards when this section requires deep treatment.

### Detailed Design (LLD)

This is the implementation section. It covers "how" at the component level.

- **Component responsibilities**: What each component owns, delegates, and assumes.
- **APIs / Contracts**: Full endpoint specifications — method, path, request/response schemas, error codes, auth requirements, rate limits. Use typed schemas (OpenAPI, Protobuf), not pseudocode.
- **Schema / Data model changes**: Table definitions with column types, constraints, indexes, partitioning. Include migration scripts for schema changes.
- **Storage / Caching / Messaging**: Technology choices with justification, read/adk-write patterns, cache invalidation strategy.
- **State transitions**: State machines for entities with complex lifecycles.
- **Error handling**: Enumerated error codes with HTTP status, condition, user message, and recovery action. Retry policies with max retries, backoff strategy, and jitter.
- **Idempotency / Retries / Concurrency**: How the system handles duplicate requests, retries, and concurrent access.
- **Configuration**: All configurable parameters with type, default, constraints, and whether they require restart.

See `lld.md` for detailed LLD content standards when this section requires deep treatment.

### Alternatives Considered

- Include at least two genuine alternatives with pros, cons, and rejection rationale.
- If an alternative was prototyped or benchmarked, include the results.
- Strawman alternatives that exist only to make the chosen approach look good undermine the document.

### Security / Privacy / Compliance

- This section is **mandatory**. "No security implications" is almost never true.
- Address: authentication, authorization, input validation, data encryption (at rest and in transit), PII handling, audit logging.
- Identify trust boundaries in the architecture and what crosses them.
- Reference applicable compliance requirements (GDPR, SOC2, HIPAA, PCI-DSS).

### Reliability / Scalability / Performance

- How the system handles growth in traffic, data volume, and team size.
- Capacity estimates with back-of-envelope math.
- Horizontal vs vertical scaling strategy for each component.
- Failure modes with blast radius, detection, recovery, and data impact.
- Cascading failure and thundering herd mitigation.

### Observability

- Key metrics for each component: latency percentiles, error rates, throughput, saturation.
- Logging strategy: what is logged, at what level, where aggregated.
- Distributed tracing for cross-service request paths.
- Alerting thresholds tied to SLO targets.
- Dashboard definitions for normal operation and incident response.

### Testing Strategy

- Cover unit, integration, and end-to-end testing approaches.
- Include load/performance testing plans if the system has throughput requirements.
- Describe how the design supports testability (dependency injection, interface boundaries).
- Define acceptance criteria for each testing level.

### Migration / Rollout / Rollback

- Define deployment phases: canary, staged rollout, full release.
- Specify feature flags and kill-switch behavior.
- **Rollback strategy is required**: describe how to revert each phase, including data migration rollback.
- Define success criteria for each phase before proceeding to the next.
- Address backward compatibility and data backfill requirements.

### Risks and Mitigations

- Enumerate known risks with likelihood, impact, and mitigation plan.
- Include technical risks, operational risks, and timeline risks.
- Identify single points of failure and their mitigations.

### Open Questions

- Each question must have an owner and a target resolution date.
- Questions must be specific and actionable.

### Decision Log / ADR Links

- Record key decisions made during the design process.
- Link to ADRs for architecturally significant decisions.
- This creates the traceability chain: RFC -> Tech Spec -> ADR.

---

## 3. Scaling the Template

### Lightweight Tech Spec (1-3 pages)

For single-team, moderate-complexity changes. Typically maps to 2-6 story points.

Fill only: Metadata, Summary, Context, Goals, Non-Goals, Proposed Design (HLD), Testing Strategy, Rollout, Open Questions. Keep LLD minimal — a brief API description and schema change is sufficient.

### Heavyweight Tech Spec (10-20 pages)

For cross-team, high-impact changes. Typically maps to >6 story points or multi-sprint initiatives.

Fill all sections in depth. Use appendices for detailed schemas, benchmarks, and extended examples. The HLD and LLD sections may each be several pages long.

### Decision Criteria

| Signal | Lightweight | Heavyweight |
|--------|------------|-------------|
| Story points | 2-6 SP | >6 SP |
| Components touched | One or two | Multiple / cross-team |
| Risk level | Low-Medium | Medium-High |
| API / data changes | Moderate | Significant |
| Estimated dev time | 1-2 days | >3 days |

---

## 4. Common Issues

- **Solution masquerading as a problem statement**: The Context section describes the solution instead of the problem. Describe the pain point without mentioning any technology.
- **Missing rationale**: Decisions are stated without explanation. Every "we will use X" must be followed by "because Y."
- **HLD and LLD are out of sync**: The high-level architecture shows components that the detailed design does not cover, or vice versa.
- **Vague rollback plan**: "We can roll back if something goes wrong" is not a plan. Specify the mechanism, data implications, and decision criteria.
- **Security as an afterthought**: A one-line "we will use HTTPS" is not a security section. Address specific threats.
- **No capacity math**: Stating scale targets without showing how they were derived from the problem parameters.
- **Diagrams without text**: A diagram alone does not constitute a design section. Every diagram needs explanatory prose.

---

## 5. Review Checklist

- [ ] Metadata block is complete with document ID, status, owner, and dates
- [ ] Review tracking table lists named reviewers with roles
- [ ] Summary is one paragraph and conveys the full scope
- [ ] Problem statement describes the problem, not the solution
- [ ] Goals are specific and measurable
- [ ] Non-goals are stated and justified
- [ ] Requirements include quantified non-functional targets
- [ ] Current state is described with diagram if non-trivial
- [ ] HLD includes architecture diagram with labeled data flows
- [ ] Every diagrammed component is described in prose
- [ ] LLD covers APIs with typed schemas, not pseudocode
- [ ] Data model includes schema, indexes, and migration plan
- [ ] Security section addresses auth, data protection, and trust boundaries
- [ ] Reliability section includes capacity math and failure modes
- [ ] Observability covers metrics, logging, tracing, and alerting
- [ ] Testing strategy covers unit, integration, and e2e levels
- [ ] Rollout plan includes phased deployment and rollback strategy
- [ ] At least two genuine alternatives are evaluated
- [ ] Every design decision includes rationale
- [ ] Open questions have owners and target dates
- [ ] Decision log links to ADRs for significant decisions
- [ ] No TODO/TBD placeholders remain in the final version

---

## 6. Template

```markdown
# TS-NNN: <Title>

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Tech Spec |
| Document ID | TS-NNN |
| Status | Draft |
| Owner | <name> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Project / Initiative | <name or N/A> |
| Tracking Link(s) | <Jira / GitHub / Linear / N/A> |
| Target Milestone / Release | <milestone or N/A> |
| Related Docs | <links to RFC, ADRs, PRDs> |
| Repositories / Services | <repo or service names> |

## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## Summary

<One paragraph: what is changing and why.>

## Context / Problem Statement

<Current situation, pain point, business/technical driver. Link to originating RFC or PRD.>

## Goals

- <Specific, measurable goal>

## Non-Goals

- <What is explicitly excluded and why>

## Requirements and Constraints

### Functional Requirements
- <What the system does>

### Non-Functional Requirements
| Requirement | Target | Basis |
|-------------|--------|-------|
| Latency | p99 < 200ms | Current SLO |
| Throughput | 10K req/sec | Projected peak |

### Constraints
- <Compliance, timeline, dependency constraints>

## Current State

<Existing architecture, behavior, or workflow. Include diagram if non-trivial.>

## Proposed Design — High-Level (HLD)

### Architecture Overview
<Architecture diagram + explanation of components, responsibilities, and data flow.>

### Component Boundaries
| Component | Responsibility | Inputs | Outputs |
|-----------|---------------|--------|---------|
| | | | |

### External Dependencies
| System | Protocol | Failure Mode | Fallback |
|--------|----------|-------------|----------|
| | | | |

## Detailed Design (LLD)

### Component: <Name>
<Responsibility, internal structure, interfaces, dependencies.>

### API Contracts
<Full endpoint specs with method, path, schemas, error codes.>

### Data Model
<Schema definitions, indexes, migrations. Include ER diagram.>

### State Transitions
<State machine for complex entity lifecycles.>

### Error Handling
| Error Code | HTTP Status | Condition | Recovery |
|------------|-------------|-----------|----------|
| | | | |

### Configuration
| Parameter | Type | Default | Constraints | Restart Required |
|-----------|------|---------|-------------|-----------------|
| | | | | |

## Alternatives Considered

### Alternative 1: <Name>
<Approach, advantages, disadvantages, why rejected.>

### Alternative 2: <Name>
<Approach, advantages, disadvantages, why rejected.>

## Security / Privacy / Compliance

<Auth, data protection, trust boundaries, compliance requirements.>

## Reliability / Scalability / Performance

<Capacity estimates, scaling strategy, failure modes.>

## Observability

<Metrics, logging, tracing, alerting, dashboards.>

## Testing Strategy

| Level | Scope | Approach |
|-------|-------|----------|
| Unit | | |
| Integration | | |
| E2E | | |
| Load | | |

## Migration / Rollout / Rollback

### Deployment Phases
1. <Phase, success criteria, rollback trigger>

### Feature Flags
- <Flag name, purpose, kill-switch behavior>

### Rollback Plan
<How to revert each phase, data migration rollback.>

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| | | | |

## Open Questions

| # | Question | Owner | Target Date | Resolution |
|---|----------|-------|-------------|------------|
| 1 | | | | |

## Decision Log / ADR Links

| Decision | ADR | Date |
|----------|-----|------|
| | | |

## Appendix

<Detailed examples, extended schemas, benchmarks, additional diagrams.>
```
