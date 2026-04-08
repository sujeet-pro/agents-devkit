---
name: chart
description: "adk - [full] [chart] Create data charts — bar, line, pie, scatter, area, and 30+ chart types from CSV/JSON data. CLI-based SVG/PNG rendering."
user-invocable: true
argument-hint: "<description> [--type bar|line|pie|scatter|area|...] [--data <file>] [--render] [--format svg|png] [--theme light|dark|both]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
dependencies:
  commands: [git, node, python3]
  npm-packages: [@chartts/cli]
workflow-tier: full
---

# Data Chart

Create data-driven charts from CSV, JSON, or inline data. Supports 30+ chart types including bar, line, pie, scatter, area, heatmap, waterfall, treemap, funnel, radar, gauge, and more. CLI-based rendering — no browser required.

This skill can be invoked directly or from other skills (especially `/adk:docs-crud` and `/adk:docs-write`) when documents need data visualizations.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before rendering | Run preflight.py for chartts CLI validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Keep both data file and rendered chart. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<description>` | text | required | What the chart should show |
| `--type` | see Chart Types | auto-detect | Chart type |
| `--data` | file path | none | Input data file (CSV, TSV, or JSON) |
| `--render` | flag | off | Render to image after generating data file |
| `--format` | `svg`, `png` | `svg` | Output image format |
| `--theme` | `light`, `dark`, `both` | `both` | Theme variant(s) to render |
| `--width` | integer | 600 | Chart width in pixels |
| `--height` | integer | 400 | Chart height in pixels |
| `--title` | text | none | Chart title (also used as aria-label) |
| `--output` | file path | `./charts/<name>.<format>` | Output file path |
| `--help` | flag | off | Show help |

### Examples

```
/adk:chart "Monthly revenue comparison Q1 vs Q2" --type bar --data revenue.csv
/adk:chart "User growth over time" --type line --render
/adk:chart "Traffic distribution by region" --type pie --data traffic.json --render --format png
/adk:chart "API latency percentiles" --type bar --render --theme both
/adk:chart "Sprint velocity" --type bar --data sprints.csv --render
/adk:chart "Cost projections" --type area --render --format png
/adk:chart --help
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, data source, chart type, and output format |
| 1. Research & Options | yes | Analyze data, determine chart type and data structure |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Generate data file and render chart |
| 5. Validate & Learn | yes | Verify rendering, check data accuracy, confirm readability |

## Human in the Loop

- **Plan first (Phase 0)**: Confirm intent — data source, chart type, dimensions, and theme — before generating.
- **Auto mode**: When invoked with `--auto` or by a parent skill, skip confirmations and proceed directly.

## Workflow

### Phase 0: Intent Confirmation

Confirm: chart type, data source (existing file or data to generate), output format, dimensions, and theme.

### Phase 1: Data Analysis

If `--data` is provided, read the file and analyze its structure. If no data file exists, create one from the user's description or research.

Determine the best chart type if not specified:

| Data Pattern | Recommended Chart Type |
|-------------|----------------------|
| Categories with values | `bar` or `horizontal-bar` |
| Time series | `line` or `area` |
| Part-of-whole composition | `pie` or `donut` |
| Two-variable correlation | `scatter` or `bubble` |
| Multiple series comparison | `stacked-bar` or `grouped-bar` |
| Distribution | `histogram` or `box` (if supported) |
| Hierarchical data | `treemap` or `sunburst` |
| Flow/conversion | `funnel` |
| Multi-dimensional comparison | `radar` |
| Single metric with target | `gauge` |
| Price/financial data | `candlestick` |
| Heat patterns | `heatmap` |
| Progress over time | `waterfall` |

### Phase 4: Generate Chart

#### Step 1: Prepare Data File

Create a data file in the `./charts/` directory (or user-specified location).

**CSV format** (preferred for simple data):

```csv
Category,Value,Series
Q1,120000,Revenue
Q2,145000,Revenue
Q1,95000,Costs
Q2,105000,Costs
```

**JSON format** (for complex or nested data):

