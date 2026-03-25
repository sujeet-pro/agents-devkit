---
name: write-tool-eval
description: Use when you need to create a structured tool or technology evaluation document comparing multiple options against defined criteria
user_invocable: true
arguments:
  - name: tools
    description: "Comma-separated list of tools or technologies to evaluate"
    required: true
  - name: criteria
    description: "Optional comma-separated evaluation criteria (default: auto-detected based on tool category)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# Tool Evaluation Writing

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill to produce a structured comparison of tools or technologies. For deeper investigation of a single tool, use `/devkit:research-deep`. For other document types, use `/devkit:write-doc`.

## Preflight

Before research, drafting, or publishing setup, run:

`zsh scripts/check-skill-deps.zsh write-tool-eval format=<format>`

If the document will be published to Confluence or Google Docs, do a lightweight MCP read before launching the writing team.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/tool-evaluation.md`

Also load `skills/_references/guidelines/document/research-and-fact-checking.md` for research verification and the matching coding guidance from `skills/_references/guidelines/coding/` when evaluating developer tools or frameworks.

## Required Child Agents

Run at least these child agents in parallel:

- `research-agent` (one per tool) for official docs, pricing, community health, known issues, and recent changelog entries
- `code-snippet-agent` for integration examples when evaluating libraries or frameworks
- `doc-reviewer` for structure, balance, and objectivity
- a diagram pass through `/devkit:diagram` for comparison visuals and architecture diagrams
- `source-publisher` if the final output is Confluence or Google Docs

## Evaluation Structure

The document must include these sections:

### 1. Executive Summary
One paragraph summarizing the evaluation context, the tools compared, and the top-line recommendation.

### 2. Evaluation Context
Why this evaluation is needed. What problem are we solving? What constraints exist (budget, team skills, timeline, compliance)?

### 3. Criteria Definition
Define each evaluation criterion with:
- Description of what is being measured
- Weight (critical, high, medium, low)
- How it will be scored (e.g., 1-5 scale, pass/fail, qualitative)

If `criteria` was not provided, derive appropriate criteria from the tool category (e.g., for databases: performance, scalability, cost, ecosystem, operations, security).

### 4. Individual Tool Profiles
For each tool:
- Overview and primary use case
- Key features relevant to the evaluation
- Maturity and community health (stars, contributors, release cadence)
- Pricing model
- Known limitations and risks
- Integration considerations for the current stack

### 5. Comparison Matrix
A table scoring each tool against every criterion. Include:
- Numeric scores
- Brief justification for each score
- Visual indicators for quick scanning

Include a diagram when it aids comparison (e.g., radar chart description, architecture fit diagram).

### 6. Deep Dives
For the top two or three candidates, provide deeper analysis:
- Proof-of-concept feasibility
- Migration path from current tooling
- Operational overhead
- Team learning curve

### 7. Recommendation
A clear recommendation with:
- Primary choice and rationale
- Runner-up and when it would be preferred instead
- Conditions that would change the recommendation
- Suggested next steps (proof of concept, pilot, full adoption)

## Writing Rules

- Stay objective. Present facts and let the criteria drive the recommendation.
- Cite sources for all claims (documentation URLs, benchmark results, pricing pages).
- Default to markdown as the source of truth unless the destination requires a native format.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.
- Use only free or open tooling for conversion and rendering.
- When evaluating tools against the current stack, inspect the repository first instead of guessing integration points.

## Final Step

Before publishing, run an internal review loop with the doc-review team and fix all critical issues that block handoff.
