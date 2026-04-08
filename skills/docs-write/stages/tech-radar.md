# Stage: Technology Radar

Use this stage when the agent should create or directly revise a technology radar artifact with Adopt, Trial, Assess, or Hold recommendations backed by evidence.

## Type-Specific Phase Guidance

### Exploration
- Research the technology landscape for the specified domain or categories
- Scan the current codebase and infrastructure for technologies in use
- Identify industry trends, community adoption patterns, and maturity signals
- If publishing to Confluence or Google Docs, verify MCP connectivity

### Deep Research
- For each technology entry, gather evidence: adoption rate, community health, release cadence, known issues
- Compare against team capabilities and existing stack
- Assess migration effort and integration complexity

### Execute
- Write the tech radar following the document structure below
- Every recommendation must be backed by evidence, not opinion
- Use consistent evaluation criteria across all entries

## Document Structure

### Radar Overview
- Scope: what domains or categories this radar covers
- Date and cadence (quarterly, biannual, etc.)
- How to read the radar: ring definitions

### Ring Definitions
- **Adopt**: Proven in production, recommended as default choice for new projects
- **Trial**: Worth pursuing, ready for use in projects that can handle some risk
- **Assess**: Worth exploring, understand how it fits your needs
- **Hold**: Proceed with caution, not recommended for new projects

### Categories
Organize entries into categories (e.g., Languages, Frameworks, Tools, Platforms, Techniques).

### Entry Format
For each technology:
- Name and category
- Ring (Adopt/Trial/Assess/Hold)
- Movement since last radar (new, moved in, moved out, unchanged)
- Summary (2-3 sentences)
- Evidence: why this ring placement
- Team context: current usage, integration considerations
- Links: official site, docs, relevant internal ADRs

### Radar Visualization
- Description or Mermaid diagram of the radar layout
- Quadrant view by category

### Change Log
- Technologies that moved rings since the last radar
- Rationale for each movement
- New entries and removals

## Child Agent Team

- `tech-researcher` for gathering evidence on each technology entry
- `stack-analyzer` for assessing current usage in the codebase
- `trend-analyst` for industry adoption trends and community health
- `adk-doc-reviewer` for consistency and evidence quality

## Writing Rules

- Every ring placement must cite specific evidence
- Avoid hype-driven assessments -- focus on production readiness and team fit
- Be specific about "for whom" and "in what context" each recommendation applies
- Include dissenting opinions or edge cases where the recommendation differs

## Type-Specific Output Format

Markdown document with structured entries. Include a radar visualization diagram if possible.

## Validation Checklist

- Every entry has evidence supporting its ring placement
- Categories are consistent and comprehensive
- Ring definitions are clear and consistently applied
- Change log captures all movements since last radar
- Current stack usage is accurately reflected
