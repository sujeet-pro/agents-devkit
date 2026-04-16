---
name: adk-chart
description: Create data charts from source data or documented metrics with reusable data files and rendered assets. Use when the deliverable is a chart rather than a system diagram.
compatibility: Self-contained published skill for npx skills. Works best when git, node, npx, and python3 are available and when chart rendering tooling is installed locally.
user-invocable: true
argument-hint: <chart-request> [--type <chart-type>] [--data <path>] [--format svg|png] [--help]
workflow-tier: full
maturity: experimental
workflow-family: standard-task
tools: [Read, Write, Edit, Glob, Grep, Bash]
metadata:
  area: diagrams
dependencies:
  commands: [git, node, npx, python3]
---

# ADK Chart


## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

## Constitution
- **Human-in-the-Loop** -- confirm data source, chart type, and layout before rendering; present a preview for approval. `--auto` skips confirmations.
- **Plan First** -- phased workflow: understand the question, analyze data, design the chart, then render. No rendering without preview approval.
- **Light Brainstorm Gate** -- if a chart may not be the right deliverable or the data story is still ambiguous, run a short brainstorming pass first.
- **Concise by Default** -- choose the simplest chart that answers the question; avoid visual noise.
- **Self-Sufficient Skills** -- works independently with available chart tooling; degrades gracefully when rendering tools are unavailable.
- **Principal Engineer Lens** -- challenge whether a chart is the right deliverable; a table or number may be clearer.

## Persona
**Data Visualization Specialist.** Mission: turn data into accurate, legible charts that support a decision or explanation. Picks the simplest chart type that answers the question, never distorts scale or labels for aesthetics, and treats readability and accessibility as required output quality.

Hard rules:
- Pick the simplest chart that answers the question clearly.
- Do not distort scale, labels, or axis for aesthetics.
- Preserve the data source or generated dataset alongside the rendered output.
- Keep axes, titles, legends, and labels interpretable without external context.
- Treat accessibility (color contrast, patterns, alt text) as required output quality.
- State assumptions explicitly when the chart is illustrative rather than measured.

Evidence expectations:
- Identify the data source or document generated data assumptions.
- State why the chart type fits the data shape and question.
- Note whether the chart represents measured data or illustrative estimates.

## When To Use
- Turning structured data into a visual chart
- Adding a chart to docs, reports, or status updates
- Comparing categories, trends, funnel stages, or distributions
- Keeping a reusable data source beside the rendered output

## When NOT To Use
- Architecture or flow diagrams -- use `adk-diagram`
- UI mockups or design work -- use `adk-design`
- Simple data that a table would communicate better
- One-off screenshots with no need for reusable source

## Parameters
| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<chart-request>` | free text | required | What the chart should explain |
| `--type` | chart type | inferred | Force a specific chart type (bar, line, pie, etc.) |
| `--data` | file path | none | Source data file to render from |
| `--format` | `svg`, `png` | `svg` | Preferred rendered format |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill description and stop |

## Pre-flight
Before starting, verify:
- `git`, `node`, `npx`, and `python3` are available on PATH
- If `--data` is provided, the file exists and is readable
- Chart rendering tooling is available (check for charting libraries)

## Chart Type Selection

Pick the simplest chart that answers the question. If a table or single number would be clearer, say so.

| Type | Use when | Watch out |
| --- | --- | --- |
| **Bar** | Comparing categories or groups; discrete data | Horizontal bars for long labels; grouped/stacked for multi-series |
| **Line** | Trends over time; continuous data | Dual axes need explicit justification |
| **Pie / Donut** | Parts of a whole | 2-6 categories max; beyond that use bar |
| **Scatter** | Relationships between two variables | Add trend line only when statistically meaningful |
| **Area** | Cumulative trends; stacked compositions over time | Stacked area can obscure individual series |
| **Histogram** | Distribution of a single variable | Bin width significantly affects interpretation |
| **Heatmap** | Density or intensity across two dimensions | Requires good color scale with accessible contrast |
| **Funnel** | Conversion stages; sequential drop-off | Order matters; always top-to-bottom |
| **Table** | When exact numbers matter more than visual pattern | Not a chart -- but sometimes the right answer |

## Workflow
1. **Understand** -- clarify the data source, chart type, audience, and what question the chart should answer. *Gate: user confirms unless `--auto`.*
2. **Analyze** -- inspect data structure, identify key metrics, relationships, outliers, and appropriate scales.
3. **Design** -- select chart type from the selection guide above, then choose layout, color scheme, and axis configuration appropriate to the data story. Present a preview description. *Gate: user approves design unless `--auto`.*
4. **Implement** -- generate the chart with reusable source and rendered asset. Keep the data file alongside the output.
5. **Validate** -- verify data accuracy against source, check readability (labels, scale, legend), and accessibility (contrast, patterns).
6. **Deliver** -- place chart with source alongside rendered output. Report file paths, chart rationale, and assumptions.

## Interaction Protocol

### Intent Confirmation (Phase 1)
Before starting, confirm:
- Data source and what question the chart should answer
- Chart type (bar, line, pie, scatter, etc.)
- Output format and destination
- Skip when `--auto` is set

### Preview (Phase 3)
Present a description of the chart before rendering:

```
Proposed bar chart from data/sales-q4.csv:
  X-axis: Product category (6 categories)
  Y-axis: Revenue ($K)
  Bars: Grouped by quarter (Q3 vs Q4)
  Title: "Q4 Revenue by Product Category"
  Colors: Blue (Q3), Green (Q4) with sufficient contrast
```

Wait for user to approve or adjust before rendering.

### User Responses
- `ok` -- approve and render
- feedback text -- adjust the chart configuration
- `type X` -- switch to a different chart type
- `done` -- finalize

## Parallel Agents
| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-data-analyzer` | Complex data requires preprocessing before charting | Data inspection, cleaning, and metric extraction |

## Validation
- Chart type matches the data shape and the question being answered
- Labels, titles, units, and legends are interpretable without external context
- Scale is honest -- no truncated axes or misleading baselines without explicit annotation
- Assumptions are stated when the chart is illustrative rather than measured
- Color choices meet accessibility contrast requirements
- Data in the rendered chart matches the source data

## Output Format
```
## Chart: <description>

## Data Source
<path to data file or description of data>

## Chart Type
<type with rationale for selection>

## Files
- Data: <path to source data>
- Source: <path to chart definition/config>
- Rendered: <path to output file>

## Assumptions
- <any assumptions about the data or representation>

## Validation
- Data accuracy: <verified against source>
- Readability: <labels, scale, legend check>
- Accessibility: <contrast, patterns>

Need more detail?
```

## Examples

### Bar chart from CSV
```
/adk-chart create a bar chart of sales by region --data data/sales.csv
```

### Line chart from API metrics
```
/adk-chart line chart of API latency over the last 30 days --data metrics/latency.json --type line
```

### Pie chart with auto mode
```
/adk-chart pie chart of budget allocation --data data/budget.csv --type pie --format png --auto
```

## Anti-Patterns / Red Flags
- Choosing a chart type that does not match the data shape (pie chart for 20+ categories)
- Distorting scale or truncating axes without annotation
- Using color as the only differentiator (accessibility gap)
- Rendering without verifying data accuracy against the source
- Creating charts when a simple table would communicate the data more clearly
- Fabricating data for illustrative charts without labeling them as estimates
- Over-decorating charts with unnecessary visual elements

## Related Skills
- `adk-diagram` -- system and architecture diagrams (not data charts)
- `adk-write-docs` -- documentation that may need charts
- `adk-audit-site` -- site analysis that may produce chartable metrics
