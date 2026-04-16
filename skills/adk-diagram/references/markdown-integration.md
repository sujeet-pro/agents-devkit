# Markdown Integration

## Default Embed Pattern

Prefer a theme-aware `<picture>` block when the markdown target accepts inline HTML. The paths below assume the default `.diagramkit/` output folder; if the project uses `sameFolder: true`, drop the `.diagramkit/` segment.

```html
<figure>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./diagrams/auth-flow-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="./diagrams/auth-flow-light.svg" />
    <img alt="Authentication flow showing user login request through OAuth provider, token exchange, and session creation" src="./diagrams/auth-flow-light.svg" />
  </picture>
  <figcaption>Authentication flow</figcaption>
</figure>
```

Use `alt` for a detailed description of what the image renders (for accessibility and fallback). Use `<figcaption>` for a short visible label shown below the image.

If the markdown target or repo style avoids inline HTML, fall back to a plain markdown image link:

```md
![Auth flow](./diagrams/auth-flow-light.svg)
```

## Docs-Framework Embed Pattern

Some docs frameworks (e.g. Pagesmith, VitePress) support class-based theme switching instead of `<picture>`. If the project uses `.only-light` / `.only-dark` classes:

```html
<figure>
  <img src="./diagrams/auth-flow-light.svg" class="only-light" alt="Authentication flow showing user login request through OAuth provider, token exchange, and session creation">
  <img src="./diagrams/auth-flow-dark.svg" class="only-dark" alt="Authentication flow showing user login request through OAuth provider, token exchange, and session creation">
  <figcaption>Authentication flow</figcaption>
</figure>
```

Use `alt` for a detailed description of what the image renders. Use `<figcaption>` for a short visible label.

Pagesmith also provides these additional classes:

- `.show-on-light` / `.show-on-dark` — generic helpers for toggling any element (not just images) by color scheme
- `.invert-on-dark` — applies `invert(1) hue-rotate(180deg)` in dark mode, useful for simple black-and-white diagrams that don't need separate light/dark renders:

```html
<figure>
  <img src="./diagrams/simple-flow.svg" class="invert-on-dark" alt="Linear data flow from ingestion through validation to storage">
  <figcaption>Data pipeline</figcaption>
</figure>
```

Pagesmith sets `color-scheme-auto` on `<html>` by default, which follows the OS `prefers-color-scheme` media query. Explicit `color-scheme-light` or `color-scheme-dark` classes force the matching variant regardless of OS preference.

Check the project's existing diagram embeds to determine which pattern to use.

## Placement Rules

- If the user names a section or there is an obvious matching heading, place the embed directly below that section.
- If an existing embed for the same diagram slug exists, replace it instead of adding a duplicate.
- If there is no obvious insertion point, append a short `## Diagram` or `### Diagram` section near the end of the relevant document area.

## Relative Paths

- Compute paths from the markdown file location, not from the repo root.
- If `diagramkit.config.json5` or another diagramkit config renders assets outside the sibling `diagrams/` folder, update the markdown to the actual rendered SVG path.

## Source Note

When the document would benefit from it, add a brief note that the editable source lives alongside the rendered asset:

```md
Source: `./diagrams/auth-flow.mermaid`
```

Keep this optional. Do not add noisy boilerplate to short docs.