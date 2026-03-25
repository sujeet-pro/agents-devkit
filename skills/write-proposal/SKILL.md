---
name: write-proposal
description: Use when you need to draft a concise decision proposal — lighter than an RFC, focused on a specific decision with clear recommendation
user_invocable: true
arguments:
  - name: title
    description: "Title of the proposal"
    required: true
  - name: scope
    description: "Optional scope or domain such as backend, frontend, infrastructure, data"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# Decision Proposal Writing

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill for concise decision proposals. For larger, more detailed proposals that need extensive design sections, use `/devkit:write-rfc`. To record the final decision after a proposal is accepted, use `/devkit:write-adr`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-proposal format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`

Also load `skills/_references/guidelines/document/research-and-fact-checking.md` when the proposal references tools, vendors, or technical claims, and the matching coding guidance from `skills/_references/guidelines/coding/` when the proposal touches implementation.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` for context, prior art, and supporting evidence
- `doc-reviewer` for structure, clarity, and persuasiveness
- `source-publisher` if the final output is Confluence or Google Docs

## Proposal Structure

The proposal must include these sections:

### 1. Problem Statement
Clear description of the problem or decision needed. What is the current state and why is a change required?

### 2. Proposed Solution
The recommended approach with enough detail to evaluate it. Include diagrams if they aid understanding (use `/devkit:diagram`).

### 3. Pros and Cons
Honest evaluation of the proposed solution:
- Benefits and advantages
- Drawbacks, risks, and limitations
- Known unknowns

### 4. Impact Analysis
What teams, systems, or processes are affected? Include:
- Engineering effort estimate
- Dependencies on other teams or systems
- Operational impact
- User-facing changes if any

### 5. Decision Criteria
What criteria should be used to evaluate this proposal? Make them specific and measurable where possible.

### 6. Recommendation
A clear, actionable recommendation with rationale. State explicitly what decision is being requested from the reader.

## Writing Rules

- Keep the document focused and concise. A proposal should be readable in 10-15 minutes.
- Lead with the recommendation — busy readers should get the key message early.
- Default to markdown as the source of truth unless the destination requires a native format.
- Use concrete examples and data points over abstract statements.
- When the proposal touches real code, inspect the repository first instead of inventing APIs.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.
