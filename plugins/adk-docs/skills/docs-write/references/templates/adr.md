# ADR-<NNNN>: <Short decision title>

- **Status:** Proposed | Accepted | Superseded by ADR-XXXX | Deprecated
- **Date:** YYYY-MM-DD (ISO date of last status change)
- **Authors:** @handle(s)
- **Deciders:** list of people whose approval was required

## Context

What's the problem or opportunity? 3-8 sentences. Describe the current
state (cite the relevant code / configs / metrics). Describe what's
forcing a decision now (a constraint, a deadline, a recurring
incident). Do not advocate for any option here — just surface the
situation.

## Decision

State the chosen option in one sentence up front. Then 3-6 sentences
elaborating: what we will do, what we will stop doing, the boundary
of the change. Cite the ticket / incident / design doc that triggered
this.

## Consequences

**Positive:**
- Bullet list of concrete benefits. Tie each to a cited metric or
  behavior the reader can verify.

**Negative:**
- Bullet list of costs we accept. Be honest: "new runtime dep", "adds
  2 weeks to Q3 roadmap", "increases p50 by ~30ms".

**Neutral / observational:**
- Changes that aren't obviously pro/con but are worth flagging.

## Alternatives considered

For each alternative, one subsection:

### Alternative A: <short name>

1-3 sentences describing the alternative, why it's tempting, and the
specific reason it was rejected (cite evidence — benchmark, security
review, cost estimate).

### Alternative B: <short name>

Same shape.

## Implementation notes

Optional section. Link to the implementation ticket / epic. List the
repos affected, the rollout order, and any feature-flag strategy.

## References

- Related ADRs (supersedes / superseded by).
- Design docs, postmortems, benchmark results.
- Upstream vendor docs (quote ≤15 words; link for the rest).
