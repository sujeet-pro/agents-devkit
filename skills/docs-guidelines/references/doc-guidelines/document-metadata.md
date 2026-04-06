# Document Metadata, Review Tracking, and Status Lifecycle

Shared conventions for header metadata, review tracking tables, and document status lifecycle across all engineering document types (RFC, Tech Spec, ADR). These conventions ensure consistency whether the document lives in markdown, Google Docs, or Confluence.

**Applies to**: RFC, Tech Spec / Technical Design Document, ADR, and any formal engineering document that requires review and approval.

**References**:
- [Scaling Engineering Teams via RFCs — Gergely Orosz](https://blog.pragmaticengineer.com/scaling-engineering-teams-via-writing-things-down-rfcs/)
- [Template for Writing Technical RFC Docs — Lambros Petrou](https://www.lambrospetrou.com/articles/rfc-template/)
- [The Power of "Yes, if" — Squarespace Engineering](https://engineering.squarespace.com/blog/2019/the-power-of-yes-if)
- [InnerSource: Transparent Cross-Team Decision Making Using RFCs](https://patterns.innersourcecommons.org/p/transparent-cross-team-decision-making-using-rfcs)
- [AWS Prescriptive Guidance: ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)

---

## 1. Header Metadata Block

Every formal engineering document must start with a metadata block. Use this standard set of fields. Fields marked **(optional)** may be omitted when not applicable.

```text
Document Title:
Document Type: RFC | Tech Spec | ADR
Document ID: <type-prefix + sequential number, e.g., RFC-012, TS-045, ADR-0023>
Status: <see Status Lifecycle below>
Owner:
Created: YYYY-MM-DD
Last Updated: YYYY-MM-DD
Project / Initiative: <name or N/A>
Tracking Link(s) (Optional): <Jira / GitHub Issue / Linear / Asana / N/A>
Target Milestone / Release (Optional):
Related Docs (Optional): <links to related RFCs, Tech Specs, ADRs, PRDs>
Repositories / Services (Optional): <repo or service names>
```

### Field Guidance

- **Document ID**: Use a type prefix and sequential number. Never reuse an ID, even for superseded documents. The sequence is append-only.
- **Status**: Must be one of the values defined in the Status Lifecycle section below. Always include the date of the most recent status change.
- **Owner**: The person responsible for the document. One person, not a team.
- **Tracking Links**: Generic field that works with any work-tracking tool. Do not hardcode Jira-specific fields. If no tracking tool is in use, mark as N/A.
- **Related Docs**: Cross-link between RFCs, Tech Specs, and ADRs. The typical flow is RFC -> Tech Spec -> ADR(s).

---

## 2. Review Tracking Table

Every document that goes through a review process must include a review tracking table. This table tracks who has been asked to review, their current status, and any high-level comments.

### Table Format

```markdown
## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| Jane Smith | Backend Lead | Approved | 2026-03-15 | Concerns about caching addressed in v2 |
| Bob Chen | Security Eng | Approved with conditions | 2026-03-17 | Requires TLS 1.3; see comment thread |
| Alice Park | SRE | Not reviewed | -- | -- |
| Architecture Board | Board | Approved | 2026-03-20 | Condition: add rollback plan (done) |
```

### Reviewer Status Values

| Status | Meaning |
|--------|---------|
| **Not reviewed** | Has not yet looked at the document |
| **In progress** | Currently reviewing |
| **Approved** | Signs off on the document as-is |
| **Approved with conditions** | Approves contingent on specific changes ("yes, if...") |
| **Changes requested** | Does not approve; specific feedback provided |
| **Declined** | Does not approve the proposal (must state what would change their decision) |
| **Abstained** | Chose not to provide a review opinion |

### Reviewer Role Guidance

Include reviewers from these categories as applicable:

| Role Category | When to Include |
|---------------|----------------|
| **Tech Lead / Area Owner** | Always — owns the technical area |
| **Domain Expert** | When the change touches specialized domains |
| **Security Engineer** | When the change has security, privacy, or compliance implications |
| **SRE / Platform** | When the change affects production operations, reliability, or infrastructure |
| **Product Manager** | When the change has user-facing or business impact |
| **Architecture Board** | For cross-team or organization-wide changes |
| **Data Engineer** | When the change involves data models, pipelines, or storage |

### Cross-Platform Notes

- **Markdown**: Use the table above directly.
- **Google Docs**: Use a native Google Docs table. The table should be placed immediately after the metadata block.
- **Confluence**: Use a native Confluence table or the built-in "Decision" macro for tracking approvals.

---

## 3. Document Status Lifecycle

### RFC Status Values

```
Draft --> In Review --> Approved --> In Progress --> Completed
                   \              \
                    \--> Declined  \--> Abandoned
                                   \--> Superseded (by RFC-NNN)
```

| Status | Definition |
|--------|-----------|
| **Draft** | Author is developing the document; not ready for review |
| **In Review** | Circulated to reviewers for feedback |
| **Approved** | Decision made to proceed with the proposal |
| **Declined** | Reviewers or author decide not to proceed; reason documented |
| **In Progress** | Implementation underway based on the approved RFC |
| **Completed** | Implementation finished; RFC is now a historical record |
| **Abandoned** | Author withdrew the RFC before a decision was reached |
| **Superseded** | Replaced by a newer RFC; link to replacement required |

### Tech Spec / Technical Design Document Status Values

```
Draft --> In Review --> Approved --> Implementing --> Implemented
                   \                                \--> Obsolete
                    \--> Revision Requested
```

| Status | Definition |
|--------|-----------|
| **Draft** | Author is developing the document; not ready for review |
| **In Review** | Circulated to reviewers for technical evaluation |
| **Revision Requested** | Reviewers require significant changes before approval |
| **Approved** | Design is accepted; implementation may begin |
| **Implementing** | Active implementation in progress |
| **Implemented** | Implementation complete; spec is now a reference document |
| **Obsolete** | The design is no longer current; superseded or deprecated |

### ADR Status Values

```
Proposed --> Accepted --> Superseded (by ADR-NNNN)
         \            \--> Deprecated
          \--> Rejected
```

| Status | Definition |
|--------|-----------|
| **Proposed** | Decision is documented and ready for team review |
| **Accepted** | Decision is approved; ADR becomes immutable |
| **Rejected** | Decision was considered but not adopted; reason documented |
| **Deprecated** | Decision is no longer relevant due to changed circumstances |
| **Superseded** | Replaced by a newer ADR; old ADR updated to link to replacement |

### Status Rules

1. **Always record the date** of each status transition: `Approved (2026-03-15)`.
2. **Never delete documents.** Mark them as Superseded, Deprecated, or Obsolete and link to the replacement.
3. **ADRs are immutable after acceptance.** To change a decision, create a new ADR and mark the old one as Superseded.
4. **RFCs and Tech Specs are living documents** during Draft and In Review phases. After approval, changes should be tracked through versioned updates or supplementary documents.

---

## 4. Review Process Guidelines

### Review SLAs (Recommended)

| Milestone | Target |
|-----------|--------|
| First response | 1 business day |
| Final comments / decision | 2 business days |
| Escalation if blocked past SLA | Tech lead or area owner makes the call |

### Review Models

**Fast path** (small, low-risk changes):
- Author writes the document, moves to In Review.
- Review happens asynchronously during PR review or in the document itself.

**Pre-review required** (medium+ / risky changes):
- Required when any of these are true:
  - Touches multiple components or teams
  - Performance-sensitive change
  - Non-trivial API or data model change
  - Estimated effort exceeds 2 dev-days

**"Yes, if" model** (recommended for architecture reviews):
- Reviewers respond with "approved", "changes requested", or "approved with conditions" (the "yes, if" pattern from Squarespace).
- Flat rejection requires the reviewer to specify what would make the proposal acceptable.

---

## 5. Relationship Between Document Types

```
Problem identified
       |
       v
  [Write RFC]  <-- "Should we do this, and which direction?"
       |
       v
  [RFC Approved]
       |
       +-----> [Extract ADR(s)]  <-- Record key decisions from the RFC
       |
       v
  [Write Tech Spec]  <-- "How exactly will we build and operate this?"
       |
       v
  [Implementation]
       |
       v
  [Update ADR(s) if decisions change during implementation]
```

| Criterion | RFC | Tech Spec | ADR |
|-----------|-----|-----------|-----|
| **Primary question** | Should we do this? Which direction? | How will we build this? | What did we decide, and why? |
| **Audience** | Broad engineering org | Implementation team + reviewers | Future engineers, new team members |
| **Scope** | One proposal (may span many decisions) | One project or feature | One decision |
| **Typical length** | 2-5 pages | 5-20 pages | 0.5-2 pages |
| **Mutability** | Living doc during review; frozen after approval | Living doc through implementation | Immutable after acceptance |
| **Storage** | Wiki / Docs platform | Wiki / Docs platform | Code repository (`docs/adr/`) preferred |

### When to Use Which

- **Not every change requires all three.** Small decisions may only need an ADR. Medium features may only need a Tech Spec. Cross-cutting, organization-wide proposals warrant the full RFC -> Tech Spec -> ADR pipeline.
- **HLD and LLD are sections inside the Tech Spec**, not separate documents, unless the system is large enough to warrant separate review audiences.
- **A lightweight Tech Spec** (1-3 pages) suffices for changes within a single team with moderate complexity.
- **A heavyweight Tech Spec** (10-20 pages) is appropriate for cross-team changes, new services, or significant architecture changes.
