# Color palettes for diagrams

Use **hex** strings for `strokeColor`, `backgroundColor`, and `appState.viewBackgroundColor`. Keep **pairing** consistent: fill = softer tint, stroke = stronger hue.

## Default (general architecture)

| Role | Stroke | Fill (example) |
|------|--------|----------------|
| Primary / UI | `#1971c2` | light blue tint |
| Success / data | `#2f9e44` | light green |
| Accent / ops | `#e8590c` | light orange |
| Error / external risk | `#e03131` | light red |
| Secondary / API | `#7048e8` | light purple |
| Neutral / infra | `#868e96` | gray tint |

Core accents: **blue** `#1971c2`, **green** `#2f9e44`, **orange** `#e8590c`, **red** `#e03131`, **purple** `#7048e8`, **gray** `#868e96`.

## AWS

- Orange **`#FF9900`** (brand / compute emphasis)
- Dark blue **`#232F3E`** (text, borders, dark panels)
- Light blue **`#527FFF`** (secondary highlights)

## Azure

- Blue **`#0078D4`**
- Teal **`#008575`**
- Purple **`#5C2D91`**

## GCP

- Blue **`#4285F4`**
- Red **`#EA4335`**
- Yellow **`#FBBC05`**
- Green **`#34A853`**

## Kubernetes

- Blue **`#326CE5`** (workloads)
- White **`#FFFFFF`** (icons on blue, or light panels with dark stroke)

## Light vs dark canvas

- **Light mode:** `appState.viewBackgroundColor`: `"#ffffff"` — use standard saturated strokes and pastel fills.
- **Dark mode:** prefer **`#1e1e1e`** (or similar) for **background** in source when authoring dark-native diagrams; use **slightly lighter** fills and **higher-contrast** strokes so shapes remain visible.

When using **diagramkit** with `--theme both`, author with the **light** palette first; the tool can generate dark variants — still pick strokes that remain readable on dark surfaces.

## Usage tips

- Limit **3–5** fill hues per diagram; repeat for layers instead of new colors.
- Use **dashed** strokes and neutral grays for **boundaries** (VPC, namespace), not fills.
- Match **palette** to audience (AWS/Azure/GCP) for quick recognition.
