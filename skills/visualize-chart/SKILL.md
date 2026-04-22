---
name: visualize-chart
description: Produce a numeric or categorical chart - bar, line, pie, scatter, histogram, stacked area, heatmap - from a data source (CSV, JSON, inline values, or a SQL/REST query result). Use when the deliverable is a data plot, with the editable spec saved alongside the rendered image. Do not use for structural diagrams (use adk-visualize-diagram) or UI mockups (use adk-frontend-design).
metadata:
  category: docs
  kind: task
  layer: 6
  modes: [auto]
---

# ADK Visualize / Chart

Standalone task skill under the `@adk:visualize` (a.k.a. `adk-visualize`) category router. Produces an editable chart spec first, then renders to the destination format. The editable spec is always kept alongside the rendered image.

## When to use

- Bar, line, pie, scatter, histogram, stacked area, or heatmap from real data.
- Chart must be embedded in a markdown doc, an audit report, or a slide.
- Existing chart needs regeneration with new data or a different style.

## When NOT to use

- Structural / relationship picture -> `@adk:visualize-diagram` (a.k.a. `adk-visualize-diagram`)
- UI mockup or component design -> `@adk:frontend-design` (a.k.a. `adk-frontend-design`)
- One-off stat printed in prose - just write the number, no chart needed

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<chart type>` | yes | `bar` / `line` / `pie` / `scatter` / `histogram` / `stacked-area` / `heatmap` |
| `<data source>` | yes | Path to CSV / JSON, inline values, or a one-shot query result |
| `<x>` `<y>` `<series>` | yes when applicable | Field names mapping to axes / series |
| `<format>` | optional | `vega-lite` (default - editable JSON) / `python-mpl` / `mermaid` (limited subset) |
| `<render>` | optional | `svg` (default) / `png` / `none` |
| `<output path>` | optional | Defaults to `.temp/drafts/chart-<slug>.<ext>` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate chart type, data source, axis mapping, format, render target. Approval gate unless `--auto`.
2. **Inspect data** - read first ~20 rows; identify columns, types, missing values, and obvious outliers. Note row count and value range.
3. **Decide encoding** - confirm chart type fits the data shape:
   - Bar: categorical x, numeric y.
   - Line: ordinal/temporal x, numeric y, optional series.
   - Pie: small set of categories summing to a meaningful whole.
   - Scatter: two numeric variables, optional categorical color.
   - Histogram: one numeric variable, choose bin count.
   - Stacked area: temporal x, multiple numeric series with shared meaning.
   - Heatmap: two categorical/ordinal axes, one numeric value.
4. **Draft spec** - write the editable spec (vega-lite JSON by default, matplotlib script as a `# /// script` PEP 723 file, or mermaid for the limited subset).
5. **Render** - produce SVG (preferred for markdown) or PNG (preferred for print / email). Keep the editable spec next to it.
6. **Validate** - check: axes labeled with units, legend present when needed, value range visible (no truncated y starting at non-zero without a note), color count <= 7.
7. **Report** - chart path + spec path; key insight from the data in one bullet; offer to tweak.

## Format defaults

| Destination | Default format | Render |
| --- | --- | --- |
| Markdown report | vega-lite spec | SVG file linked from markdown |
| Audit / handoff PDF | vega-lite spec | PNG @ 300 dpi |
| Slide deck | vega-lite spec | SVG, exportable to deck |
| Quick inline ASCII view | mermaid pie / xy chart | Inline mermaid block |

## Vega-Lite quick reference

This skill produces vega-lite by default. Key fields:

- `mark`: `"bar"`, `"line"`, `"point"`, `"area"`, `"rect"` (heatmap).
- `encoding.x` / `encoding.y`: `{ "field": "...", "type": "quantitative" | "nominal" | "ordinal" | "temporal" }`.
- `encoding.color`: series mapping.
- Always set `title`, axis `title`, and unit hint when applicable.

