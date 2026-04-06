# Stage: Decision Proposal

Use this stage for concise decision proposals -- lighter than an RFC, focused on a specific decision with a clear recommendation. A proposal is appropriate when the decision is smaller in scope than an RFC but still needs structured evaluation.

For larger decisions, use the `rfc` stage. For implementation detail, use the `system-design` stage. To record a durable decision, use the `adr` stage.

## Type-Specific Phase Guidance

### Exploration
- Research the problem space and existing solutions
- Identify affected teams, systems, and processes
- Gather data points that support the recommendation

### Execute
- Write the proposal following the document structure below
- Lead with the recommendation -- busy readers should get the key message early
- Keep the document focused and concise, readable in 10-15 minutes

## Document Structure

### 1. Executive Summary
One-paragraph summary with the recommendation stated upfront.

### 2. Problem Statement
What needs to be decided and why. Include context and urgency.

### 3. Proposed Solution
The recommended approach with enough detail to evaluate. Include specific technologies, patterns, or approaches (not abstract descriptions).

### 4. Pros and Cons
Honest evaluation of the proposed solution:
- Benefits and advantages
- Drawbacks, risks, and limitations
- Known unknowns

### 5. Impact Analysis
What teams, systems, or processes are affected? Include:
- Engineering effort estimate
- Dependencies on other teams or systems
- Operational impact
- User-facing changes if any

### 6. Decision Criteria
What criteria should be used to evaluate this proposal? Make them specific and measurable where possible.

### 7. Recommendation
A clear, actionable recommendation with rationale. State explicitly what decision is being requested from the reader.

## Writing Rules

- Lead with the recommendation -- busy readers should get the key message early.
- Keep the document focused and concise, readable in 10-15 minutes.
- Use concrete examples and data points over abstract statements.
- When the proposal touches real code, inspect the repository first instead of inventing APIs.

## Type-Specific Output Format

Markdown file. Short and focused -- typically 1-3 pages.

## Validation Checklist

- Recommendation is stated clearly upfront
- Pros and cons are balanced and honest
- Impact analysis covers all affected parties
- Decision criteria are specific and measurable
- The document is concise enough to read in 10-15 minutes
