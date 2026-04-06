# Export and rendering

The **`.excalidraw` file is the source of truth**. Commit it beside any generated images so diagrams stay editable and diffable.

## diagramkit CLI

Install/use via npm (`diagramkit` is listed in the skill dependencies). Render from the repo root or path to the file:

```bash
npx diagramkit render path/to/diagram.excalidraw --format svg --theme both
```

| Flag | Role |
|------|------|
| `--format svg` | Vector output for **web** embedding, scales cleanly |
| `--format png` | Raster for **docs**, slides, or raster-only pipelines |
| `--theme both` | Emit **light and dark** variants (when supported) |
| `--theme light` / `--theme dark` | Single theme only |

Adjust paths to match your project; the skill’s `SKILL.md` also shows `diagramkit render diagram.excalidraw` without `npx` when globally available.

## Outputs

- **SVG** — preferred for READMEs, static sites, and Confluence/HTML (crisp at any zoom).
- **PNG** — use for PDFs or platforms that mishandle SVG; request **higher scale** if the CLI exposes a scale/DPI option for retina displays.

## Themes

Generate **both** themes for documentation that supports light/dark reading modes. If only one theme is needed, pick **SVG + light** for maximum compatibility.

## Scale / high-DPI

When bitmap output is required, prefer **2× scale** (or the CLI’s equivalent) for sharp screenshots on retina displays — check `diagramkit --help` for the exact flag name in your version.

## Workflow

1. Edit or generate **`*.excalidraw`** JSON.
2. Run **`npx diagramkit render ...`** to produce `svg`/`png`.
3. **Keep** the `.excalidraw` next to assets (e.g. `docs/diagrams/architecture.excalidraw` + `architecture.svg`).
4. In docs, **link or embed** the rendered file; mention the source path for maintainers.

Never replace the JSON source with only a PNG/SVG without storing the editable file.

## Naming and repo layout

Suggested pattern:

- `docs/diagrams/<topic>.excalidraw` — source
- `docs/diagrams/<topic>.svg` — rendered (light, or default)
- If the tool emits suffixed themes: `*.light.svg`, `*.dark.svg` — link both from docs that support theme switching

Use **kebab-case** filenames to match URLs and avoid spaces in CI.

## Validation before commit

- Open the SVG in a browser or doc preview; check **fonts** and **colors** match intent.
- For **dark** SVGs, confirm strokes are visible on the target background.
- Re-run render after JSON edits in CI or pre-commit if you enforce **parity** between source and assets.

## Quick reference

```bash
# SVG, both themes (typical docs pipeline)
npx diagramkit render ./docs/diagrams/system.excalidraw --format svg --theme both

# PNG for a slide deck, dark only
npx diagramkit render ./docs/diagrams/system.excalidraw --format png --theme dark
```

If `npx` resolves an older **diagramkit**, pin the version in `package.json` for reproducible exports.
