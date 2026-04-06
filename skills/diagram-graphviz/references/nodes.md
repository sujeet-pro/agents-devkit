# Nodes — shapes, records, HTML labels, styling

Use **semantic node IDs** (`auth_service`) with human-readable **labels**.

## Common shapes (keywords)

| Shape | Typical use |
|-------|-------------|
| `box`, `ellipse` | Modules, steps (ellipse is common default) |
| `circle`, `doublecircle` | States, start/final in automata |
| `diamond` | Decisions |
| `plaintext` | Label-only (minimal border) |
| `record`, `Mrecord` | Fields and ports (see below) |
| `point` | Invisible junction / pseudo start |
| `doubleoctagon`, `tripleoctagon` | Emphasis layers |
| `house`, `invhouse` | Sources / sinks |
| `pentagon`, `hexagon`, `septagon`, `octagon` | Polygon variants |
| `star` | Highlights |
| `folder`, `component`, `tab`, `note` | Packages, UML, annotations |
| `box3d`, `cylinder` | 3D box, databases / storage |

```dot
node [shape=cylinder];
db [label="PostgreSQL"];
```

## Record labels (`shape=record`)

- **`|`** separates fields **vertically** (rows).
- **`{ ... }`** groups fields **horizontally** (columns).
- Nesting `{ a | { b | c } }` builds tables of cells.

```dot
node [shape=record];
user [label="{User|+ id: int\l+ name: string\l|+ save()\l}"];
```

- **`\l`** left-aligns line in record text; **`\r`** right; **`\n`** centered newline.

## HTML-like labels

Use **`label=<...>`** with a small subset of HTML: `<TABLE>`, `<TR>`, `<TD>`, `<FONT>`, `<BR>`, etc. Good for rich formatting and **named ports**.

```dot
rich [label=<
  <TABLE BORDER="0">
    <TR><TD PORT="p1">A</TD><TD PORT="p2">B</TD></TR>
  </TABLE>
>];
```

## Ports

- **Record / HTML**: define named ports in label (`<portname>` in record, `PORT="name"` in HTML).
- **Syntax**: `tail_node:port` → `head_node:port` (directed edges).
- **Compass**: append `:n`, `:ne`, `:e`, `:se`, `:s`, `:sw`, `:w`, `:nw`, `:c` to anchor the attachment point.

```dot
node [shape=record];
a [label="<left> L | <right> R"];
b [label="Target"];
a:left -> b;
```

## Style attributes (common)

| Attribute | Notes |
|-----------|--------|
| `shape`, `style` | Combine: `filled`, `dashed`, `dotted`, `bold`, `rounded` |
| `fillcolor`, `color`, `penwidth` | Fill, border, stroke width |
| `fontcolor`, `fontname`, `fontsize` | Text |
| `width`, `height`, `fixedsize`, `margin` | Size (inches), fixed box, padding |

```dot
x [shape=box, style="rounded,filled", fillcolor="#dae8fc", color="#6c8ebf", fontcolor="#333333"];
```

Use records for simple tables; HTML for multi-cell layout. Theme-friendly fills: main `SKILL.md` color table.
