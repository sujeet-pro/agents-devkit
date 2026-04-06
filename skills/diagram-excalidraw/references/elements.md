# Excalidraw element types and properties

`.excalidraw` files are **JSON**. The root object has `type: "excalidraw"`, `elements[]`, `appState`, and optional `files` for embedded images. Every element has a unique `id`; **`type`** selects the element kind.

## IDs

Use **nanoid-style** strings, e.g. `elem_abc123`, `arrow_svc_db`. Duplicate IDs break the file.

## Element kinds (`type`)

| `type` | Role |
|--------|------|
| `rectangle` | Boxes, services, layers, groups (dashed stroke for groups) |
| `diamond` | Decision nodes in theory — **see caveat below** |
| `ellipse` | Actors, start/end, external systems |
| `arrow` | Connections, flows (also supports elbow routing) |
| `line` | Plain polyline; set arrowheads to `null` for no heads |
| `text` | Labels; pair with shapes via `containerId` / `boundElements` |
| `image` | Raster assets; references `files` map by file id |
| `frame` | Visual grouping / export regions in the editor |
| `freedraw` | Hand-drawn strokes |

**Caveat (diamond):** For raw JSON diagrams in this skill, **avoid diamonds for anything that needs arrows** — vertex rounding can misalign bindings. Prefer styled rectangles for decisions (see main `SKILL.md`).

## Core geometry and style

| Property | Meaning |
|----------|---------|
| `x`, `y` | Top-left of the element’s bounding box (arrows: origin of `points`) |
| `width`, `height` | Size of bounding box; for arrows, derive from `points` (see arrows reference) |
| `angle` | Rotation in radians (often `0`) |
| `strokeColor`, `backgroundColor` | Hex strings, e.g. `"#1971c2"` |
| `fillStyle` | e.g. `"solid"`, `"hachure"`, `"cross-hatch"` |
| `strokeWidth` | Line weight |
| `roughness` | `0` = crisp, `1` = hand-drawn |
| `opacity` | `0`–`100` |
| `roundness` | Corner curve; `{ "type": 3 }` for rounded rects; `null` for sharp/elbow arrows |

## Relationships and links

| Property | Meaning |
|----------|---------|
| `groupIds` | Array of group ids so elements move together |
| `frameId` | Id of containing frame, or `null` |
| `boundElements` | List of `{ "type": "text"|"arrow", "id": "..." }` attached to this shape |
| `link` | Optional hyperlink string or `null` |

## Minimal rectangle snippet

```json
{
  "id": "elem_svc_api",
  "type": "rectangle",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 80,
  "angle": 0,
  "strokeColor": "#1971c2",
  "backgroundColor": "#a5d8ff",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "roughness": 1,
  "opacity": 100,
  "roundness": { "type": 3 },
  "groupIds": [],
  "frameId": null,
  "boundElements": [{ "type": "text", "id": "elem_svc_api-text" }],
  "link": null
}
```

Labeled shapes need a **separate** `text` element with `containerId`; do not rely on a `label` field in raw JSON (see `SKILL.md`).