```json
[
  {"category": "Q1", "revenue": 120000, "costs": 95000},
  {"category": "Q2", "revenue": 145000, "costs": 105000}
]
```

#### Step 2: Render

```bash
chartts render --type <chart-type> --data <file> -o <output-path> [options]
```

Full render command:

```bash
# SVG output (default)
chartts render --type bar --data ./charts/data.csv -o ./charts/revenue.svg --width 600 --height 400 --theme light

# PNG output
chartts render --type bar --data ./charts/data.csv -o ./charts/revenue.png --width 600 --height 400 --theme light --scale 2

# Both themes
chartts render --type bar --data ./charts/data.csv -o ./charts/revenue-light.svg --theme light
chartts render --type bar --data ./charts/data.csv -o ./charts/revenue-dark.svg --theme dark
```

#### Step 3: Dark Mode

For `--theme both`, render two variants:
- `<name>-light.svg` with `--theme light`
- `<name>-dark.svg` with `--theme dark`

### Phase 5: Validate & Report

```
Chart rendered:
  Data: ./charts/revenue-data.csv
  Light: ./charts/revenue-light.svg
  Dark: ./charts/revenue-dark.svg

Render with: chartts render --type bar --data ./charts/revenue-data.csv -o ./charts/revenue.svg
```

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

## Data Preparation Guidelines

### From Raw Numbers in Documents

When a document contains metrics, performance data, or comparisons described in prose, extract the data into a structured format:

1. Identify the data points from the text
2. Determine the appropriate chart type
3. Create a CSV/JSON file with the structured data
4. Render the chart

### From Existing Data Files

When `--data` points to an existing file:
1. Read and validate the file format (CSV, TSV, JSON)
2. Auto-detect columns suitable for the chart type
3. Use `--x` and `--y` flags to specify columns if auto-detection fails

### Generating Sample/Projected Data

When the chart shows projections or estimates:
1. Clearly label projected data points
2. Use different visual styling (dashed lines for projections)
3. Include data source notes

## Theming

### Light Theme (Default)

Clean white background with standard chart colors. Suitable for documents, presentations, and print.

### Dark Theme

Dark background with adjusted colors for visibility. Suitable for dark-mode documentation and dashboards.

### Color Accessibility

- Chart.ts uses a default palette designed for color vision deficiency (CVD) accessibility
- For custom colors, ensure WCAG AA contrast ratio against the background
- Use patterns or textures in addition to color when distinguishing more than 4 series

## Quality Standards

1. **Descriptive title** — every chart must have a title via `--title` that describes what the chart shows
2. **Labeled axes** — use `--x` and `--y` flags or column headers that serve as axis labels
3. **Readable scale** — choose dimensions that prevent label overlap
4. **Data source** — keep the data file alongside the chart for reproducibility
5. **Both themes** — render both light and dark variants unless the target medium is fixed
6. **Appropriate type** — match the chart type to the data pattern (see recommendation table)
7. **Accessible** — include alt text when embedding in documents

## Integration with Other Skills

### Document Skills (`docs-crud`, `docs-write`)

When invoked from a document skill:
- The chart data is derived from the document content (metrics, comparisons, projections)
- Output is placed in a `charts/` subdirectory relative to the document
- Both the data file and rendered chart are kept
- The document embeds the chart with markdown image syntax

### Diagram Skills

Charts and diagrams serve different purposes:
- **Charts**: quantitative data visualization (numbers, metrics, trends)
- **Diagrams**: structural and relational visualization (architecture, flows, sequences)

Use charts for data, diagrams for structure. Some documents need both.

## When to Use This Skill

| Scenario | Use Chart Skill | Use Diagram Skill |
|----------|----------------|-------------------|
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

- `/adk:diagram` — structural and relational diagrams (architecture, flows, ER)
- `/adk:docs-crud` — document creation that may embed charts
- `/adk:docs-write` — formal document writing that may embed charts
- `/adk:diagram-mermaid` — Mermaid-based diagrams (some chart types overlap: pie, xy, gantt)
- `/adk:diagram-graphviz` — Graphviz DOT diagrams for dependency graphs
