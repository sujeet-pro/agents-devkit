# Layout patterns and spatial organization

Use a **20px grid** (`appState.gridSize: 20`) so x/y values snap cleanly and diagrams align in Excalidraw and exports.

## Spacing

- **~60px** between adjacent peer elements (adjust per element size).
- **~120px** between **groups** (swim lanes, layers, clusters).
- Keep title row **high** (low `y`), then stack layers downward or flow stages left-to-right.

## Grid-based placement

Pick base coordinates on multiples of 20, e.g. columns at `100, 320, 540` (200px column + 20px gutter) or use the row/column tables in `SKILL.md` Phase 1.

## Hub-and-spoke

Place a **central** rectangle (hub) at roughly the canvas center. Arrange satellites on a circle or compass points; route arrows radially. Stagger multiple arrows from the same edge (20%–80% along the edge) to reduce overlap.

## Left-to-right flow

For pipelines or stages: **same `y`**, increase **`x`** per stage (e.g. `100, 360, 620, 880`). Arrows point **right** with horizontal `points` or short elbows into the next box.

## Top-down hierarchy

For trees and stacks: **same `x`** per column, increase **`y`** per level (e.g. rows at `100, 230, 380, 530`). Vertical arrows use `[[0,0],[0,dy]]` or elbows when columns differ.

## Swim lanes

Use **wide horizontal bands**:

1. Large **rectangle** per lane (`strokeStyle: "dashed"`, light fill or transparent).
2. **Standalone** lane title `text` at top-left (`containerId: null`).
3. Place services inside the lane; keep **120px** vertical gap between lane rectangles.

## Frames

`frame` elements group related content for focus and exports in the app. Set child elements’ **`frameId`** to the frame’s `id` when grouping a subsystem. Use frames for “slides” or bounded regions, not as a substitute for dashed group boxes if you only need a visual boundary (rectangles are simpler in JSON).

## Consistency checklist

- Snap positions to the **20px** grid.
- One **dominant** reading order (LR or TB), mixed only when the diagram type requires it.
- Reserve **margins** (~80px) from canvas edges for titles and notes.

## Example column grid (LR)

Typical service width **160–200px**. With **60px** gap:

| Col | x (left) |
|-----|----------|
| 0 | 100 |
| 1 | 360 |
| 2 | 620 |
| 3 | 880 |

Place all stage boxes at **`y: 200`**; arrows connect **right** edge of col *i* to **left** edge of col *i+1*.

## Example row stack (TB)

| Row | y (top) | Content |
|-----|---------|---------|
| Title | 20 | Diagram title `text` |
| Clients | 100 | Users, BFF |
| Gateway | 230 | API gateway |
| Services | 380 | Domain services |
| Data | 530 | DB, cache, queues |

Increase **y** by **~130–150px** per layer so arrows and labels fit between rows.

## Z-order

List elements in **dependency order** in `elements[]`: draw **lanes and group rectangles first**, then nodes, then arrows, then floating labels — so connectors render above backgrounds without extra logic (Excalidraw still uses explicit ordering; when in doubt, match how you would paint layers).
