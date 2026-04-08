---
title: "chart"
description: Create data charts from CSV/JSON — bar, line, pie, scatter, and 30+ chart types
skill_name: chart
category: task
workflow_tier: full
user_invocable: true
---

# chart

Creates data visualizations from CSV/JSON data. Supports 30+ chart types with CLI-based SVG/PNG rendering via chartts.

## When to Use

- Visualize data in documents
- Generate charts for reports and presentations
- Embed charts in markdown documentation

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<description>` | free text | (required) | Chart description |
| `--type` | `bar`, `line`, `pie`, `scatter`, `area`, `radar`, `heatmap`, `treemap`, `sunburst`, `sankey`, `funnel`, `gauge`, `boxplot`, `histogram`, `bubble`, etc. | auto-detect | Chart type |
| `--data` | file path | — | CSV/JSON data source |
| `--render` | flag | auto | Render to image |
| `--format` | `svg`, `png` | `svg` | Output format |
| `--theme` | `light`, `dark` | `light` | Color theme |
| `--width` | pixels | auto | Chart width |
| `--height` | pixels | auto | Chart height |
| `--title` | text | — | Chart title |
| `--output` | file path | auto | Output file path |
| `--help` | flag | — | Show parameters |

## Workflow

Full 6-phase workflow with complexity-adaptive skipping.

## Shared Skills

`workflow`, `communication`, `preflight-check`, `output-format`, `principal-engineer` (medium+), `agentic-teams` (medium+), `interaction`.

## Examples

```text
/adk:chart bar chart of monthly revenue from ./data/revenue.csv
/adk:chart --type pie --data ./data/market-share.json market share breakdown
/adk:chart --type line --theme dark --format png performance over time
```
