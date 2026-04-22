# Markdown Guidelines

Standalone markdown reference for the shared Pagesmith markdown pipeline. This file covers the base features that `@pagesmith/core` exposes directly and that `@pagesmith/docs` builds on top of.

Both packages share the same core unified pipeline. `@pagesmith/docs` then adds docs-specific frontmatter plus a docs-only link and asset rewrite pass after heading extraction. For stock docs authoring rules such as page-local diagram/image publishing, `.inline.svg`, and theme-aware image embedding, also read the bundled [`./markdown-reference.md`](./markdown-reference.md) — the same reference content shipped with `@pagesmith/docs@0.9.9`.

## Pipeline Order

```
remark-parse → remark-gfm → remark-frontmatter
  → remark-github-alerts → remark-smartypants
  → remark-math (when `markdown.math` is `true` or `'auto'` detects math markers)
  → [user remark plugins]
  → lang-alias transform → remark-rehype
  → rehype-mathjax (when math is enabled, before the built-in code renderer)
  → applyPagesmithCodeRenderer (dual themes, line numbers, titles, copy, collapse, mark/ins/del)
  → rehype-code-tabs → rehype-scrollable-tables
  → rehype-slug → rehype-autolink-headings
  → rehype-external-links → rehype-accessible-emojis → rehype-local-images
  → heading extraction → [user rehype plugins] → rehype-stringify
```

## GitHub Flavored Markdown (remark-gfm)

GFM adds tables, strikethrough, task lists, autolinks, and footnotes.

### Tables

```md
| Left | Center | Right |
| :--- | :----: | ----: |
| L    |   C    |     R |
| data |  data  |  data |
```

Column alignment is controlled by colons in the separator row: `:---` for left, `:---:` for center, `---:` for right.

### Strikethrough

```md
~~deleted text~~
```

### Task Lists

```md
- [x] Completed task
- [ ] Pending task
- [ ] Another pending task
```

### Autolinks

Bare URLs are automatically converted to clickable links:

```md
Visit https://pagesmith.dev for more info.
```

### Footnotes

```md
Content with a footnote[^1] and another[^note].

[^1]: This is the footnote content.

[^note]: Footnotes can use any identifier.
```

## GitHub Alerts (remark-github-alerts)

Five alert types using GitHub's blockquote syntax:

```md
> [!NOTE]
> Informational note.

> [!TIP]
> Helpful tip.

> [!IMPORTANT]
> Important information.

> [!WARNING]
> Warning message.

> [!CAUTION]
> Cautionary message.
```

Alerts render as styled callout boxes with an icon and colored left border. The syntax is compatible with GitHub's own rendering.

## Math (remark-math + rehype-mathjax)

Use `$` for inline math and `$$` for display (block) math. Rendered to SVG via MathJax.

Inline: `$E = mc^2$`

Block:

```md
$$
\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}
$$
```

Note: The `$` delimiters must not have spaces immediately inside them for inline math. `$x$` works, `$ x $` does not.

## Smart Typography (remark-smartypants)

ASCII typography is automatically converted to proper typographic characters. Code blocks and inline code are not affected.

| Input     | Output            | Description                                   |
| --------- | ----------------- | --------------------------------------------- |
| `"hello"` | \u201chello\u201d | Straight double quotes to curly double quotes |
| `'hello'` | \u2018hello\u2019 | Straight single quotes to curly single quotes |
| `--`      | \u2013            | Two hyphens to en dash                        |
| `---`     | \u2014            | Three hyphens to em dash                      |
| `...`     | \u2026            | Three dots to ellipsis                        |

## External Links (rehype-external-links)

Only absolute URLs starting with `http://` or `https://` get the external link treatment: `target="_blank"` and `rel="noopener noreferrer"` are added automatically.

Relative links (`/guide/getting-started`, `../about`, `#section`) stay in the same tab and are not modified.

