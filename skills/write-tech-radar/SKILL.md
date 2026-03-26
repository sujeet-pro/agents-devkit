---
name: write-tech-radar
description: Use when you need to draft or directly revise a professional technology radar with Adopt, Trial, Assess, or Hold recommendations backed by evidence
user_invocable: true
arguments:
  - name: topic
    description: "Specific technology to evaluate, or 'landscape' to survey the full category"
    required: true
  - name: categories
    description: "Categories to evaluate: languages, frameworks, tools, platforms, or a comma-separated combination (default: all relevant categories)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence (default: markdown)"
    required: false
---

# Technology Radar

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly revise the radar artifact. If you only want comment-only review, use `/devkit:review-doc`.

## Preflight

Before starting research or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-tech-radar format=<format>`

If publishing to Confluence or Google Docs, verify MCP connectivity with a lightweight read.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/tool-evaluation.md`
- `skills/_references/guidelines/document/research-and-fact-checking.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Landscape researcher** (`research-agent`): surveys the technology landscape for the requested categories. Collects official documentation, release cadence, community size, GitHub activity, and adoption signals from major companies. Produces a landscape brief with factual data points per technology.
- **Adoption analyst**: analyzes the current codebase and team context to assess existing adoption. Checks dependency manifests, import patterns, configuration files, and team familiarity. Maps current usage to the radar's classification categories.
- **Risk assessor**: evaluates each technology for vendor lock-in, license changes, maintenance trajectory, security track record, migration cost, and learning curve. Produces a risk profile per technology with severity ratings.
- **Recommendation writer**: synthesizes the landscape, adoption, and risk data into final radar classifications. Writes evidence-backed justifications for each Adopt/Trial/Assess/Hold recommendation with specific action items.

## Workflow

1. **Research landscape.** Launch the landscape researcher for each requested category.
2. **Analyze current adoption.** Launch the adoption analyst to scan the codebase.
3. **Assess risks.** Launch the risk assessor with landscape and adoption data.
4. **Draft recommendations.** Launch the recommendation writer to classify each technology.
5. **Assemble radar.** Merge outputs into the radar structure with quadrant visualization.
6. **Review.** Verify every classification is backed by evidence, not opinion.

Save intermediary artifacts to `.temp/write-tech-radar/`.

## Rating Criteria

- **Adopt**: proven in production, strong community, low risk, recommended for new projects
- **Trial**: promising with positive early results, worth investing in for specific use cases
- **Assess**: worth exploring, not yet ready for production use
- **Hold**: proceed with caution, consider alternatives, plan migration if currently adopted

## Output

A professional technology radar containing:

- **Methodology**: evaluation approach, data sources, and assessment date
- **Radar Visualization**: quadrant diagram via `/devkit:diagram`
- **Technology Profiles**: ring classification, category, evidence summary, recommendation, and movement since last assessment
- **Cross-Cutting Themes**: patterns observed across categories
- **Action Items**: prioritized next steps for the team

## Final Step

Before delivering, verify every classification is backed by at least two independent data points and recommendations include concrete action items.

## Adjacent Skills

- `/devkit:write-tool-eval` for detailed head-to-head tool comparisons
- `/devkit:research` for standalone research on specific technologies
- `/devkit:review-doc` for comment-only review of existing radar documents
