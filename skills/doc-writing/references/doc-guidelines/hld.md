# High Level Design (HLD) Guidelines

Guidelines for writing and reviewing High Level Design sections. An HLD describes the architecture of a system at a level that stakeholders, architects, and engineers from adjacent teams can understand without deep domain expertise.

**Important**: HLD is typically a **section within a Tech Spec**, not a separate document. Use these guidelines when writing the "Proposed Design — High-Level (HLD)" section of a Tech Spec (see `tdd.md`). Create a standalone HLD document only when the system is large enough that the architecture overview requires its own review audience separate from the implementation details.

**Audience**: Engineering leadership, architects, cross-team engineers, and technical program managers who need to understand the system's shape and constraints without implementation details.

**References**:
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [HLD vs LLD — GeeksforGeeks](https://www.geeksforgeeks.org/system-design/difference-between-high-level-design-and-low-level-design/)

---

## 1. Required Sections

Every HLD must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | System Context | Where the system sits in the broader ecosystem. |
| 2 | Architecture Overview | High-level component layout with diagram. |
| 3 | Component Descriptions | Responsibility and scope of each component. |
| 4 | Integration Points | How the system connects to external systems and services. |
| 5 | Non-Functional Requirements | Performance, scalability, availability, and security targets. |
| 6 | Technology Choices | Key technology selections with justification. |
| 7 | Deployment Architecture | How the system is deployed and operated. |
| 8 | Monitoring & Observability | How the system's health and behavior are observed. |

---

## 2. Content Standards

### System Context
- Include a context diagram (C4 Level 1 or equivalent) showing the system as a single box surrounded by its users and external dependencies.
- Identify all actors: human users, external systems, batch processes, and third-party services.
- Describe the nature of each interaction (synchronous API call, async messaging, file transfer, etc.).

### Architecture Overview
- Include a container diagram (C4 Level 2 or equivalent) showing the major components and their relationships.
- Focus on **what** each component does and **why** it exists as a separate unit, not **how** it is implemented internally.
- Show data flow direction on all connections between components.
- Keep the diagram to 5-10 components. If you need more, group related components into subsystems and create separate diagrams for each.

### Component Descriptions
- Each component identified in the architecture diagram must have a description that covers:
  - **Responsibility**: What this component owns (one to two sentences).
  - **Inputs and outputs**: What data it consumes and produces.
  - **Boundaries**: What this component does NOT do (to prevent ambiguity about ownership).
- Components should have single, clear responsibilities. If a component description requires "and" more than once, consider splitting it.

### Integration Points
- For each external system integration, document:
  - Protocol and communication pattern (REST, gRPC, message queue, etc.).
  - Data format and contract ownership (who owns the schema).
  - Failure modes and fallback behavior (what happens when the dependency is unavailable).
  - SLA expectations for the dependency.
- Distinguish between dependencies the system **requires** (hard dependencies) and those it can **degrade without** (soft dependencies).

### Non-Functional Requirements
- NFRs must have **measurable targets**, not vague aspirations.

| NFR Category | Bad Example | Good Example |
|---|---|---|
| Performance | "The system should be fast" | "API responses under 200ms at p95" |
| Scalability | "Handle growth" | "Support 10K concurrent users, scaling to 50K within 12 months" |
| Availability | "Highly available" | "99.95% uptime (21.9 minutes downtime/month max)" |
| Security | "Must be secure" | "All data encrypted at rest (AES-256) and in transit (TLS 1.3)" |

- Include capacity estimates: expected request rates, data volumes, and storage growth.
- State the basis for each target (current metrics, business requirements, or SLA commitments).

### Technology Choices
- For each major technology decision (language, framework, database, message broker, cloud service), provide:
  - **What** was chosen.
  - **Why** it was chosen over alternatives (team expertise, performance characteristics, ecosystem support, licensing).
  - **Trade-offs** acknowledged (known limitations or risks of the choice).
- Do not justify choices by popularity alone. "Industry standard" is context, not justification.

### Deployment Architecture
- Include a deployment diagram showing where components run (cloud regions, availability zones, clusters, serverless functions).
- Describe the deployment topology: single-region vs multi-region, active-active vs active-passive.
- Document scaling strategy: horizontal vs vertical, auto-scaling triggers, and limits.
- Describe disaster recovery approach: RPO (Recovery Point Objective) and RTO (Recovery Time Objective).

### Monitoring & Observability
- Define the three pillars for this system:
  - **Metrics**: Key performance indicators (latency, throughput, error rate, saturation) and where they are collected.
  - **Logging**: What is logged, at what level, and where logs are aggregated.
  - **Tracing**: Distributed tracing strategy for cross-service requests.
- Define alerting thresholds tied to the NFR targets from Section 5.
- Describe dashboards or runbooks that operators will use during incidents.

---

## 3. Structure & Flow

- An HLD is a communication tool first. Optimize for clarity over completeness.
- A reader unfamiliar with the domain should understand the system's purpose and shape after reading Sections 1-3.
- Use consistent terminology. Define a glossary at the top if the domain has specialized terms.
- Diagrams are primary; text supports and explains the diagrams. Every diagram must be referenced and explained in the surrounding text.
- Avoid implementation details. If you are specifying class names, SQL queries, or API payloads, you have gone too deep. Defer those to the LLD.

---

## 4. Common Issues

- **Too much implementation detail**: The HLD reads like code documentation. Remember: "what" and "why", not "how."
- **Missing failure modes**: The document describes the happy path but ignores what happens when components or dependencies fail.
- **NFRs without numbers**: Qualitative requirements like "fast" and "reliable" are not actionable. Every NFR needs a target and a measurement method.
- **Orphan components**: A component appears in the diagram but is never described in text, or vice versa.
- **Technology choices without trade-offs**: Every technology has downsides. Acknowledging them builds credibility and helps future decision-making.

---

## 5. Review Checklist

- [ ] System context diagram is present and shows all external actors
- [ ] Architecture diagram shows 5-10 components with labeled data flows
- [ ] Every diagrammed component has a text description with responsibility, inputs/outputs, and boundaries
- [ ] Integration points document protocol, failure modes, and SLA expectations
- [ ] All NFRs have measurable targets with a stated basis
- [ ] Capacity estimates are included (request rates, data volumes, storage growth)
- [ ] Technology choices include justification and acknowledged trade-offs
- [ ] Deployment diagram shows regions, scaling strategy, and DR approach
- [ ] Monitoring covers metrics, logging, and tracing
- [ ] Alerting thresholds are tied to NFR targets
- [ ] Document is understandable by someone outside the immediate team
- [ ] No implementation details that belong in an LLD
- [ ] No TODO/TBD placeholders remain in the final version
