---
title: "chart"
description: Create data charts — bar, line, pie, scatter, area, and 30+ chart types from CSV/JSON data with CLI-based SVG/PNG rendering
skill_name: chart
category: task
workflow_tier: full
user_invocable: true
---

# chart

Create data-driven charts from CSV, JSON, or inline data. Supports 30+ chart types including bar, line, pie, scatter, area, heatmap, waterfall, treemap, funnel, radar, gauge, and more. CLI-based rendering via `chartts` — no browser required.

## When to Use

- Visualize data comparisons, trends, or distributions in a chart
- Generate charts for embedding in documentation
- Create performance, revenue, or sprint velocity visualizations
- Render charts in both light and dark themes
- Generate SVG or PNG charts from CSV/JSON data files

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<description>` | text | required | What the chart should show |
| `--type` | see Chart Types | auto-detect | Chart type |
| `--data` | file path | none | Input data file (CSV, TSV, or JSON) |
| `--render` | flag | off | Render to image after generating data file |
| `--format` | `svg` \| `png` | `svg` | Output image format |
| `--theme` | `light` \| `dark` \| `both` | `both` | Theme variant(s) to render |
| `--width` | integer | 600 | Chart width in pixels |
| `--height` | integer | 400 | Chart height in pixels |
| `--title` | text | none | Chart title (also used as aria-label) |
| `--output` | file path | `./charts/<name>.<format>` | Output file path |
| `--auto` | flag | off | Skip confirmations |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **`--data` provided** | Reads and analyzes the existing data file, auto-detects columns for the chart type |
| **No `--data`** | Creates a data file from the user's description or research |
| **`--type` omitted** | Auto-detects chart type from data patterns (time series → line, categories → bar, part-of-whole → pie) |
| **`--render` set** | Generates data file and renders chart image |
| **`--theme both`** | Renders two variants: `<name>-light.<format>` and `<name>-dark.<format>` |
| **Invoked by doc skill** | Chart data derived from document content; output placed in `charts/` subdirectory relative to the document |

## Chart Types

### Basic Charts

| Type | Flag | Best For |
|------|------|---------|
| Bar | `bar` | Category comparisons |
| Horizontal Bar | `horizontal-bar` | Long category labels |
| Line | `line` | Trends over time |
| Area | `area` | Volume over time |
| Pie | `pie` | Part-of-whole (≤ 7 slices) |
| Donut | `donut` | Part-of-whole with center label |
| Scatter | `scatter` | Correlations between two variables |

### Advanced Charts

| Type | Flag | Best For |
|------|------|---------|
| Stacked Bar | `stacked-bar` | Category comparison with composition |
| Grouped Bar | `grouped-bar` | Side-by-side category comparison |
| Stacked Area | `stacked-area` | Volume composition over time |
| Bubble | `bubble` | Three-variable correlation (x, y, size) |
| Radar | `radar` | Multi-dimensional comparison |
| Heatmap | `heatmap` | Pattern detection in matrix data |
| Treemap | `treemap` | Hierarchical composition |
| Waterfall | `waterfall` | Cumulative effect of sequential values |
| Funnel | `funnel` | Conversion or reduction stages |
| Gauge | `gauge` | Single metric against a target |
| Candlestick | `candlestick` | Financial OHLC data |

### Data Format per Chart Type

| Chart Type | Required Columns | Optional |
|-----------|-----------------|----------|
| `bar`, `horizontal-bar` | label, value | series (for grouped) |
| `line`, `area` | x (date/number), y | series |
| `pie`, `donut` | label, value | — |
| `scatter` | x, y | series, size (bubble) |
| `stacked-bar` | label, value, series | — |
| `radar` | axis, value | series |
| `heatmap` | x, y, value | — |
| `waterfall` | label, value | type (increase/decrease/total) |
| `funnel` | stage, value | — |
| `gauge` | value | target, min, max |
| `candlestick` | date, open, high, low, close | volume |

## Auto-Detection Table

When `--type` is omitted, the skill selects a chart type based on data patterns:

| Data Pattern | Recommended Chart Type |
|-------------|----------------------|
| Categories with values | `bar` or `horizontal-bar` |
| Time series | `line` or `area` |
| Part-of-whole composition | `pie` or `donut` |
| Two-variable correlation | `scatter` or `bubble` |
| Multiple series comparison | `stacked-bar` or `grouped-bar` |
| Distribution | `histogram` or `box` |
| Hierarchical data | `treemap` or `sunburst` |
| Flow/conversion | `funnel` |
| Multi-dimensional comparison | `radar` |
| Single metric with target | `gauge` |
| Price/financial data | `candlestick` |
| Heat patterns | `heatmap` |
| Progress over time | `waterfall` |

## Key Behaviors

- **Auto-detection**: infers chart type from data patterns when `--type` is not set
- **Dual theming**: renders both light and dark variants by default for documentation compatibility
- **Accessibility**: uses a CVD-accessible default palette; enforces WCAG AA contrast ratios
- **Data-first**: keeps the data file alongside the chart for reproducibility
- **Quality standards**: requires descriptive title, labeled axes, readable scale, appropriate type, and alt text

## Workflow

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, data source, chart type, and output format |
| 1. Research & Options | yes | Analyze data, determine chart type and data structure |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate data file and render chart |
| 5. Validate & Learn | yes | Verify rendering, check data accuracy, confirm readability |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before rendering | Run preflight.py for chartts CLI validation |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

After rendering, prints a summary:

```
Chart rendered:
  Data: ./charts/revenue-data.csv
  Light: ./charts/revenue-light.svg
  Dark: ./charts/revenue-dark.svg

Render with: chartts render --type bar --data ./charts/revenue-data.csv -o ./charts/revenue.svg
```

## Charts vs Diagrams

| Scenario | Use Chart | Use Diagram |
|----------|-----------|-------------|
| Performance comparison | Yes | No |
| Architecture overview | No | Yes (Mermaid/Excalidraw) |
| Sprint velocity | Yes | No |
| Database schema | No | Yes (Mermaid ER) |
| Cost projections | Yes | No |
| Sequence flow | No | Yes (Mermaid) |
| Market share breakdown | Yes | No |
| Network topology | No | Yes (draw.io/Graphviz) |
| A/B test results | Yes | No |
| State machine | No | Yes (Graphviz/Mermaid) |

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:diagram` | Structural and relational diagrams (architecture, flows, ER) |
| `/adk:docs-crud` | Document creation that may embed charts |
| `/adk:docs-write` | Formal document writing that may embed charts |
| `/adk:diagram-mermaid` | Mermaid-based diagrams (some chart types overlap: pie, xy, gantt) |
| `/adk:diagram-graphviz` | Graphviz DOT diagrams for dependency graphs |

## Examples

```
/adk:chart "Monthly revenue comparison Q1 vs Q2" --type bar --data revenue.csv
/adk:chart "User growth over time" --type line --render
/adk:chart "Traffic distribution by region" --type pie --data traffic.json --render --format png
/adk:chart "API latency percentiles" --type bar --render --theme both
/adk:chart "Sprint velocity" --type bar --data sprints.csv --render
/adk:chart "Cost projections" --type area --render --format png
/adk:chart --help
```
