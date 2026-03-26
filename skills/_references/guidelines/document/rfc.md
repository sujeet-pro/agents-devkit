# RFC (Request for Comments) Guidelines

Guidelines for writing and reviewing RFCs. An RFC is a written proposal that captures a plan, circulates it for feedback, and collects approvals before committing to a design or implementation direction.

**Audience**: Engineering teams, architects, tech leads, and stakeholders who need to evaluate whether a proposal should be pursued and in which direction.

**When to use**: Use an RFC when the question is "should we do this, and which direction should we choose?" For implementation detail, use a Tech Spec. For recording a final decision, use an ADR.

**References**:
- [Scaling Engineering Teams via RFCs — Gergely Orosz (Pragmatic Engineer)](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- [Design Docs at Google — Malte Ubl](https://www.industrialempathy.com/posts/design-docs-at-google/)
- [Template for Writing Technical RFC Docs — Lambros Petrou](https://www.lambrospetrou.com/articles/rfc-template/)
- [A Structured RFC Process — Phil Calcado](https://philcalcado.com/2018/11/19/a_structured_rfc_process.html)
- [Rust RFC Template](https://github.com/rust-lang/rfcs/blob/master/0000-template.md)
- [Sourcegraph RFC Process](https://github.com/sourcegraph/handbook/blob/main/content/company-info-and-process/communication/rfcs/index.md)
- [HashiCorp RFC Template](https://www.hashicorp.com/en/how-hashicorp-works/articles/rfc-template)
- [The Power of "Yes, if" — Squarespace Engineering](https://engineering.squarespace.com/blog/2019/the-power-of-yes-if)
- [InnerSource: Transparent Cross-Team Decision Making Using RFCs](https://patterns.innersourcecommons.org/p/transparent-cross-team-decision-making-using-rfcs)

---

## 1. Required Sections

Every RFC must include the following sections in order. The RFC should be concise — typically 2-5 pages. If it grows beyond that, consider whether the detail belongs in a separate Tech Spec.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Metadata | Standard header with review tracking (see `document-metadata.md`) |
| 2 | Summary | One-paragraph executive overview |
| 3 | Motivation / Problem Statement | Why this matters now; the current pain point or gap |
| 4 | Goals | What this proposal achieves |
| 5 | Non-Goals | What this proposal explicitly does not address |
| 6 | Proposal | The recommended direction with enough detail to evaluate |
| 7 | Alternatives Considered | Other approaches with trade-offs and rejection rationale |
| 8 | Impact Analysis | Engineering, product, security, compliance, cost, and infrastructure impact |
| 9 | Rollout Approach | How the change will be introduced (high-level) |
| 10 | Open Questions | Unresolved issues that need stakeholder input |
| 11 | Decision Requested | Explicitly state what decision the reviewers are being asked to make |

---

## 2. Optional Sections

Include these when the RFC scope warrants them.

| Section | When to Include |
|---------|----------------|
| **Prior Art** | When the proposal relates to patterns used by other teams, companies, or open-source projects |
| **Timeline / Milestones** | Multi-phase projects spanning more than one sprint |
| **Architecture Changes** | When the proposal alters the system-level architecture |
| **Security / Compliance** | When user data, authentication, or regulatory requirements are affected |
| **Testing & Validation** | When the proposal needs a specific validation strategy before full rollout |
| **UI/UX Considerations** | When the proposal has user-facing changes |
| **FAQ** | Pre-populate with anticipated questions, then update from reviewer feedback |
| **Drawbacks** | When the proposal has significant known downsides that reviewers should weigh |

---

## 3. Content Standards

### Metadata

Follow the standard metadata block and review tracking table defined in `document-metadata.md`. Use the RFC status lifecycle: Draft -> In Review -> Approved -> In Progress -> Completed.

### Summary

- One paragraph, readable by any engineer in the organization.
- Must convey the problem, the proposed direction, and the expected outcome.
- A reader who only reads the Summary should understand what the RFC is about and what is being asked of them.

### Motivation / Problem Statement

- Describe the current situation and the pain point that makes a change necessary.
- Include quantitative data when available: error rates, latency numbers, customer complaints, cost figures.
- Be objective. Present the problem without arguing for a specific solution.
- Reference prior attempts to solve this problem if any exist.

### Goals

- Each goal must be specific and verifiable. "Improve reliability" is not a goal; "Reduce service error rate from 2% to 0.1%" is.
- Goals define the success criteria for the proposal.

### Non-Goals

- Explicitly state what this RFC does not address.
- Non-goals prevent scope creep during review and implementation.
- If a topic is frequently raised in discussion but is out of scope, add it here.

### Proposal

- Start with a high-level overview (one paragraph) before diving into detail.
- Include 1-2 diagrams showing the proposed architecture or flow.
- Present enough technical detail for reviewers to evaluate the direction, but defer implementation-level detail to a Tech Spec.
- When the proposal involves choosing between approaches, present the recommended approach as the primary proposal and the alternatives in the Alternatives section.

### Alternatives Considered

- Include at least two genuine alternatives. Strawman alternatives that exist only to make the proposal look good undermine the document.
- For each alternative: describe the approach, its advantages, its disadvantages, and why it was not chosen.
- If an alternative was prototyped or benchmarked, include the results.

### Impact Analysis

Evaluate impact across these dimensions:

| Dimension | What to Address |
|-----------|----------------|
| **Engineering** | Effort estimate, team dependencies, migration complexity |
| **Product / Business** | User-facing changes, feature availability, business metrics |
| **Security / Compliance** | Data handling changes, new attack surfaces, regulatory requirements |
| **Cost / Infrastructure** | Cloud spend, licensing, hardware, operational overhead |
| **Operational** | On-call impact, monitoring changes, runbook updates |

### Rollout Approach

- High-level phases for introducing the change (e.g., canary, staged rollout, full release).
- Feature flags and kill-switch strategy.
- Backward compatibility considerations.
- This section should be directional. The detailed rollout plan belongs in the Tech Spec.

### Open Questions

- Each question must be specific enough that someone can answer it.
- Assign an owner and target resolution date when possible.
- "What about scaling?" is too vague; "Should we partition by tenant ID or timestamp?" is actionable.

### Decision Requested

- Explicitly state what decision the reviewers are being asked to make.
- Example: "We are requesting approval to proceed with Option A (event-driven architecture) and begin writing a Tech Spec."

---

## 4. Common Issues

- **Solution disguised as motivation**: The Motivation section argues for a specific solution instead of presenting the problem objectively. Keep motivation and proposal separate.
- **Too much implementation detail**: An RFC that specifies database schemas, API payloads, and class hierarchies is doing the Tech Spec's job. Stay at the "direction" level.
- **Missing non-goals**: Without explicit non-goals, reviewers raise scope questions that derail the discussion.
- **Alternatives are strawmen**: Only one alternative is seriously considered; the others are obviously inferior. Include genuine alternatives with real trade-offs.
- **No decision requested**: The RFC ends without stating what the readers are being asked to decide. Always close with a clear ask.
- **Empty review tracker**: The review tracking table is present but no reviewers are named. Identify reviewers before moving to In Review status.

---

## 5. Review Checklist

- [ ] Metadata block is complete with document ID, status, owner, and dates
- [ ] Review tracking table lists named reviewers with roles
- [ ] Summary is one paragraph and conveys the full picture
- [ ] Motivation describes the problem without arguing for a solution
- [ ] Goals are specific and verifiable
- [ ] Non-goals are stated to prevent scope creep
- [ ] Proposal includes at least one diagram
- [ ] Proposal stays at the "direction" level, not implementation detail
- [ ] At least two genuine alternatives are evaluated with trade-offs
- [ ] Impact analysis covers engineering, product, security, cost, and operations
- [ ] Rollout approach describes phased introduction
- [ ] Open questions are specific with owners where possible
- [ ] Decision requested is explicitly stated
- [ ] No TODO/TBD placeholders remain in the final version
- [ ] Document is 2-5 pages (not a disguised Tech Spec)

---

## 6. Template

```markdown
# RFC-NNN: <Title>

## Metadata

| Field | Value |
|-------|-------|
| Document Type | RFC |
| Document ID | RFC-NNN |
| Status | Draft |
| Owner | <name> |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Project / Initiative | <name or N/A> |
| Tracking Link(s) | <Jira / GitHub / Linear / N/A> |
| Related Docs | <links to related Tech Specs, ADRs, PRDs> |

## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## Summary

<One paragraph: what is being proposed, why, and what outcome is expected.>

## Motivation / Problem Statement

<Current situation, pain point, and quantitative impact. No solution arguments here.>

## Goals

- <Specific, verifiable goal 1>
- <Specific, verifiable goal 2>

## Non-Goals

- <What this RFC explicitly does not address>

## Proposal

<High-level overview paragraph, then detailed proposal with diagrams.>

## Alternatives Considered

### Alternative 1: <Name>

<Description, advantages, disadvantages, and why it was not chosen.>

### Alternative 2: <Name>

<Description, advantages, disadvantages, and why it was not chosen.>

## Impact Analysis

| Dimension | Impact |
|-----------|--------|
| Engineering | <effort, dependencies, migration> |
| Product / Business | <user-facing changes, metrics> |
| Security / Compliance | <data handling, regulatory> |
| Cost / Infrastructure | <cloud spend, licensing> |
| Operational | <on-call, monitoring, runbooks> |

## Rollout Approach

<High-level phases, feature flags, backward compatibility.>

## Open Questions

| # | Question | Owner | Target Date |
|---|----------|-------|-------------|
| 1 | <specific question> | <name> | YYYY-MM-DD |

## Decision Requested

<Explicitly state what approval or direction is being sought.>
```
