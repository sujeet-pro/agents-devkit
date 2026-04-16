# ADK Chart Workflow

## Phases

### Phase 1: Understand
Clarify the data source, chart type, audience, and what question the chart should answer.

**Inputs:** user chart request, `--type`, `--data`, `--format` flags
**Actions:**
- Parse the chart request and identify the question to answer
- Identify the data source (file path, inline data, or generated)
- Determine the target audience and context (doc, report, presentation)
- Determine output format (SVG or PNG)
- Present confirmation summary to user

**Gate:** User confirms data source, chart type, and audience. Skip when `--auto` is set.

**Outputs:** confirmed chart goal, data source, audience

### Phase 2: Analyze
Inspect the data structure, identify key metrics, and assess chart suitability.

**Actions:**
- Read the data source file (CSV, JSON, etc.)
- Identify columns, data types, ranges, and distributions
- Detect outliers, missing values, or data quality issues
- Identify the key metrics and relationships relevant to the question
- Determine appropriate scales, groupings, and aggregations
- Assess whether a chart is the right format (vs. table or summary number)

**Outputs:** data analysis summary, recommended chart configuration

### Phase 3: Design
Choose chart type, layout, color scheme, and axis configuration.

**Chart type decision matrix:**

| Data shape | Question type | Chart type |
| --- | --- | --- |
| Categories / groups | Comparison | Bar (horizontal for long labels) |
| Time series | Trend | Line |
| Parts of whole (2-6 items) | Composition | Pie / Donut |
| Two numeric variables | Relationship | Scatter |
| Time series + composition | Cumulative trend | Area (stacked) |
| Single variable distribution | Distribution | Histogram |
| Two dimensions + intensity | Density | Heatmap |
| Sequential stages | Drop-off | Funnel |
| Exact numbers matter most | Precision | Table (not a chart) |

**Actions:**
- Match data shape and question to the decision matrix above
- If a table or single number would communicate the data more clearly, recommend that instead
- Define axis labels, titles, units, and legend
- Choose color scheme with accessibility in mind (contrast, patterns, secondary encoding)
- Plan layout: grouped vs stacked, horizontal vs vertical, annotations
- Present preview description for user approval

**Gate:** User approves chart design. Skip when `--auto` is set.

**Outputs:** approved chart design specification

### Phase 4: Implement
Generate the chart with reusable source and rendered asset.

**Actions:**
- Create or prepare the data file in a reusable format
- Generate the chart using available rendering tooling
- Keep the data file and chart source alongside the rendered output
- Render in the requested format (SVG preferred)

**Outputs:** rendered chart, data file, chart source

### Phase 5: Validate
Verify data accuracy, readability, and accessibility.

**Actions:**
- Cross-check rendered chart values against source data
- Verify labels, scale, legend, and title are interpretable
- Check axis honesty: no misleading truncation or distortion
- Validate color accessibility: contrast ratios, secondary encoding
- Confirm assumptions are stated for illustrative data

**Outputs:** validation results

### Phase 6: Deliver
Place chart with source alongside rendered output, report results.

**Actions:**
- Place rendered chart and data file in the target location
- Report file paths for data source, chart config, and rendered output
- State chart rationale, assumptions, and validation results
- Offer to adjust chart type, layout, or details

**Outputs:** structured chart report

## Validation Rules
- Chart type matches the data shape and question
- Labels, titles, units, and legends are interpretable without external context
- Scale is honest: no truncated axes or misleading baselines without annotation
- Assumptions are stated for illustrative data
- Color choices meet accessibility contrast requirements
- Rendered chart data matches source data

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Understand): skip user confirmation, proceed with parsed intent
- Phase 3 (Design): skip design approval, use recommended configuration
- Phase 5 (Validate): still runs full validation
- Phase 6 (Deliver): still reports full results with all sections
