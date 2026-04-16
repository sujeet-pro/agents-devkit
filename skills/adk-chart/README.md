# adk-chart

Create data charts from source data or documented metrics with reusable data files and rendered assets.

## Quick Start

```bash
npx adk-chart "bar chart of sales by region" --data data/sales.csv
```

## What This Skill Does

Turns structured data into charts that explain measured data, estimated numbers, or documented metrics. Keeps a reusable data source beside the rendered output. Use when the deliverable is a chart rather than a system diagram.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<chart-request>` | free text | required | What the chart should explain |
| `--type` | chart type | inferred | Force a chart type when known |
| `--data` | file path | none | Source data file to render from |
| `--format` | `svg`, `png` | `svg` | Preferred rendered format |
| `--auto` | flag | off | Skip confirmations and use defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | command | yes |
| `node` | command | yes |
| `npx` | command | yes |
| `python3` | command | yes |

## Skill Layout

```
adk-chart/
  SKILL.md
  README.md
  scripts/
    preflight.py
  references/
    workflow.md
    persona.md
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. Confirm the chart goal, audience, and data source.
2. Inspect the data or extract it from the agreed source material.
3. Choose the simplest chart type that answers the question.
4. Keep the generated or provided data file with the rendered output.
5. Render the chart in the requested format and verify labels and scale.
6. Finish with chart rationale, outputs, and any assumptions still in play.

## Interaction Protocol

Unless `--auto` is set, the skill follows an interactive workflow:

1. **Intent confirmation** -- confirms the data source, the question the chart answers, chart type, and output format.
2. **Preview** -- presents a description of the chart (axes, labels, grouping, title) before rendering.
3. **User response** -- `ok` to approve and render, feedback text to adjust, `type X` to switch chart type, `done` to finalize.

## Output Format

Each run produces:
- Chart goal
- Data source path
- Chart type used
- Rendered output paths
- Validation notes
- Remaining assumptions

## Examples

### Bar chart from CSV
```bash
npx adk-chart "bar chart of sales by region" --data data/sales.csv
```
Confirms the data columns and chart goal, previews the layout, renders the chart.

### Line chart from API metrics
```bash
npx adk-chart "line chart of API latency over the last 30 days" --data metrics/latency.json --type line
```
Reads the JSON data, proposes axis labels and scale, renders a line chart.

### Pie chart with explicit type
```bash
npx adk-chart "pie chart of budget allocation" --data data/budget.csv --type pie --format png --auto
```
Skips confirmations, reads the CSV, renders a pie chart in PNG format.

## What Success Looks Like

- [ ] The chart type matches the data shape and question
- [ ] Labels, titles, and units are interpretable
- [ ] The data file is kept with the rendered output for reproducibility
- [ ] Assumptions are explicit when the chart is illustrative rather than measured
- [ ] The skill reports chart goal, data source, outputs, and validation notes