```md
[GitHub](https://github.com) <!-- opens in new tab -->
[Internal page](/guide/getting-started) <!-- stays in same tab -->
[Anchor link](#section) <!-- stays in same tab -->
```

## Accessible Emojis (rehype-accessible-emojis)

Unicode emoji characters in prose are automatically wrapped in accessible markup. No special syntax is needed -- just use emoji characters directly.

```md
Great job! 🎉
```

Renders as:

```html
Great job! <span role="img" aria-label="party popper">🎉</span>
```

The `role="img"` and `aria-label` attributes ensure screen readers announce the emoji's meaning.

## Local Images (rehype-local-images)

When Pagesmith knows the markdown source path, relative local images automatically inherit intrinsic dimensions (`width`, `height`, `style="max-width:min({width}px,100%)"`) from the filesystem. All raster images (PNG, JPEG, WebP, GIF) render as a `<picture>` element with AVIF and WebP `<source>` variants, using the WebP variant as the `<img src>` fallback (broadest modern format support). SVG images are not wrapped in `<picture>` and receive no format conversion.

Every markdown image is wrapped in `<figure class="ps-figure">`. The title attribute from markdown syntax (`![alt](src "title")`) becomes a `<figcaption>`. Images that appear inside `<a>` links are not figure-wrapped (to preserve the link structure). `.avif` source images are passed through as-is without re-wrapping in `<picture>`.

```md
![Hero](./hero.jpg)
![Logo with caption](./logo.png "Company Logo")
```

The first example produces:

```html
<figure class="ps-figure">
  <picture>
    <source srcset="./hero.avif" type="image/avif" />
    <source srcset="./hero.webp" type="image/webp" />
    <img
      src="./hero.webp"
      alt="Hero"
      width="1200"
      height="800"
      style="max-width:min(1200px,100%)"
    />
  </picture>
</figure>
```

The second example produces a `<figcaption>Company Logo</figcaption>` inside the figure.

`entry.render()` sets the source path automatically and keeps resolution inside the collection directory. For `convert()` or `layer.convert()`, pass `sourcePath` when you want the same behavior outside collections; by default relative refs stay inside that markdown file's directory, and you can pass `assetRoot` when the safe root should be broader (for example the collection directory).

### Automatic Light/Dark Pair Merging

Consecutive images whose filenames end with `-light` and `-dark` suffixes (e.g. `diagram-light.svg` and `diagram-dark.svg`) are automatically merged into a single `<figure class="ps-figure ps-figure-themed">`. The merged image inherits intrinsic dimensions from the light variant. When using `-light`/`-dark` suffixes, **both variants must be present** as consecutive images — a lone `-light` or `-dark` image without its counterpart will throw an error.

The generated `<picture>` element is format-aware:

- **SVG pairs** use `<source type="image/svg+xml">` — no AVIF/WebP conversion is attempted since SVGs are already resolution-independent vectors.
- **Raster pairs** use AVIF + WebP `<source>` variants, with generated format conversion files placed in the output directory.

```md
![Architecture overview](./diagrams/arch-light.svg "Build pipeline architecture")
![Architecture overview](./diagrams/arch-dark.svg)
```

Produces (for SVG pairs):

```html
<figure class="ps-figure ps-figure-themed">
  <picture>
    <source
      srcset="./diagrams/arch-dark.svg"
      type="image/svg+xml"
      media="(prefers-color-scheme: dark)"
    />
    <source srcset="./diagrams/arch-light.svg" type="image/svg+xml" />
    <img
      src="./diagrams/arch-light.svg"
      alt="Architecture overview"
      width="879"
      height="771"
      style="max-width:min(879px,100%)"
    />
  </picture>
  <figcaption>Build pipeline architecture</figcaption>
</figure>
```

The title on the first (light) image becomes the `<figcaption>`. In auto mode, the browser natively evaluates the `<source media>` queries — zero JavaScript needed.

### Invert on dark

