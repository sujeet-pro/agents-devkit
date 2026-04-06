# Edges — attributes, arrows, routing, layout hints

Edges inherit **`edge [...]`** defaults; per-edge `[...]` overrides.

## Edge attributes (common)

| Attribute | Purpose |
|-----------|---------|
| `label`, `headlabel`, `taillabel` | Center / head / tail labels (e.g. multiplicity) |
| `xlabel` | External label (often less overlap than `label`) |
| `dir` | `forward`, `back`, `both`, `none` — arrow direction semantics |
| `arrowhead`, `arrowtail` | Arrow glyph at head/tail (see table below) |
| `style` | `solid`, `dashed`, `dotted`, `bold`, `invis`, … |
| `color`, `fontcolor`, `penwidth` | Stroke and text |
| `weight` | Layout priority (higher → often shorter, stronger pull) |
| `constraint` | `true`/`false` — participate in ranking (dot) |
| `minlen` | Minimum rank separation on edge (dot) |

```dot
a -> b [label="calls", dir=forward, arrowhead=normal, penwidth=1.2];
```

## Arrowhead / arrowtail types

Typical values: `normal`, `inv`, `dot`, `invdot`, `odot`, `invodot`, `none`, `tee`, `empty`, `invempty`, `diamond`, `odiamond`, `ediamond`, `crow`, `box`, `obox`, `open`, `halfopen`, `vee`, …

```dot
// ER-style
parent -- child [arrowhead=tee, arrowtail=crow];   /* one / many */
uses --> impl [arrowhead=odiamond];                /* aggregation */
owns --> part [arrowhead=diamond];                 /* composition */
```

Combine with `dir`: e.g. `dir=both` for arrows on both ends.

## Edge routing (`splines`)

Graph-level attribute (often on `graph [...]`):

| Value | Behavior |
|-------|----------|
| `true` / `yes` | Curved splines (default style depends on engine) |
| `false` / `no` | Line segments |
| `polyline` | Polyline |
| `ortho` | Orthogonal (axis-aligned), useful for block diagrams |
| `curved` | Curved edges |
| `line` | Straight lines |

```dot
digraph {
    graph [splines=ortho];
    ...
}
```

Not every engine honors all spline modes equally; **`dot`** is the usual choice for hierarchical + ortho.

## Invisible edges

**`style=invis`** keeps edges in the layout graph but hides drawing — useful to align nodes or enforce spacing without showing a line.

```dot
a -> b [style=invis];
```

## Same-rank and ordering (`dot`)

Force nodes on one layer:

```dot
{ rank=same; A; B; C; }
```

Other helpers: `rank=min`, `rank=max`, `rank=sink`, `rank=source` on subgraphs. Chains of `weight` and invisible edges tune horizontal order within a rank.

**Note:** Rank constraints apply to the **`dot`** engine; spring layouts (`neato`, `fdp`, …) ignore rank.
