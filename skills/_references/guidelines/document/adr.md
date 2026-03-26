# Architecture Decision Record (ADR) Guidelines

Guidelines for writing and reviewing Architecture Decision Records. ADRs capture the context, decision, and consequences of architecturally significant choices so that future engineers understand not just what was decided, but why.

**Audience**: Engineers, architects, and technical leads who need to understand past decisions, evaluate whether they still hold, or make new decisions in the same problem space.

**When to use**: Use an ADR when the question is "what decision did we make, and why?" For pre-alignment on direction, use an RFC. For implementation detail, use a Tech Spec.

**References**:
- [Documenting Architecture Decisions — Michael Nygard (2011)](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — Original ADR format
- [About MADR v3 — adr.github.io](https://adr.github.io/madr/) — Markdown Any Decision Records extended format
- [The MADR Template Explained — Olaf Zimmermann](https://ozimmer.ch/practices/2022/11/22/MADRTemplatePrimer.html)
- [When Should I Write an ADR — Spotify Engineering](https://engineering.atspotify.com/2020/04/when-should-i-write-an-architecture-decision-record)
- [AWS Prescriptive Guidance: ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
- [ADR Templates — adr.github.io](https://adr.github.io/adr-templates/)
- [joelparkerhenderson/architecture-decision-record (GitHub)](https://github.com/joelparkerhenderson/architecture-decision-record)
- [Maintain an ADR — Microsoft Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record)
- [ADRs and RFCs: Their Differences — Candost Dagdeviren](https://candost.blog/adrs-rfcs-differences-when-which/)

---

## 1. Format & Numbering

- One ADR per file, stored in `docs/adr/`.
- File naming: `NNNN-short-slug.md` where `NNNN` is zero-padded sequential (e.g., `0001-use-postgresql-for-primary-store.md`).
- ADR identifiers follow the format `ADR-NNNN` (e.g., `ADR-0001`).
- Never reuse a number, even if the ADR is superseded or deprecated. The sequence is append-only.
- Keep the slug short but descriptive. It should convey the decision without opening the file.

---

## 2. Required Sections

Every ADR must include the following sections in order. ADRs should be short and durable — typically 0.5-2 pages.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Title | `ADR-NNNN: <Decision Title>` — imperative verb phrase |
| 2 | Metadata | Standard header with status, date, owner, reviewers |
| 3 | Context and Problem Statement | The forces at play and the problem requiring a decision |
| 4 | Decision Drivers | Key factors that influenced the choice |
| 5 | Considered Options | Options that were evaluated |
| 6 | Decision | The chosen option with justification |
| 7 | Consequences | Positive, negative, and neutral outcomes |

---

## 3. Optional Sections

Include when the ADR scope warrants them.

| Section | When to Include |
|---------|-----------------|
| **Alternatives Detail** | When options need detailed pros/cons analysis (MADR format) |
| **Confirmation** | How implementation compliance will be verified |
| **Compliance** | Regulatory, legal, or policy implications |
| **Related Docs** | Links to RFCs, Tech Specs, tickets, meeting notes |
| **Notes** | Additional context for future readers |

---

## 4. Content Standards

### Title

- Format: `ADR-NNNN: <Imperative verb phrase>`.
- The title should describe the decision, not the problem.
  - **Wrong**: `ADR-0003: Database Performance Issues`
  - **Right**: `ADR-0003: Use Read Replicas for Reporting Queries`
- Keep it under 80 characters.

### Metadata

Use a compact metadata block appropriate for ADRs. ADRs are lighter than RFCs and Tech Specs, so the metadata is streamlined.

```text
Status: Proposed | Accepted | Rejected | Deprecated | Superseded by ADR-NNNN
Date: YYYY-MM-DD
Owner: <name>
Decision-Makers: <list of people who approved/rejected>
Consulted: <SMEs with two-way communication>
Informed: <stakeholders with one-way updates>
Related Docs: <links to RFC, Tech Spec, tickets>
```

When the ADR goes through a formal review process (e.g., for significant or cross-team decisions), include the standard review tracking table from `document-metadata.md`.

### Context and Problem Statement

- Describe the situation that requires a decision. What is the issue? What forces are at play?
- Include technical constraints, business constraints, team constraints, and timeline pressures.
- Reference prior art: what was tried before, what adjacent teams do, what the industry converges on.
- Be objective. The context section presents the problem space; it does not argue for a solution.
- Link to related tickets, RFCs, design docs, or previous ADRs that inform this decision.
- Length: 2-5 sentences for simple decisions; a few paragraphs for complex ones.

### Decision Drivers

- Bullet list of the key factors that influenced the choice.
- Examples: desired quality attribute, technical constraint, team expertise, timeline pressure, compliance requirement.
- These frame the evaluation criteria for the considered options.

### Considered Options

- List all options that were seriously evaluated.
- Include at least two options. A decision with only one option is not a decision.
- Brief description (1-2 sentences) of each option.

### Decision

- State the decision clearly and specifically. Name the technology, pattern, or approach chosen.
- Use active voice: "We will use..." not "It was decided..."
- Be precise enough that two engineers reading the ADR would implement the same thing.
  - **Vague**: "We will use a message queue."
  - **Specific**: "We will use Apache Kafka (managed via Confluent Cloud) as the event bus for inter-service communication. Topics will be partitioned by tenant ID. Consumers will use consumer groups with at-least-once delivery semantics."
- State the justification referencing the decision drivers: "Chosen because [driver 1] and [driver 2]."

### Consequences

- Enumerate outcomes in three explicit categories:
  - **Positive**: What improves, what becomes possible, what risk is mitigated.
  - **Negative**: What gets harder, what new risks are introduced, what costs increase.
  - **Neutral**: Side effects that are neither good nor bad but worth noting (e.g., "Team will need training on Kafka").
- Be honest about the negatives. An ADR that lists only positive consequences is incomplete.
- Include operational consequences: what changes for deployment, monitoring, on-call, runbooks.
- Note if subsequent ADRs or follow-up work will be needed.

---

## 5. Status Lifecycle

Follow the ADR status lifecycle defined in `document-metadata.md`:

```
Proposed --> Accepted --> Superseded (by ADR-NNNN)
         \            \--> Deprecated
          \--> Rejected
```

**Critical rules:**
- **ADRs are immutable after acceptance.** To change a decision, create a new ADR and mark the old one as Superseded.
- **Never delete an ADR.** Even rejected ADRs provide value by documenting what was considered and why it was not adopted.
- When an ADR is superseded, add a link to the replacement: `Superseded by [ADR-0012](0012-switch-to-vitess.md)`.
- When an ADR is deprecated, state why the decision is no longer relevant.
- Include the date of the most recent status change: `Accepted (2026-03-15)`.

---

## 6. When to Write an ADR

Based on Spotify's guidance, write an ADR when:

1. **Choosing a technology**: Database, message broker, framework, library, language for a new component.
2. **Choosing an architecture pattern**: SSR vs CSR, microservices vs monolith, event-driven vs request-driven.
3. **Infrastructure decisions**: CDN strategy, caching layer, deployment topology, cloud provider selection.
4. **Backfilling**: A "blessed" solution exists but was never documented — capture it now.
5. **After large changes**: Following an RFC process, extract the concluded decisions into ADRs.
6. **Small but sticky decisions**: Even lightweight choices compound into problems when undocumented.

The default should be documentation rather than silence. If you are unsure whether a decision warrants an ADR, it probably does.

---

## 7. Common Issues

- **Decision disguised as context**: The Context section argues for a solution instead of presenting the problem objectively. Move the argument to the Decision section.
- **Vague decisions**: "We will use caching" is not a decision. Specify what cache, what strategy, and what data.
- **No negative consequences**: Every decision has trade-offs. If the Consequences section is all positive, the analysis is incomplete.
- **Stale status**: An ADR marked Proposed that was accepted months ago. Keep statuses current.
- **Missing links**: ADRs exist in a web of decisions. Failing to link related ADRs means readers must rediscover connections.
- **Too long**: An ADR exceeding two pages is likely conflating the decision record with a design document. Keep the ADR focused; link to the Tech Spec for detailed analysis.
- **No decision drivers**: Without stating what factors mattered, reviewers cannot evaluate whether the right option was chosen.

---

## 8. Review Checklist

- [ ] Title uses imperative verb phrase and is under 80 characters
- [ ] Status is one of: Proposed, Accepted, Rejected, Deprecated, Superseded
- [ ] Status includes a date
- [ ] If superseded, the replacement ADR is linked
- [ ] Owner and decision-makers are named
- [ ] Context describes forces and constraints without arguing for a solution
- [ ] Decision drivers are listed as explicit evaluation criteria
- [ ] At least two options were considered
- [ ] Decision is specific enough that two engineers would implement the same thing
- [ ] Decision references the decision drivers in its justification
- [ ] Consequences include positive, negative, and neutral outcomes
- [ ] Operational consequences (deploy, monitor, on-call) are addressed
- [ ] Related ADRs, RFCs, Tech Specs, and tickets are linked
- [ ] File name follows `NNNN-short-slug.md` convention
- [ ] ADR number is sequential and not reused
- [ ] ADR is 0.5-2 pages (not a disguised Tech Spec)
- [ ] No TODO/TBD placeholders remain

---

## 9. Template

```markdown
# ADR-NNNN: <Decision Title — Imperative Verb Phrase>

## Metadata

| Field | Value |
|-------|-------|
| Status | Proposed |
| Date | YYYY-MM-DD |
| Owner | <name> |
| Decision-Makers | <names> |
| Consulted | <SME names> |
| Informed | <stakeholder names> |
| Related Docs | <links to RFC, Tech Spec, tickets, prior ADRs> |

## Review Tracker

<Include for significant or cross-team decisions. Omit for lightweight, single-team decisions.>

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## Context and Problem Statement

<What is the issue? What forces are at play? What constraints exist?
Reference related ADRs, tickets, and design docs. Be objective.>

## Decision Drivers

- <Driver 1: e.g., desired quality attribute>
- <Driver 2: e.g., technical constraint>
- <Driver 3: e.g., team expertise>

## Considered Options

1. <Option 1: brief description>
2. <Option 2: brief description>
3. <Option 3: brief description>

## Decision

Chosen option: "<Option N>", because <justification referencing decision drivers>.

<Additional detail on the specific technology, pattern, or approach.
Be precise enough that two engineers would implement the same thing.>

## Consequences

### Positive

- <What improves or becomes possible>

### Negative

- <What gets harder, riskier, or more costly>

### Neutral

- <Side effects worth noting; follow-up work needed>

## Links

- RFC: <link if applicable>
- Tech Spec: <link if applicable>
- Related ADR: [ADR-NNNN](NNNN-slug.md)
- Ticket: <tracking link>
```