Images containing `.invert.` in their filename (e.g. `flow.invert.svg`) automatically receive the `invert-on-dark` class from the pipeline. This applies `invert(1) hue-rotate(180deg)` in dark mode via CSS. Best suited for simple black-and-white diagrams or icons.

```md
![Linear flow from input through validation to output](./simple-flow.invert.svg "Processing pipeline")
```

## Theme-Aware Images

When `@pagesmith/site` CSS is loaded, content images and other elements can respond to the active color scheme. The `<html>` element always carries one of `color-scheme-auto`, `color-scheme-light`, or `color-scheme-dark` (default: `color-scheme-auto`).

### Image best practices

Use standard markdown image syntax for all content images. The pipeline automatically wraps them in `<figure class="ps-figure">` and generates `<picture>` elements for raster images. Use the markdown title attribute for captions:

```md
![Dashboard showing real-time metrics](./hero.jpg "Production monitoring dashboard")
```

For light/dark pairs, place the light and dark variants consecutively:

```md
![Architecture overview](./diagrams/arch-light.svg "Build pipeline architecture")
![Architecture overview](./diagrams/arch-dark.svg)
```

### CSS classes

| Class               | Purpose                                                                  |
| ------------------- | ------------------------------------------------------------------------ |
| `.ps-figure`        | Wrapper class on all pipeline-generated `<figure>` elements              |
| `.ps-figure-themed` | Added when a light/dark pair is auto-merged                              |
| `.invert-on-dark`   | Invert image colors in dark mode (auto-applied for `.invert.` filenames) |
| `.only-light`       | Show element only in light mode (manual HTML)                            |
| `.only-dark`        | Show element only in dark mode (manual HTML)                             |
| `.show-on-light`    | Show any element only in light mode                                      |
| `.show-on-dark`     | Show any element only in dark mode                                       |

### Generic show/hide helpers

For non-image elements that should toggle with the color scheme, use the generic helpers:

```html
<div class="show-on-light">Light-mode only content</div>
<div class="show-on-dark">Dark-mode only content</div>
```

## Heading Links (rehype-slug + rehype-autolink-headings)

All headings automatically receive:

1. A URL-safe `id` attribute generated by `rehype-slug`
2. The heading text wrapped in an anchor link (behavior: `wrap`) by `rehype-autolink-headings`

Slug generation algorithm:

- Convert to lowercase
- Replace spaces with hyphens
- Strip special characters (punctuation, symbols)
- Collapse multiple hyphens

Examples:

| Heading                 | Generated slug     |
| ----------------------- | ------------------ |
| `## Getting Started`    | `getting-started`  |
| `## What's New in v2?`  | `whats-new-in-v2`  |
| `## API Reference (v3)` | `api-reference-v3` |
| `## CSS & JavaScript`   | `css--javascript`  |

Rendered HTML:

```html
<h2 id="getting-started"><a href="#getting-started">Getting Started</a></h2>
```

## Built-in Code Renderer Features

Syntax highlighting is handled by the built-in Pagesmith renderer on top of Shiki with dual themes. Shared code block chrome ships in the CSS bundles, while syntax token colors and copy/collapse behavior are injected inline per rendered document.

### Dual Themes

Automatic light/dark switching via `prefers-color-scheme`. Defaults: `github-light` / `github-dark`.

Configure:

```ts
markdown: {
  shiki: {
    themes: { light: 'github-light', dark: 'github-dark' },
  },
}
```

### Code Block Meta Syntax

All features are enabled via meta strings after the language identifier:

