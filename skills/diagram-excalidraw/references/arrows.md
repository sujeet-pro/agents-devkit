# Arrows: routing, bindings, and labels

Excalidraw arrows use `type: "arrow"` (or `line` for segments without arrowheads). **`points`** are polyline vertices in **local** coordinates; the arrow’s `x`,`y` is the start anchor, and subsequent points are offsets from that origin.

## `points` routing

`points` is an array of `[dx, dy]` steps from the start. Example elbow:

```json
"points": [[0, 0], [100, 0], [100, 50], [200, 50]]
```

Compute **`width`** / **`height`** as the bounding box of cumulative offsets: take max absolute x and y across all points (see `SKILL.md` arrow bbox rule).

Common patterns:

- Straight down: `[[0,0], [0, dy]]`
- Straight right: `[[0,0], [dx, 0]]`
- L-shape: `[[0,0], [dx,0], [dx,dy]]` or `[[0,0], [0,dy], [dx,dy]]`

For **90° elbows** (not curved), set `elbowed: true`, `roundness: null`, `roughness: 0`.

## `startBinding` and `endBinding`

Bindings attach arrow ends to shapes so the editor can adjust endpoints:

```json
"startBinding": {
  "elementId": "elem_source",
  "focus": 0,
  "gap": 1
},
"endBinding": {
  "elementId": "elem_target",
  "focus": 0,
  "gap": 1
}
```

Optional **`fixedPoint`** on each binding pins the attachment on the shape edge, e.g. top `[0.5, 0]`, bottom `[0.5, 1]`, left `[0, 0.5]`, right `[1, 0.5]`.

**Mirror bindings:** add this arrow to each shape’s `boundElements`:

```json
"boundElements": [
  { "type": "arrow", "id": "arrow_src_tgt" }
]
```

## Labels on arrows

The `label` property is **not** for raw JSON. Use a **`text`** element with `containerId: null`, placed near the arrow midpoint, or use `boundElements` on the arrow for text that should associate in the editor:

```json
"boundElements": [{ "type": "text", "id": "arrow_src_tgt-label" }]
```

## Arrow vs line; arrowheads

- **`type: "line"`** — polyline; use when you want a connector **without** arrowheads (set both heads `null`).
- **`type: "arrow"`** — connector with optional heads.

**`startArrowhead`** / **`endArrowhead`**: `null`, `"arrow"`, `"bar"`, `"dot"`, `"triangle"`. Bidirectional: both ends `"arrow"`.

```json
"startArrowhead": null,
"endArrowhead": "arrow"
```
