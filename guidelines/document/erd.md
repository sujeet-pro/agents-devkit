# Engineering Requirements Document (ERD) Guidelines

## 1. Purpose & Audience

This guideline defines how to write and review Engineering Requirements Documents. An ERD translates business needs into precise, testable engineering specifications that drive system design, implementation, and validation.

**Primary audience:** Engineers writing or reviewing ERDs, technical leads approving them, and QA teams deriving test plans from them.

**When to use:** Before starting design or implementation of any system, feature, or infrastructure change that affects production.

## 2. Required Sections

Every ERD must include the following sections in order:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Overview & Context | Why this document exists, what problem it solves, link to product requirements |
| 2 | Technical Requirements — Functional | What the system must do, described as testable behaviors |
| 3 | Technical Requirements — Non-Functional | Quality attributes: reliability, availability, maintainability |
| 4 | System Constraints | Infrastructure, budget, timeline, backward compatibility limits |
| 5 | Performance Requirements | Latency, throughput, and capacity targets with measurable thresholds |
| 6 | Security Requirements | Authentication, authorization, encryption, and compliance needs |
| 7 | Monitoring & Alerting Requirements | What to observe, threshold definitions, escalation paths |
| 8 | Capacity Planning | Current load, projected growth, scaling triggers |
| 9 | Compliance & Regulatory Requirements | Legal, regulatory, and policy obligations |
| 10 | Glossary & References | Term definitions and links to related documents |

## 3. Content Standards

### 3.1 Every Requirement Must Be Testable

Bad: "The system should be fast."
Good: "API responses must return within 200ms at p95 under 500 RPS sustained load."

Each requirement must answer: **How would someone verify this is met?** If you cannot write a test or define a measurement, the requirement is incomplete.

### 3.2 Use Structured Requirement Format

Each requirement should follow this pattern:

- **ID:** REQ-XXX (sequential, never reused)
- **Priority:** P0 (must-have) / P1 (should-have) / P2 (nice-to-have)
- **Description:** One clear sentence stating the requirement
- **Acceptance Criteria:** Measurable condition(s) that prove the requirement is met
- **Dependencies:** Other requirements or external systems this depends on

### 3.3 Constraints Must Be Explicit

State what you cannot change, not just what you want. Include:

- **Infrastructure constraints:** Cloud provider, region, existing services that must be reused
- **Budget constraints:** Dollar amounts or cost-per-unit ceilings, not "cost-effective"
- **Timeline constraints:** Hard deadlines with the reason they are hard
- **Compatibility constraints:** Which existing APIs, data formats, or clients must continue working

### 3.4 Performance Requirements Need Three Numbers

For every performance target, specify:

1. **Target:** The goal under normal conditions (e.g., p50 latency < 50ms)
2. **Threshold:** The maximum acceptable value before degradation is unacceptable (e.g., p99 latency < 500ms)
3. **Load profile:** The conditions under which these numbers apply (e.g., 1000 concurrent users, 80% reads)

### 3.5 Capacity Planning Must Include Growth

Do not state only current needs. Every capacity section must include:

- Current baseline load with measurement date
- Projected load at 6 months and 12 months with assumptions stated
- Scaling triggers: at what utilization percentage does scaling action begin?
- Cost implications of scaling at each projected milestone

## 4. Structure & Flow

Follow this logical progression:

1. **Start with context** — What business problem drives these requirements? Link to the product spec or RFC.
2. **Functional before non-functional** — Define what it does before defining how well it does it.
3. **Constraints before targets** — Establish boundaries before setting goals within them.
4. **Security and compliance together** — These often overlap; keep them close to avoid contradiction.
5. **Monitoring last** — You can only define what to monitor after you know the requirements and targets.

Group related requirements under clear subheadings. Number every requirement for traceability.

## 5. Common Issues

| Issue | Problem | Fix |
|-------|---------|-----|
| Vague performance targets | "Low latency" means different things to different people | Add specific percentile + value + load conditions |
| Missing failure modes | Only happy-path requirements | Add requirements for degraded operation, failover, and data loss limits |
| No priority ranking | Everything looks equally important | Assign P0/P1/P2; a document where everything is P0 has no priorities |
| Implicit constraints | Team assumes everyone knows the constraints | Write them down even if they seem obvious |
| Copy-pasted compliance | Generic GDPR/SOC2 text that does not apply | Tailor each compliance requirement to what this system specifically handles |
| No dependency mapping | Requirements reference other systems without stating the dependency | Add explicit dependency IDs and link to external system documentation |
| Stale capacity numbers | Baseline data is months old | Include the measurement date and require refresh if older than 30 days |

## 6. Review Checklist

Before approving an ERD, verify every item:

- [ ] Every requirement has a unique ID and priority level
- [ ] Every requirement has measurable acceptance criteria
- [ ] Functional requirements cover both success and failure scenarios
- [ ] Performance targets include target value, threshold value, and load profile
- [ ] System constraints are explicit with justification (not just "we prefer X")
- [ ] Security requirements specify authentication method, encryption standard, and data classification
- [ ] Monitoring section defines what is measured, alert thresholds, and who gets paged
- [ ] Capacity planning includes current baseline with date, 6-month and 12-month projections, and scaling triggers
- [ ] Compliance requirements are specific to this system, not generic boilerplate
- [ ] All cross-references to other documents or systems are valid links
- [ ] Glossary defines every domain-specific or ambiguous term
- [ ] No requirement uses unmeasurable words: "fast," "secure," "scalable," "reliable" without quantification
- [ ] Dependencies between requirements are documented and non-circular
- [ ] The document has a version number and last-updated date