| Meta                | Example                                   | Description                                      |
| ------------------- | ----------------------------------------- | ------------------------------------------------ |
| `title="..."`       | ````js title="app.js"`                    | File title above the code block                  |
| `showLineNumbers`   | ````js showLineNumbers`                   | Show line numbers                                |
| `startLineNumber=N` | ````js showLineNumbers startLineNumber=5` | Start line numbering at N                        |
| `mark={lines}`      | ````js mark={3,5-7}`                      | Highlight lines                                  |
| `ins={lines}`       | ````js ins={4}`                           | Mark lines as inserted (green)                   |
| `del={lines}`       | ````js del={5}`                           | Mark lines as deleted (red)                      |
| `collapse={lines}`  | ````js collapse={1-5}`                    | Collapse lines by default                        |
| `wrap`              | ````js wrap`                              | Enable text wrapping                             |
| `frame="..."`       | ````js frame="none"`                      | Frame style: `none`, `code`, `terminal`, `lines` |

### Combined Example

````md
```ts title="server.ts" showLineNumbers mark={3} ins={7-8} collapse={1-2}
import express from "express";
import cors from "cors";
const app = express(); // highlighted
app.use(cors());

// New routes added
app.get("/api", handler);
app.post("/api", handler);
```
````

````

### Automatic Features (no meta needed)

- **Copy button** -- on every code block, progressively enhanced by the shared Pagesmith content runtime
- **Language badge** -- automatic language indicator
- **Syntax highlighting** -- dual theme support

### Language Aliases

Configure custom language aliases:

```ts
markdown: {
  shiki: {
    langAlias: { 'my-lang': 'typescript' },
  },
}
````

### Global Line Numbers

Enable line numbers on all code blocks:

```ts
markdown: {
  shiki: {
    defaultShowLineNumbers: true,
  },
}
```

## Custom Plugins

Extend the pipeline:

```ts
markdown: {
  remarkPlugins: [myRemarkPlugin, [pluginWithOptions, { option: true }]],
  rehypePlugins: [myRehypePlugin],
}
```

User remark plugins run after the built-in remark plugins (GFM, math, frontmatter, alerts, smartypants) but before `remark-rehype`. User rehype plugins run after heading extraction but before `rehype-stringify`.

Raw HTML is preserved by default (`allowDangerousHtml: true`). Disable it when rendering untrusted markdown. Math processing defaults to `math: 'auto'`, which enables `remark-math` and `rehype-mathjax` only for pages that contain math markers.

## Frontmatter -- @pagesmith/core

Core provides base schemas. Use them or define your own with Zod:

| Schema                     | Fields                                                        |
| -------------------------- | ------------------------------------------------------------- |
| `BaseFrontmatterSchema`    | title, description, publishedDate, lastUpdatedOn, tags, draft |
| `BlogFrontmatterSchema`    | extends base + category, featured, coverImage                 |
| `ProjectFrontmatterSchema` | extends base + gitRepo, links                                 |

## Frontmatter -- @pagesmith/docs (additional)

Docs pages support these additional frontmatter fields beyond what your schema defines:

| Field          | Type      | Description                        |
| -------------- | --------- | ---------------------------------- |
| `title`        | `string`  | Page title (sidebar + browser tab) |
| `description`  | `string`  | Meta description for SEO           |
| `navLabel`     | `string`  | Override top navigation label      |
| `sidebarLabel` | `string`  | Override sidebar label             |
| `order`        | `number`  | Manual sort order within section   |
| `draft`        | `boolean` | Exclude from build                 |

### Home Page Frontmatter (docs only)

