# Technical Design Document (TDD) Guidelines

Guidelines for writing and reviewing Technical Design Documents. A TDD captures the engineering approach to solving a well-defined problem, with enough detail that reviewers can evaluate trade-offs and implementers can begin work.

**Audience**: Engineers, tech leads, and architects who will build or review the proposed system.

---

## 1. Required Sections

Every TDD must include the following sections in order. Omitting a section requires an explicit justification in the document itself.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Problem Statement | What problem are we solving and why now? |
| 2 | Goals & Non-Goals | What this design achieves and what it explicitly does not. |
| 3 | Proposed Solution | High-level description of the chosen approach. |
| 4 | Technical Architecture | System components, interactions, and diagrams. |
| 5 | API Contracts | Interface definitions for all service boundaries. |
| 6 | Data Model | Schema definitions, entity relationships, storage choices. |
| 7 | Security Considerations | Threat model, authentication, authorization, data protection. |
| 8 | Testing Strategy | How the design will be validated at each level. |
| 9 | Rollout Plan | Phased deployment, feature flags, rollback strategy. |
| 10 | Alternatives Considered | Other approaches evaluated and why they were rejected. |
| 11 | Open Questions | Unresolved decisions that need input before or during implementation. |

---

## 2. Content Standards

### Problem Statement
- Must describe the problem from the user or system perspective, not the solution.
- Include quantitative impact where possible (error rates, latency, revenue loss).
- Link to the originating PRD, incident, or feature request.

### Goals & Non-Goals
- Goals must be specific and verifiable. "Improve performance" is not a goal; "Reduce p99 latency to under 200ms" is.
- Non-goals prevent scope creep. State what this design intentionally leaves out and why.

### Proposed Solution
- Start with a one-paragraph summary before diving into details.
- Include a system context diagram showing where the new component fits into the existing architecture.

### Technical Architecture
- Must include at least one architecture diagram (C4 context or container level).
- Diagrams must use a consistent notation (Mermaid, PlantUML, or Excalidraw with a legend).
- Every component in the diagram must be described in the text.

### API Contracts
- Define method, path, request schema, response schema, and error codes for every endpoint.
- Use typed schemas (OpenAPI, Protobuf, or equivalent). Pseudocode is not acceptable.
- Specify authentication and rate-limiting requirements per endpoint.

### Data Model
- Include an entity-relationship diagram for new or modified tables.
- Document column types, constraints, indexes, and partitioning strategy.
- Describe data lifecycle: creation, updates, archival, and deletion.
- Address data migration for schema changes to existing tables.

### Security Considerations
- This section is **mandatory**, not optional. "No security implications" is almost never true.
- Address: authentication, authorization, input validation, data encryption (at rest and in transit), PII handling, and audit logging.
- Identify the trust boundaries in the architecture and what crosses them.

### Testing Strategy
- Cover unit, integration, and end-to-end testing approaches.
- Describe how the design supports testability (dependency injection, interface boundaries).
- Include load/performance testing plans if the system has throughput requirements.

### Rollout Plan
- Define deployment phases (e.g., canary, staged rollout, full release).
- Specify feature flags and their kill-switch behavior.
- **Rollback strategy is required**: describe how to revert each phase, including data migration rollback.
- Define success criteria for each phase before proceeding to the next.

### Alternatives Considered
- Include at least two genuine alternatives. Strawman alternatives that exist only to make the chosen approach look good undermine the document.
- For each alternative, describe: the approach, its advantages, its disadvantages, and why it was not chosen.
- If an alternative was prototyped or benchmarked, include the results.

### Open Questions
- Each question must have an owner and a target resolution date.
- Questions should be specific enough that someone can answer them. "What about scaling?" is too vague; "Should we partition the events table by tenant ID or timestamp?" is actionable.

---

## 3. Structure & Flow

- The document should be readable top-to-bottom. A reviewer should not need to jump around to understand the proposal.
- Every design decision must include its **rationale**. Stating what was decided without explaining why is insufficient.
- Cross-reference related sections explicitly: "See Section 7 for the security implications of this API design."
- Keep the main document focused. Move lengthy schemas, benchmarks, or reference data to appendices.

---

## 4. Common Issues

- **Solution masquerading as a problem statement**: The problem section describes the solution instead of the actual problem. Fix: describe the pain point without mentioning any technology.
- **Missing rationale**: Decisions are stated without explanation. Every "we will use X" must be followed by "because Y."
- **Vague rollback plan**: "We can roll back if something goes wrong" is not a plan. Specify the mechanism, data implications, and decision criteria.
- **Security as an afterthought**: A one-line "we will use HTTPS" is not a security section. Address the specific threats to this system.
- **Diagrams without text**: A diagram alone does not constitute an architecture section. Every diagram needs explanatory text.

---

## 5. Review Checklist

- [ ] Problem statement describes the problem, not the solution
- [ ] Goals are specific and measurable
- [ ] Non-goals are stated and justified
- [ ] Architecture diagram is present and matches the text
- [ ] All components in diagrams are described in prose
- [ ] API contracts use typed schemas, not pseudocode
- [ ] Data model includes an ER diagram and migration plan
- [ ] Security section addresses authentication, authorization, and data protection
- [ ] Testing strategy covers unit, integration, and e2e levels
- [ ] Rollout plan includes phased deployment and rollback strategy
- [ ] At least two genuine alternatives are evaluated
- [ ] Every design decision includes rationale
- [ ] Open questions have owners and target dates
- [ ] No TODO/TBD placeholders remain in the final version
