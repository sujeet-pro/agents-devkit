# `docs-diagram` — artifact format

```
.temp/task-<slug>/
├── prompt.txt                 # verbatim user prompt + timestamp
├── elements.md                # (only if --scope) node + edge list with citations
├── <subject>.mermaid          # the Mermaid source
├── <subject>.light.svg        # (if diagramkit available)
├── <subject>.dark.svg         # (if diagramkit available)
├── validation/
│   └── docs-diagram.md        # per-phase validator log (incl. render output)
└── report.md                  # final consolidated report
```

## Slug

- `diagram-<type>-<kebab-subject>`, e.g.
  `diagram-sequence-oidc-login`.
- If the subject is long, truncate to 6 kebab-words.
- If the same slug would collide, add `-N` suffix.

## Split outputs

When the concept exceeds 15 nodes and the skill auto-splits:

```
.temp/task-<slug>/
├── <subject>.overview.mermaid
├── <subject>.overview.light.svg / .dark.svg
├── <subject>.<zoom-name>.mermaid
├── <subject>.<zoom-name>.light.svg / .dark.svg
└── report.md
```

`<zoom-name>` is the subsystem's name (e.g. `checkout-zoom`).

## `elements.md` shape (under `--scope`)

```markdown
# elements — <slug>

## Nodes

| Id | Label | Source |
| --- | --- | --- |
| `cart-svc` | "Cart Service" | `services/checkout/src/main/kotlin/com/acme/CartService.kt:10` |
| `orders-db` | "Orders DB" | `db/schema.sql:1` |

## Edges

| From | To | Label | Source |
| --- | --- | --- | --- |
| `cart-svc` | `orders-db` | "writes" | `CartService.kt:42-58 (uses JdbcTemplate)` |
| `web-ui` | `cart-svc` | "POST /cart/add" | `web/src/api/cart.ts:12` |
```

## Rules

1. Every diagram file is self-contained — no cross-file references.
2. The `.mermaid` file starts with the title comment line.
3. If diagramkit rendered, the SVGs are kept next to the source.
4. Never write outside `.temp/task-<slug>/`.
