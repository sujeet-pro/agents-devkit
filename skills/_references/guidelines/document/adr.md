# Architecture Decision Record (ADR) Guidelines

Guidelines for writing and reviewing Architecture Decision Records. ADRs capture the context, decision, and consequences of architecturally significant choices so that future engineers understand not just what was decided, but why.

**Audience**: Engineers, architects, and technical leads who need to understand past decisions, evaluate whether they still hold, or make new decisions in the same problem space.

**Reference**: Based on Michael Nygard's original ADR format ([Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)).

---

## 1. Format & Numbering

- One ADR per file, stored in `docs/adr/`.
- File naming: `NNNN-short-slug.md` where `NNNN` is zero-padded sequential (e.g., `0001-use-postgresql-for-primary-store.md`).
- ADR identifiers follow the format `ADR-NNNN` (e.g., `ADR-0001`).
- Never reuse a number, even if the ADR is superseded or deprecated. The sequence is append-only.
- Keep the slug short but descriptive. It should convey the decision without opening the file.

---

## 2. Required Sections

Every ADR must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Title | `ADR-NNNN: <Decision Title>` |
| 2 | Status | Current lifecycle state |
| 3 | Context | The forces at play and the problem that demands a decision |
| 4 | Decision | The change being made, stated specifically |
| 5 | Consequences | Outcomes of the decision: positive, negative, and neutral |

---

## 3. Content Standards

### Title

- Format: `ADR-NNNN: <Imperative verb phrase>`.
- The title should describe the decision, not the problem.
  - **Wrong**: `ADR-0003: Database Performance Issues`
  - **Right**: `ADR-0003: Use Read Replicas for Reporting Queries`
- Keep it under 80 characters.

### Status

- One of the following values: **Proposed**, **Accepted**, **Deprecated**, **Superseded**.
- Status lifecycle:
  ```
  Proposed → Accepted → [Deprecated | Superseded by ADR-NNNN]
  ```
- When an ADR is superseded, include the link to the replacement: `Superseded by [ADR-0012](0012-switch-to-vitess.md)`.
- When an ADR is deprecated, state why the decision is no longer relevant.
- Include the date of the most recent status change: `Accepted (2024-09-15)`.

### Context

- Describe the situation that requires a decision. What is the issue? What forces are at play?
- Include technical constraints, business constraints, team constraints, and timeline pressures.
- Reference prior art: what was tried before, what adjacent teams do, what the industry converges on.
- Be objective. The context section presents the problem space; it does not argue for a solution.
- Link to related tickets, RFCs, design docs, or previous ADRs that inform this decision.

### Decision

- State the decision clearly and specifically. Name the technology, pattern, or approach chosen.
- Be precise enough that two engineers reading the ADR would implement the same thing.
  - **Vague**: "We will use a message queue."
  - **Specific**: "We will use Apache Kafka (managed via Confluent Cloud) as the event bus for inter-service communication. Topics will be partitioned by tenant ID. Consumers will use consumer groups with at-least-once delivery semantics."
- If the decision involves choosing among alternatives, briefly name the alternatives considered and state why they were rejected. Keep this concise; the detailed analysis belongs in the Context section or a linked design doc.

### Consequences

- Enumerate outcomes in three explicit categories:
  - **Positive**: What improves, what becomes possible, what risk is mitigated.
  - **Negative**: What gets harder, what new risks are introduced, what costs increase.
  - **Neutral**: Side effects that are neither good nor bad but worth noting (e.g., "Team will need training on Kafka").
- Be honest about the negatives. An ADR that lists only positive consequences is incomplete.
- Include operational consequences: what changes for deployment, monitoring, on-call, runbooks.

---

## 4. Optional Sections

These sections are not required but are recommended when applicable.

| Section | When to Include |
|---------|-----------------|
| **Alternatives Considered** | When the decision involved evaluating multiple options with non-obvious trade-offs |
| **Links** | When related ADRs, tickets, design docs, or external references exist |
| **Notes** | When reviewers or future readers need additional context that does not fit elsewhere |
| **Compliance** | When the decision has regulatory, legal, or policy implications |

---

## 5. Template

```markdown
# ADR-NNNN: <Decision Title>

## Status

Proposed | Accepted | Deprecated | Superseded by [ADR-NNNN](NNNN-slug.md)

Date: YYYY-MM-DD

## Context

<What is the issue? What forces are at play? What constraints exist?
Reference related ADRs, tickets, and design docs.>

## Decision

<What is the change? Be specific about the technology, pattern, or approach chosen.
If alternatives were considered, name them briefly and state why they were not chosen.>

## Consequences

### Positive
- <What improves>

### Negative
- <What gets harder or riskier>

### Neutral
- <Side effects worth noting>

## Links

- Related: [ADR-0003](0003-slug.md)
- Ticket: PROJ-1234
- Design doc: <link>
```

---

## 6. Common Issues

- **Decision disguised as context**: The Context section argues for a solution instead of presenting the problem objectively. Move the argument to the Decision section.
- **Vague decisions**: "We will use caching" is not a decision. Specify what cache (Redis, Memcached, application-level), what strategy (write-through, write-behind, cache-aside), and what data is cached.
- **No negative consequences**: Every decision has trade-offs. If the Consequences section is all positive, the analysis is incomplete.
- **Stale status**: An ADR marked Proposed that was accepted months ago. Keep statuses current.
- **Missing links**: ADRs exist in a web of decisions. Failing to link related ADRs means readers must rediscover connections themselves.
- **Too long**: An ADR that exceeds two pages is likely conflating the decision record with a design document. Keep the ADR focused; link to the full design doc for detailed analysis.

---

## 7. Review Checklist

- [ ] Title uses imperative verb phrase and is under 80 characters
- [ ] Status is one of: Proposed, Accepted, Deprecated, Superseded
- [ ] Status includes a date
- [ ] If superseded, the replacement ADR is linked
- [ ] Context describes forces and constraints without arguing for a solution
- [ ] Decision is specific enough that two engineers would implement the same thing
- [ ] Alternatives are named with reasons for rejection
- [ ] Consequences include positive, negative, and neutral outcomes
- [ ] Operational consequences (deploy, monitor, on-call) are addressed
- [ ] Related ADRs, tickets, and docs are linked
- [ ] File name follows `NNNN-short-slug.md` convention
- [ ] ADR number is sequential and not reused
- [ ] No TODO/TBD placeholders remain
