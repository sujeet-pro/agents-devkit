# Radar Chart

**Directive:** `radar-beta`

**Syntax:**

```
radar-beta
    title "Chart Title"
    axis1: "Label" 0 --> 10
    axis2: "Label" 0 --> 10
    axis3: "Label" 0 --> 10

    "Series 1": [8, 6, 7]
    "Series 2": [5, 9, 4]
```

**Example:**

```
%% Diagram: Framework Comparison
%% Type: radar
radar-beta
    title "Framework Evaluation"
    axis1: "Performance"
    axis2: "DX"
    axis3: "Ecosystem"
    axis4: "Learning Curve"
    axis5: "Community"

    "Next.js": [8, 9, 9, 6, 9]
    "Remix": [9, 8, 6, 5, 6]
    "SvelteKit": [9, 9, 5, 7, 5]
```
