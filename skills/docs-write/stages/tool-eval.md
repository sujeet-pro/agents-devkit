# Stage: Tool Evaluation

Use this stage to produce a structured comparison of tools or technologies against defined criteria. For deeper investigation of a single tool, use `/adk-research --deep`.

## Type-Specific Phase Guidance

### Exploration
- Identify the tools or technologies to evaluate
- Research each candidate: features, maturity, community, pricing
- Scan the current codebase to understand integration requirements

### Deep Research
- For each candidate, gather detailed data: benchmarks, case studies, migration paths
- Evaluate against the current stack for integration complexity
- Assess operational overhead, learning curve, and total cost of ownership

### Execute
- Write the evaluation following the document structure below
- Stay objective -- let criteria and evidence drive the recommendation
- Cite sources for all claims

## Document Structure

### 1. Executive Summary
The evaluation question, shortlisted tools, and the recommendation.

### 2. Evaluation Context
- What problem are we solving?
- Current tooling and its limitations
- Requirements and constraints
- Timeline and budget considerations

### 3. Evaluation Criteria
Weighted criteria table. If `--criteria` was not provided, derive appropriate criteria from the tool category (e.g., for databases: performance, scalability, cost, ecosystem, operations, security).

| Criterion | Weight | Description |
|-----------|--------|-------------|
| ... | N/10 | ... |

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

## Child Agent Team

- `tool-researcher` for gathering detailed data on each candidate
- `stack-analyzer` for assessing integration with current codebase
- `benchmark-analyst` for performance comparisons and cost analysis
- `doc-reviewer` for objectivity and evidence quality

## Writing Rules

- Stay objective. Present facts and let the criteria drive the recommendation.
- Cite sources for all claims (documentation URLs, benchmark results, pricing pages).
- When evaluating tools against the current stack, inspect the repository first instead of guessing integration points.
- Keep both editable diagram source files and rendered outputs.
- Prefer Mermaid, Excalidraw, or draw.io for diagrams.

## Type-Specific Output Format

Markdown document with comparison matrix, individual profiles, and a clear recommendation.

## Validation Checklist

- All shortlisted tools have complete profiles
- Comparison matrix covers all criteria with justified scores
- Sources are cited for all factual claims
- Recommendation is supported by the evaluation data
- Integration assessment is grounded in actual codebase inspection
- Deep dives cover the top candidates
