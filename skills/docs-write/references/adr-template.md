# Architecture Decision Record (ADR) template

Optional reference loaded by `docs-write` when the deliverable is an ADR. ADRs document a single architectural decision, its context, the alternatives considered, and the consequences. They are append-only history — superseded ADRs are NOT deleted; they're marked superseded.

## When to write an ADR

Write an ADR for any decision that:

- Is hard to reverse (database choice, language, framework, message-passing pattern).
- Has long-lasting effects on multiple teams or modules.
- The team will want to remember the **why** for in 6 / 12 / 24 months.
- Trades off a real constraint (cost, latency, complexity, maintainer time).

Don't write an ADR for:

- Day-to-day implementation choices (use the spec or the PR description).
- Decisions covered by a public framework convention (just follow it).
- Trivial reversible decisions (variable names, file layout).

## File location

`docs/decisions/NNNN-short-title.md` — sequentially numbered, lowercase-kebab title.

Example: `docs/decisions/0007-use-postgresql-as-primary-datastore.md`.

## Template

```markdown
# ADR-NNNN: <Short title>

- Status: Proposed | Accepted | Deprecated | Superseded by ADR-MMMM
- Date: YYYY-MM-DD
- Deciders: <names / roles>
- Tags: <area, area>

## Context

<What is the situation that forced this decision? What are the constraints — performance, cost, team skill, time, infrastructure, regulatory, customer commitments? Cite numbers where possible. 1–3 paragraphs.>

## Decision

<The choice made, stated plainly. One paragraph; one or two sentences if you can.>

## Alternatives considered

<For each: the option, its main virtue, the reason it was NOT picked. Be specific. Vague rejections age badly.>

- **Option A — <name>.** <Virtue.> Rejected because <specific reason>.
- **Option B — <name>.** <Virtue.> Rejected because <specific reason>.
- **Option C — <name>.** <Virtue.> Rejected because <specific reason>.

## Consequences

### Positive

- <What does this decision unlock or improve?>
- <What gets cheaper / faster / safer?>

### Negative

- <What's the cost? Performance? Operational complexity? Onboarding overhead?>
- <What did we explicitly choose to live with?>

### Risks

- <What could go wrong over time? What signals should we watch for?>
- <If this decision is wrong, what does the recovery look like?>

## References

- <Link to RFC / spec / design doc that informed this.>
- <Link to PR that implemented it.>
- <Link to previously superseded ADR(s) if any.>
- <Link to external prior art / vendor docs / benchmark.>

## Revision history

- YYYY-MM-DD — Proposed by <name>.
- YYYY-MM-DD — Accepted.
- YYYY-MM-DD — Superseded by ADR-MMMM (link).
```

## Status lifecycle

```
Proposed ── Accepted ── (Deprecated | Superseded by ADR-NNNN)
```

- **Proposed** — drafted; under review.
- **Accepted** — the team has decided; this is the current direction.
- **Deprecated** — no longer the direction, no replacement. Useful when the area is being decommissioned.
- **Superseded** — replaced by a specific newer ADR. The newer ADR's number goes in the status line. The old ADR is NOT deleted — its history is the value.

## Writing tips

- Write for the reader who will land on this in 18 months without context. Define jargon. Link to definitions.
- Prefer concrete numbers ("p95 ≤ 200ms requirement", "store ≤ 50 GB") to vague adjectives ("fast", "cheap").
- Cite real evidence (benchmarks, prototypes, vendor pricing) for claims. "X is faster" without a number ages poorly.
- Honesty about the negative consequences is the hallmark of a good ADR. The agent should be HONEST not SUPPORTIVE.
- Keep it short — 1–3 pages. Long ADRs go unread.

## Anti-patterns

- ADRs that are just summaries of what was built ("we chose X and built it"). The decision and the alternatives are missing.
- ADRs with no "alternatives considered" section. Every real decision had alternatives; document them.
- ADRs that get deleted when superseded. Mark them, don't delete them — the history is the point.
- "We'll write the ADR after we ship" — by then the alternatives are forgotten and the rationale is reconstructed (badly).
- ADRs filed for trivial choices. They dilute the signal. Reserve for the real decisions.
- Long, hedged "consequences" sections that are afraid to commit. Be plain about both upside and downside.