| Field         | Type     | Description                                        |
| ------------- | -------- | -------------------------------------------------- |
| `layout`      | `string` | `DocHome` for the home layout                      |
| `tagline`     | `string` | Short description below title                      |
| `install`     | `string` | Install command snippet                            |
| `actions`     | `array`  | CTA buttons (`{ text, link, theme: 'brand'         |
| `features`    | `array`  | Feature cards (`{ icon, title, details }`)         |
| `packages`    | `array`  | Package cards (`{ name, description, href, tag }`) |
| `codeExample` | `object` | Code example (`{ label, title, code }`)            |

## Built-in Content Validators

For markdown collections, three validators run automatically:

- **linkValidator** -- warns on bare URLs, empty link text, suspicious protocols
- **headingValidator** -- enforces single h1, sequential heading depth
- **codeBlockValidator** -- warns on missing language, unknown meta properties

Known valid meta properties: `title`, `showLineNumbers`, `startLineNumber`, `wrap`, `frame`, `collapse`, `mark`, `ins`, `del`.

## Key Rules for Content Authors

- Use fenced code blocks with a language identifier (validator warns otherwise)
- Do NOT add manual copy-button JS -- the built-in renderer handles it
- Do include the shipped Pagesmith markdown CSS so code block chrome and tabs render correctly
- One `# h1` per page (validator enforces)
- Sequential heading depth (no skipping from h2 to h4)
- Prefer relative links for internal content; absolute URLs get external link treatment

## Quick Reference Card

| Feature          | Syntax                                                                        | Plugin                                 |
| ---------------- | ----------------------------------------------------------------------------- | -------------------------------------- | --- | ------ | --- | --- | ----------- | ---------- |
| Bold             | `**bold`\*\*                                                                  | built-in                               |
| Italic           | `*italic*`                                                                    | built-in                               |
| Inline code      | `code`                                                                        | built-in                               |
| Link             | `[text](url)`                                                                 | built-in                               |
| Image            | `![alt](src "title")` — auto figure+picture wrapping                          | rehype-local-images                    |
| Light/dark pair  | consecutive `-light`/`-dark` images auto-merged                               | rehype-local-images                    |
| Blockquote       | `> quote`                                                                     | built-in                               |
| Ordered list     | `1. item`                                                                     | built-in                               |
| Unordered list   | `- item`                                                                      | built-in                               |
| Horizontal rule  | `---`                                                                         | built-in                               |
| Table            | `                                                                             | col                                    | col | `with` | --- | --- | ` separator | remark-gfm |
| Strikethrough    | `~~text~~`                                                                    | remark-gfm                             |
| Task list        | `- [x] done` / `- [ ] todo`                                                   | remark-gfm                             |
| Autolink         | bare URL                                                                      | remark-gfm                             |
| Footnote         | `[^id]` + `[^id]: text`                                                       | remark-gfm                             |
| Inline math      | `$E = mc^2$`                                                                  | remark-math                            |
| Block math       | `$$...$$`                                                                     | remark-math                            |
| Alert            | `> [!NOTE]` / `> [!TIP]` / `> [!IMPORTANT]` / `> [!WARNING]` / `> [!CAUTION]` | remark-github-alerts                   |
| Smart quotes     | `"text"` becomes curly                                                        | remark-smartypants                     |
| Em dash          | `---`                                                                         | remark-smartypants                     |
| En dash          | `--`                                                                          | remark-smartypants                     |
| Ellipsis         | `...`                                                                         | remark-smartypants                     |
| Code title       | ````js title="file.js"`                                                       | applyPagesmithCodeRenderer             |
| Line numbers     | ````js showLineNumbers`                                                       | applyPagesmithCodeRenderer             |
| Line highlight   | ````js mark={1-3}`                                                            | applyPagesmithCodeRenderer             |
| Line insert      | ````js ins={4}`                                                               | applyPagesmithCodeRenderer             |
| Line delete      | ````js del={5}`                                                               | applyPagesmithCodeRenderer             |
| Collapse lines   | ````js collapse={1-5}`                                                        | applyPagesmithCodeRenderer             |
| Word wrap        | ````js wrap`                                                                  | applyPagesmithCodeRenderer             |
| Frame style      | ````js frame="terminal"`                                                      | applyPagesmithCodeRenderer             |
| External link    | `[text](https://...)` auto new-tab                                            | rehype-external-links                  |
| Heading anchor   | auto `id` + wrap link                                                         | rehype-slug + rehype-autolink-headings |
| Accessible emoji | Unicode emoji auto-wrapped                                                    | rehype-accessible-emojis               |
