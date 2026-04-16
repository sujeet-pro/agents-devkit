---
title: 'adk-chart'
description: 'Create data charts from source data or documented metrics with reusable data files and rendered assets. Use when the deliverable is a chart rather than a system diagram'
skill_name: adk-chart
category: task
workflow_tier: full
user_invocable: true
---

# adk-chart

Use `adk-chart` to create data charts from source data or documented metrics with reusable data files and rendered assets. Use when the deliverable is a chart rather than a system diagram. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-chart` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<chart-request>` | free text | required | What the chart should explain |
| `--type` | chart type | inferred | Force a specific chart type (bar, line, pie, etc.) |
| `--data` | file path | none | Source data file to render from |
| `--format` | `svg`, `png` | `svg` | Preferred rendered format |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show this skill description and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Understand** -- clarify the data source, chart type, audience, and what question the chart should answer. *Gate: user confirms unless `--auto`.*
2. **Analyze** -- inspect data structure, identify key metrics, relationships, outliers, and appropriate scales.
3. **Design** -- select chart type from the selection guide above, then choose layout, color scheme, and axis configuration appropriate to the data story. Present a preview description. *Gate: user approves design unless `--auto`.*
4. **Implement** -- generate the chart with reusable source and rendered asset. Keep the data file alongside the output.
5. **Validate** -- verify data accuracy against source, check readability (labels, scale, legend), and accessibility (contrast, patterns).
6. **Deliver** -- place chart with source alongside rendered output. Report file paths, chart rationale, and assumptions.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm data source, chart type, and layout before rendering; present a preview for approval. `--auto` skips confirmations.
- **Plan First** -- phased workflow: understand the question, analyze data, design the chart, then render. No rendering without preview approval.
- **Light Brainstorm Gate** -- if a chart may not be the right deliverable or the data story is still ambiguous, run a short brainstorming pass first.
- **Concise by Default** -- choose the simplest chart that answers the question; avoid visual noise.
- **Self-Sufficient Skills** -- works independently with available chart tooling; degrades gracefully when rendering tools are unavailable.
- **Principal Engineer Lens** -- challenge whether a chart is the right deliverable; a table or number may be clearer.

### Persona

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

### When To Use

- Turning structured data into a visual chart
- Adding a chart to docs, reports, or status updates
- Comparing categories, trends, funnel stages, or distributions
- Keeping a reusable data source beside the rendered output

### When NOT To Use

- Architecture or flow diagrams -- use `adk-diagram`
- UI mockups or design work -- use `adk-design`
- Simple data that a table would communicate better
- One-off screenshots with no need for reusable source

### Pre-flight

Before starting, verify:
- `git`, `node`, `npx`, and `python3` are available on PATH
- If `--data` is provided, the file exists and is readable
- Chart rendering tooling is available (check for charting libraries)

### Chart Type Selection

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

### Interaction Protocol

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

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-data-analyzer` | Complex data requires preprocessing before charting | Data inspection, cleaning, and metric extraction |

### Validation

- Data accuracy: <verified against source>
- Readability: <labels, scale, legend check>
- Accessibility: <contrast, patterns>

Need more detail?
```

### Chart: <description>



### Data Source

<path to data file or description of data>

### Chart Type

<type with rationale for selection>

### Files

- Data: <path to source data>
- Source: <path to chart definition/config>
- Rendered: <path to output file>

### Assumptions

- <any assumptions about the data or representation>

### Anti-Patterns / Red Flags

- Choosing a chart type that does not match the data shape (pie chart for 20+ categories)
- Distorting scale or truncating axes without annotation
- Using color as the only differentiator (accessibility gap)
- Rendering without verifying data accuracy against the source
- Creating charts when a simple table would communicate the data more clearly
- Fabricating data for illustrative charts without labeling them as estimates
- Over-decorating charts with unnecessary visual elements

### Related Skills

- `adk-diagram` -- system and architecture diagrams (not data charts)
- `adk-write-docs` -- documentation that may need charts
- `adk-audit-site` -- site analysis that may produce chartable metrics

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-chart <chart-request>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-chart <chart-request> --auto
```
