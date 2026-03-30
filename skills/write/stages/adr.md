# Stage: Architecture Decision Record (ADR)

An ADR answers the question "what decision did we make, and why?" ADRs are short (0.5-2 pages), durable, and immutable after acceptance.

For pre-alignment on direction, use the `rfc` stage. For implementation detail, use the `system-design` stage.

## Type-Specific Phase Guidance

### Exploration
- Read the PR, discussion notes, or codebase analysis that triggered the decision
- Identify the decision drivers: quality attributes, constraints, team expertise, timeline pressures, compliance requirements
- Scan for prior ADRs in `docs/adr/` to determine the next sequential number

### Execute
- Write the ADR following the document structure below
- Keep it concise -- 0.5-2 pages. If it grows beyond that, the detail belongs in a Tech Spec

## Document Structure

### Metadata Block
Standard metadata header with document ID, status (Proposed/Accepted/Deprecated/Superseded), owner, date, and tracking links.

### Review Tracker
Review tracking table with named reviewers, roles, and status. Omit for lightweight, single-team decisions where the decision-makers are already listed in the metadata.

### Context and Problem Statement
The forces at play and the problem requiring a decision. Objective -- does not argue for a solution. Links to related RFCs, Tech Specs, tickets, and prior ADRs.

### Decision Drivers
Bullet list of key factors that influenced the choice: quality attributes, constraints, team expertise, timeline pressures, compliance requirements.

### Considered Options
At least two options that were seriously evaluated, each with a brief description.

### Decision
The chosen option with specific, actionable detail. Named technologies, patterns, and approaches. Justification referencing the decision drivers.

### Consequences
Three categories -- Positive, Negative, and Neutral. Must include operational consequences. Honest about trade-offs.

### Links
Related RFCs, Tech Specs, ADRs, and tracking tickets.

## Writing Rules

- State decisions specifically. "We will use caching" is not a decision; name the cache, the strategy, and the data.
- ADRs are immutable after acceptance. To change a decision, create a new ADR and mark the old one as Superseded.
- Be honest about negative consequences. An ADR with only positive consequences is incomplete.
- Default to markdown as the source of truth. ADRs live in the code repository under `docs/adr/`.
- When the ADR describes real code, inspect the repository first instead of inventing APIs.

## Type-Specific Output Format

Markdown file saved to `docs/adr/NNNN-<slug>.md` where NNNN is the next sequential number.

## Validation Checklist

- ADR number is sequential
- Status includes a date
- All sections are complete
- At least two options were considered
- Decision is specific and actionable
- Consequences include negative items
- Invoke `/doc-writing --type adr` to load ADR writing guidelines for validation

## Adjacent Skills

- `rfc` stage for RFC documents (pre-alignment on direction)
- `system-design` stage for Tech Spec / Technical Design Documents (implementation detail)
- `/review` for comment-only review of existing ADRs
