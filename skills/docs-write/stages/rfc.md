# Stage: RFC (Request for Comments)

An RFC answers the question "should we do this, and which direction should we choose?" For lighter decision proposals, use the `proposal` stage. For implementation detail, use the `system-design` stage. To record the final decision after an RFC is accepted, use the `adr` stage.

## Type-Specific Phase Guidance

### Exploration
- Research the problem space, existing solutions, and organizational context
- Identify stakeholders and their likely positions
- Scan for prior RFCs and related ADRs

### Brainstorm
- Present alternatives with stakeholder impact analysis
- If simulation is enabled, simulate stakeholder positions (Security, Platform, Product, SRE)

### Execute
- Write the RFC following the document structure below
- Keep concise -- typically 2-5 pages. If it grows beyond that, the detail likely belongs in a Tech Spec
- After alternatives are written, present each one interactively:
```text
## Alternative [N/total]: <name>

Description: <approach>
Pros: <list>
Cons: <list>

Stakeholder views (if simulation enabled):
- Security: <position>
- Platform: <position>
- Product: <position>
- SRE: <position>

Compared to proposal:
- Better at: <what>
- Worse at: <what>

Your assessment: [S]trong alternative | [W]eak alternative | [C]ombine with proposal
```

### Validate
- If any stakeholder "Blocks", flag the blocking concern for resolution before moving forward

## Document Structure

### Metadata Block
Standard metadata header with document ID, status, owner, dates, and tracking links.

### Review Tracker
Review tracking table with named reviewers, roles, and status. Identify reviewers before moving the RFC to "In Review" status.

### 1. Summary
A one-paragraph executive summary readable by any engineer in the organization. Must convey the problem, the proposed direction, and the expected outcome.

### 2. Motivation / Problem Statement
Why this change is needed. What is the current pain point or gap? Include quantitative data when available. Be objective -- present the problem without arguing for a specific solution.

### 3. Goals
Specific, verifiable goals that define the success criteria for the proposal.

### 4. Non-Goals
What this RFC explicitly does not address. Prevents scope creep during review and implementation.

### 5. Proposal
The recommended direction with enough detail to evaluate. Include 1-2 architecture or flow diagrams (use `/diagram` skills). Stay at the "direction" level -- defer implementation-level detail to a Tech Spec.

### 6. Alternatives Considered
At least two genuine alternative approaches with pros, cons, and rejection rationale for each. Strawman alternatives undermine the document.

### 7. Impact Analysis
Impact across five dimensions: Engineering, Product/Business, Security/Compliance, Cost/Infrastructure, and Operational. Use a structured table.

### 8. Rollout Approach
High-level phases for introducing the change. Feature flags, backward compatibility, kill-switch strategy. Detailed rollout planning belongs in the Tech Spec.

### 9. Open Questions
Unresolved questions with owners and target resolution dates. Each question must be specific and actionable.

### 10. Decision Requested
Explicitly state what decision the reviewers are being asked to make.

## Decision Criteria Matrix

When the RFC has 3+ alternatives, generate a decision criteria matrix:
```text
| Criterion | Weight | Proposal | Alt 1 | Alt 2 |
|-----------|--------|----------|-------|-------|
| <criterion> | N/10 | score | score | score |
```

Let user adjust weights and scores interactively.

## Writing Rules

- The Motivation section must present the problem objectively without arguing for the proposed solution.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.

## Type-Specific Output Format

Markdown file. Invoke `/docs-guidelines --type rfc` to load RFC writing guidelines for validation.

## Adjacent Skills

- `system-design` stage for Tech Spec / Technical Design Documents (implementation detail)
- `adr` stage for Architecture Decision Records (recording decisions)
- `proposal` stage for lighter decision proposals
- `/diagram` for standalone architecture diagrams
- `/plan --mode brainstorm` for deeper option exploration before RFC