Minimal example:

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
  "title": "Sales by month",
  "data": { "url": "sales.csv" },
  "mark": "bar",
  "encoding": {
    "x": { "field": "month", "type": "ordinal", "title": "Month" },
    "y": { "field": "revenue", "type": "quantitative", "title": "Revenue (USD)" }
  }
}
```

## Matplotlib (PEP 723) alternative

When matplotlib is requested, ship a self-contained Python script using PEP 723 inline deps so it runs with `uv run`:

```python
# /// script
# dependencies = ["matplotlib", "pandas"]
# ///
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sales.csv")
fig, ax = plt.subplots()
ax.bar(df["month"], df["revenue"])
ax.set_title("Sales by month")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue (USD)")
fig.savefig("sales.svg")
```

## Output format

```
## Chart: <type>
- Spec: `<path>`
- Render: `<path or none>`
- Format: <vega-lite | python-mpl | mermaid>
- Rows: <N>
- Columns used: <list>

## Headline
<one-bullet insight from the data>

## Preview
<inline embed when destination supports it>

Want a tweak (different bins, different series, log scale)?
```

## Hard rules

- Always keep the editable spec alongside any rendered image.
- Always label axes with units when units exist.
- Limit to ~7 distinct colors per chart; if more series exist, group or facet.
- Do not start a numeric y-axis above zero without an explicit note ("y zoomed to range").
- Do not use 3D effects, gradients, or shadows. Flat data, flat ink.

## Anti-patterns

- Chart with no axis labels.
- Pie chart with >5 slices (legibility falls off a cliff).
- Truncating the y-axis to dramatize a small change without flagging it.
- Producing a PNG without keeping the spec - the chart cannot be re-rendered when the data changes.
- Color-only encoding for categories when print / colorblind users matter.

## Examples

```
adk-visualize-chart bar --data sales-2026.csv --x month --y revenue
```

```
adk-visualize-chart line --data api-latency.json --x ts --y p99 --series endpoint --render png
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-chart-clarifying-questions.md`) and reports the choices.

1. **What is the data source (file path, URL, query)?** — _How to pick:_ File = csv/json/parquet. URL = HTTP fetch (cache to .temp/notes/). Query = SQL/PromQL/etc., capture the query string.
2. **What story does the chart tell — what should the reader take away?** — _How to pick:_ One sentence. The chart type and design follow from this.
3. **Audience (engineer / leadership / external)?** — _How to pick:_ Engineer = denser, more annotations OK. Leadership = simpler, big takeaway label. External = no jargon, brand-safe colors.

**Default report:** Chart image path + the takeaway sentence + data-source citation.

**Detailed report (on request or `--verbose`):** Add: alternative chart types considered, data-cleaning steps, statistical caveats (sample size, missing data, outliers).

**Artifact:** `chart-image-and-source` — Rendered image (`*.svg` preferred, `*.png` fallback) + plotting source (`*.py` / `*.js` / `*.r`) + data snapshot.

**Artifact path:** `<page-dir>/charts/<slug>.svg` for embedded charts. Working drafts + data snapshots in `.temp/drafts/charts/<slug>/`.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/visualize-chart-clarifying-questions.md`) and reports the choices.

1. **What is the data source (file path, URL, query)?** — _How to pick:_ File = csv/json/parquet. URL = HTTP fetch (cache to .temp/notes/). Query = SQL/PromQL/etc., capture the query string.
2. **What story does the chart tell — what should the reader take away?** — _How to pick:_ One sentence. The chart type and design follow from this.
3. **Audience (engineer / leadership / external)?** — _How to pick:_ Engineer = denser, more annotations OK. Leadership = simpler, big takeaway label. External = no jargon, brand-safe colors.

## Default vs detailed output

**Default report:** Chart image path + the takeaway sentence + data-source citation.

**Detailed report (on request or `--verbose`):** Add: alternative chart types considered, data-cleaning steps, statistical caveats (sample size, missing data, outliers).

**Artifact:** `chart-image-and-source` — Rendered image (`*.svg` preferred, `*.png` fallback) + plotting source (`*.py` / `*.js` / `*.r`) + data snapshot.

**Artifact path:** `<page-dir>/charts/<slug>.svg` for embedded charts. Working drafts + data snapshots in `.temp/drafts/charts/<slug>/`.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/visualize-chart-anti-patterns.md` | Things to avoid when running this skill. |
| `references/visualize-chart-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/visualize-chart-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/visualize-chart-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/visualize-chart-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/visualize-chart-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/visualize-chart-persona.md` | The agent persona that drives this skill. |
| `references/visualize-chart-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/visualize-chart-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
