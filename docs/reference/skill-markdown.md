---
title: 'markdown'
description: 'Author and validate Pagesmith-flavored markdown — GitHub Flavored Markdown (tables, task lists, strikethrough, autolinks, footnotes), GitHub-style alerts (NOTE/TIP/IMPORTANT/WARNING/CAUTION), inline and display math via remark-math + rehype-mathjax, smart typography, accessible emojis, themed light/dark image pairs, the Pagesmith code-block renderer (titles, line numbers, mark/ins/del, collapse, wrap, frame, language aliases, dual Shiki themes), and the auto-grouping code-tabs pattern. Self-contained and pinned to @pagesmith/core@0.9.9; the bundled script auto-installs the package globally (with permission) and runs `pagesmith-core validate` against your content. Use when writing or auditing markdown that targets Pagesmith / @pagesmith/docs sites, or when you want to know which features the built-in pipeline ships.'
skill_name: markdown
category: standalone
---
# Markdown for Pagesmith (self-contained, pinned to @pagesmith/core@0.9.9)

This skill ships **all** of the Pagesmith markdown feature reference, the
unified pipeline order, and the syntax for every built-in remark / rehype
stage. It depends on `@pagesmith/core` **only** to run `pagesmith-core
validate` against your markdown — the authoring rules below are version-pinned
and live in this skill's `references/` folder.

## When to use

- Authoring `.md` files that will be rendered by `@pagesmith/core` or
  `@pagesmith/docs` (alerts, code tabs, math, themed images, etc.).
- Auditing existing markdown for invalid frontmatter, broken local links,
  missing image dimensions, or unsupported code-fence metadata.
- Picking the right markdown idiom for an effect (e.g. "do I use `<picture>`
  or the auto-merged `-light`/`-dark` image pair?").
- Verifying that a feature is built-in versus requires a custom remark /
  rehype plugin.

## Install @pagesmith/core (global, pinned to v0.9.9)

This skill expects the `pagesmith-core` CLI to be available **globally** on
`PATH`. The bundled helper installs it on demand:

```bash
# Validate every markdown file under content/.
# Auto-installs @pagesmith/core globally (with a y/N prompt) if missing.
./scripts/validate-markdown.sh content/

# A single file:
./scripts/validate-markdown.sh content/posts/hello.md

# Non-interactive (CI):
AUTO_YES=1 ./scripts/validate-markdown.sh content/
```

What the script does, in order:

1. Verifies `pagesmith-core` is on `PATH`. If missing, prompts for permission and runs:
   ```bash
   npm install -g @pagesmith/core@0.9.9
   ```
   Decline (or set `AUTO_YES=0` and use a non-TTY shell) to abort.
2. Runs `pagesmith-core validate <target> --json`. Validation covers
   frontmatter (Zod schemas), relative link targets, and image references.
3. Exits non-zero when any file fails validation.

When the agent invokes the CLI directly, use the plain global command — never
`npx pagesmith-core`, since this skill assumes a global install:

```bash
pagesmith-core --version
pagesmith-core validate content/ --json
pagesmith-core templates           # list starter templates
pagesmith-core ai install          # install Pagesmith AI memory artifacts
```

> The version-pinned authoring rules below are in this folder's `references/`
> — they are the **source of truth** for this skill. Do not read
> `node_modules/@pagesmith/core/REFERENCE.md` (this skill ships its own copy
> of the full markdown reference for v0.9.9).

## Feature surface (built-in by default)

| Feature                  | Plugin / stage                            | Where to read more                |
| ------------------------ | ----------------------------------------- | --------------------------------- |
| Tables, strikethrough, task lists, autolinks, footnotes | `remark-gfm`                | [GFM extensions](#gfm-extensions) |
| GitHub-style alerts      | `remark-github-alerts`                    | [Alerts & callouts](#alerts--callouts) |
| Smart typography         | `remark-smartypants`                      | [Typography](#typography)         |
| Inline + display math    | `remark-math`, `rehype-mathjax`           | [Math](#math)                     |
| Code blocks (Shiki)      | Pagesmith code renderer + Shiki           | [Code blocks](#code-blocks)       |
| Code tabs                | `rehype-code-tabs` (auto-group on `title=`) | [Code tabs](#code-tabs)         |
| Scrollable tables        | `rehype-scrollable-tables`                | wraps every table                 |
| Heading slugs + anchors  | `rehype-slug`, `rehype-autolink-headings` | [Heading anchors](#heading-anchors) |
| External link safety     | `rehype-external-links`                   | every `http(s)://` gets `target="_blank" rel="noopener noreferrer"` |
| Accessible emojis        | `rehype-accessible-emojis`                | wraps every emoji in `<span role="img" aria-label="...">` |
| Local image enhancement  | `rehype-local-images`                     | [Images](#images)                 |
| Themed light/dark pairs  | `rehype-local-images` (auto-merge)        | [Themed images](#themed-images)   |

The full pipeline order with every stage, including where custom remark /
rehype plugins slot in, is in
[`references/pipeline-and-config.md`](references/pipeline-and-config.md).

## Pipeline order

```text
remark-parse              Parse markdown to MDAST
remark-gfm                Tables, strikethrough, task lists, autolinks, footnotes
remark-frontmatter        Strip YAML frontmatter from AST
remark-github-alerts      > [!NOTE], > [!TIP], etc.
remark-smartypants        Smart quotes, en/em dashes, ellipses
remark-math               $...$ / $$...$$ when math: true or 'auto' detects markers
[user remark plugins]     From MarkdownConfig.remarkPlugins
lang-alias transform      Map fenced-code language tags via shiki.langAlias
remark-rehype             Markdown AST → HTML AST
rehype-mathjax            Render math to SVG (before code renderer)
applyPagesmithCodeRenderer Syntax highlighting, code frames, copy button
rehype-code-tabs          Group consecutive titled blocks into tabs
rehype-scrollable-tables  Wrap markdown tables for horizontal scrolling
rehype-slug               Add id="" to headings
rehype-autolink-headings  Wrap heading text in anchor links
rehype-external-links     target="_blank" on external URLs
rehype-accessible-emojis  aria-label on emoji characters
rehype-local-images       Figure wrapping, picture/avif/webp, light/dark merge
heading extraction        Collect headings for TOC data
[user rehype plugins]     From MarkdownConfig.rehypePlugins
rehype-stringify          HTML AST → HTML string
```

User plugins run **after** the built-in defaults at their respective tiers,
which means custom remark plugins can rely on GFM tables, alerts, and math
already being parsed; custom rehype plugins can rely on slugs, code rendering,
and image enhancement already applied.

## GFM extensions

### Tables

```md
| Feature       | Syntax        |
| ------------- | ------------- |
| Bold          | `**bold**`    |
| Italic        | `*italic*`    |
| Strikethrough | `~~deleted~~` |
```

Alignment is controlled by colons in the separator row:

```md
| Left | Center | Right |
| :--- | :----: | ----: |
| text |  text  |  text |
```

Every rendered table is wrapped in a horizontally scrollable container
(`rehype-scrollable-tables`), so wide tables don't break the layout.

### Strikethrough

```md
~~removed text~~
```

### Task lists

```md
- [x] Completed task
- [ ] Pending task
```

### Autolinks

Bare URLs are converted to clickable links automatically:

```md
Visit https://example.com for details.
```

### Footnotes

```md
This claim needs a source[^1].

[^1]: The source for this claim.
```

The footnote content renders at the bottom of the page with a back-link.

## Alerts & callouts

Five alert types use blockquote syntax (matching GitHub's renderer):

```md
> [!NOTE]
> Useful information the reader should know.

> [!TIP]
> Helpful advice for doing things better.

> [!IMPORTANT]
> Key information the reader must not miss.

> [!WARNING]
> Something that needs immediate attention.

> [!CAUTION]
> Negative potential consequences of an action.
```

| Type           | Color  | Use for                                |
| -------------- | ------ | -------------------------------------- |
| `[!NOTE]`      | Blue   | General supplementary information      |
| `[!TIP]`       | Green  | Helpful suggestions and best practices |
| `[!IMPORTANT]` | Purple | Key details the reader must know       |
| `[!WARNING]`   | Yellow | Things to watch out for                |
| `[!CAUTION]`   | Red    | Dangerous actions or breaking changes  |

Alerts may contain multiple paragraphs, lists, fenced code blocks, and
inline formatting.

## Math

Math parsing is opt-in. The `markdown.math` field accepts:

| Value             | Effect                                                   |
| ----------------- | -------------------------------------------------------- |
| `false` (default in some bare integrations) | No math; `$…$` passes through as text. |
| `true`            | Always enabled; KaTeX assets ship on every page.         |
| `'auto'` (default for stock docs) | Enabled per-page only when `$…$` or `$$…$$` is detected. |

Default rendering engine is **MathJax** (`rehype-mathjax`), which produces
SSR-ready SVG so math is visible without client-side JS. Switch to KaTeX with
`mathEngine: 'katex'` if you need KaTeX-specific features.

### Inline math

```md
The equation $E = mc^2$ changed physics.
```

### Display math

```md
$$
\int_0^\infty e^{-x^2}\, dx = \frac{\sqrt{\pi}}{2}
$$
```

## Typography

ASCII punctuation upgrades automatically (`remark-smartypants`). Code blocks
and inline code are never affected.

| Input     | Output  | Description         |
| --------- | ------- | ------------------- |
| `"hello"` | "hello" | Curly double quotes |
| `'hello'` | ‘hello’ | Curly single quotes |
| `--`      | –       | En dash             |
| `---`     | —       | Em dash             |
| `...`     | …       | Ellipsis            |

## External links

Any link with an absolute URL (starts with `http://` or `https://`) gets
`target="_blank"` and `rel="noopener noreferrer"` automatically. Internal
links and anchor links are left alone.

```md
[GitHub repo](https://github.com/sujeet-pro/pagesmith) <!-- new tab, noopener -->
[Getting Started](../getting-started/README.md)         <!-- same tab -->
[Anchor](#math)                                          <!-- same tab -->
```

## Accessible emojis

Emoji characters are wrapped in `<span role="img" aria-label="...">` so
screen readers announce the emoji name.

```md
Build complete! 🎉
```

Renders as:

```html
Build complete! <span role="img" aria-label="party popper">🎉</span>
```

## Heading anchors

Every heading receives a URL-safe `id` (via `rehype-slug`) and the heading
text is wrapped in an anchor (via `rehype-autolink-headings`).

```md
## My Section
```

Renders as:

```html
<h2 id="my-section"><a href="#my-section">My Section</a></h2>
```

Stable ids power the table-of-contents sidebar and enable deep-linking.

## Images

All markdown images are wrapped in a `<figure class="ps-figure
ps-figure-zoomable">` and given a hidden expand button
(`<button class="ps-img-zoom-btn" hidden data-ps-img-zoom-btn>`). Raster images
(PNG, JPEG, WebP, GIF) get a `<picture>` element with WebP and AVIF `<source>`
variants — Pagesmith generates these alongside the source at build time.

The title attribute becomes the `<figcaption>`:

```md
![Dashboard metrics](./hero.png "Production monitoring dashboard")
```

Renders as:

```html
<figure class="ps-figure ps-figure-zoomable">
  <picture>
    <source srcset="./hero.avif" type="image/avif" />
    <source srcset="./hero.webp" type="image/webp" />
    <img
      src="./hero.webp"
      alt="Dashboard metrics"
      width="..."
      height="..."
      data-zoom-src="./hero.zoom.webp"
      data-zoom-type="image/webp"
    />
  </picture>
  <figcaption>Production monitoring dashboard</figcaption>
  <button type="button" class="ps-img-zoom-btn" hidden data-ps-img-zoom-btn>...</button>
</figure>
```

For every convertible raster source Pagesmith emits **three** files:

- `<stem>.avif` and `<stem>.webp` — display variants capped at 1600 px wide.
- `<stem>.zoom.webp` — high-resolution zoom variant capped at 4800 px wide.

SVGs are passed through unchanged but still figure-wrapped.

### Themed images

Two patterns ship out of the box:

**1. Auto-merged `-light` / `-dark` pairs.** Place the variants consecutively
with identical alt text. Pagesmith merges them into a single themed figure
with `<source media="(prefers-color-scheme: dark)">`:

```md
![Architecture overview](./diagrams/arch-light.svg "Build pipeline architecture")
![Architecture overview](./diagrams/arch-dark.svg)
```

The title on the **first (light)** image becomes the `<figcaption>`.

**2. `.invert.` filename suffix.** Images whose filename contains `.invert.`
get the `invert-on-dark` class so they apply `invert(1) hue-rotate(180deg)`
in dark mode (handy for hand-drawn diagrams that don't have a dark variant):

```md
![Request lifecycle](./simple-diagram.invert.svg "Request lifecycle")
```

There are also generic show/hide helpers for any HTML element:

```html
<span class="show-on-light">Light content</span>
<span class="show-on-dark">Dark content</span>
```

## Code blocks

Code blocks use the built-in Pagesmith renderer on top of Shiki — syntax
highlighting, **dual themes** (light + dark via CSS variables), titles, line
numbers, copy/collapse controls, and shared chrome.

### Basic highlighting

````md
```ts
const greeting = "Hello, world!";
```
````

Over 100 languages are supported via Shiki.

### File titles

````md
```ts title="vite.config.ts"
import { defineConfig } from "vite";
export default defineConfig({});
```
````

The title also doubles as the **tab label** when blocks auto-group (see
[Code tabs](#code-tabs) below).

### Line numbers

Line numbers are shown by default. Override per block:

````md
```bash showLineNumbers=false
npm install @pagesmith/core
```

```ts startLineNumber=42
export function resolve() { /* ... */ }
```
````

Site-wide default lives in `markdown.shiki.defaultShowLineNumbers`.

### Line highlighting

Mark, insert, or delete lines:

````md
```ts mark={2-3}
const name = "Pagesmith";
const version = "0.9.9";
const highlighted = true;
```

```ts ins={2} del={1}
const old = "before";
const updated = "after";
```
````

Range syntax: `mark={1, 3-5, 8}`.

### Diff blocks

````md
```diff
- const port = 3000
+ const port = process.env.PORT || 3000
```
````

### Collapsible sections

Hide boilerplate that readers expand on click:

````md
```ts collapse={1-5}
import { defineConfig } from "vite";
import { pagesmithContent, pagesmithSsg } from "@pagesmith/site/vite";
import collections from "./content.config";
import path from "node:path";
export default defineConfig({
  plugins: [pagesmithContent(collections), pagesmithSsg()],
});
```
````

### Word wrapping

Enable wrapping for long lines:

````md
```json wrap
{
  "name": "@pagesmith/core",
  "description": "A very long description that would otherwise overflow horizontally",
  "version": "0.9.9"
}
```
````

### Frame styles

Terminal-style languages (`bash`, `sh`, `zsh`, `shell`, `powershell`) auto-pick a
terminal frame; everything else picks the editor frame. Override explicitly:

````md
```bash frame="none"
npm install @pagesmith/core
```
````

Allowed values: `"code"` (editor), `"terminal"`, `"plain"` (alias `"none"`).

### Meta string quick reference

All properties go after the language identifier in the opening fence, in any order:

| Property          | Syntax                       | Description                       |
| ----------------- | ---------------------------- | --------------------------------- |
| `title`           | `title="file.ts"`            | Filename or label above the block |
| `showLineNumbers` | `showLineNumbers=false`      | Show or hide line numbers         |
| `startLineNumber` | `startLineNumber=42`         | Start numbering from a given line |
| `mark`            | `mark={3}` or `mark={1,3-5}` | Highlight lines (neutral)         |
| `ins`             | `ins={2-3}`                  | Mark lines as inserted (green)    |
| `del`             | `del={1}`                    | Mark lines as deleted (red)       |
| `collapse`        | `collapse={1-5}`             | Collapse a range of lines         |
| `wrap`            | `wrap`                       | Enable word wrapping              |
| `frame`           | `frame="terminal"`           | Override the frame style          |

Combine freely:

````md
```ts title="example.ts" mark={3} ins={5} collapse={1-2}
import { z } from "zod";
import { defineCollection } from "@pagesmith/core";
const posts = defineCollection({
  loader: "markdown",
  directory: "content/posts",
  schema: z.object({ title: z.string() }),
});
```
````

## Code tabs

Consecutive titled code blocks are **auto-grouped** into a tabbed interface
by `rehype-code-tabs`. Write titled fenced blocks one after another with no
other content between them:

````md
```bash title="npm"
npm install @pagesmith/core
```

```bash title="pnpm"
pnpm add @pagesmith/core
```

```bash title="yarn"
yarn add @pagesmith/core
```

```bash title="bun"
bun add @pagesmith/core
```
````

Rules:

- Every block in the group must have a `title=` — an untitled block breaks the group.
- Any non-code content between titled blocks (paragraph, heading, list, blank-line
  rule) breaks the group.
- Each group is independent; a page can contain many tab groups.
- Without JavaScript, all blocks stack vertically as a no-JS fallback.

## Language aliases

Some languages are aliased to a supported Shiki grammar so the highlighter
doesn't warn on unknown languages:

| Alias        | Highlighted as |
| ------------ | -------------- |
| `dot`        | `text`         |
| `mermaid`    | `text`         |
| `plantuml`   | `text`         |
| `excalidraw` | `json`         |
| `drawio`     | `xml`          |
| `proto`      | `protobuf`     |
| `ejs`        | `html`         |
| `hbs`        | `handlebars`   |

Add custom aliases via `markdown.shiki.langAlias` (user aliases override
defaults):

```ts
markdown: {
  shiki: {
    langAlias: {
      vue: 'html',
      astro: 'html',
      myLang: 'typescript',
    },
  },
}
```

## Dual Shiki themes

Code blocks support light and dark themes simultaneously. The default pair is
`github-light` / `github-dark`. A `prefers-color-scheme` media query (and the
site's `[data-theme]` toggle) switches between them.

```ts
markdown: {
  shiki: {
    themes: {
      light: 'catppuccin-latte',
      dark: 'catppuccin-mocha',
    },
  },
}
```

Pagesmith maps themes to `.color-scheme-light` / `.color-scheme-dark` on
`<html>`, so theme switching integrates with the site-wide color scheme
toggle.

## Custom plugins

Extend the pipeline with your own remark or rehype plugins via `defineConfig`
(only available when you wire markdown through `@pagesmith/core` directly —
stock `@pagesmith/docs` keeps `pagesmith.config.json5` JSON-safe and does not
execute function-valued plugins):

```ts
import { defineConfig } from "@pagesmith/core";
import remarkToc from "remark-toc";
import rehypeFigure from "rehype-figure";
import rehypeMermaid from "rehype-mermaid";

export default defineConfig({
  collections,
  markdown: {
    remarkPlugins: [remarkToc],
    rehypePlugins: [
      rehypeMermaid,
      [rehypeFigure, { className: "figure" }],
    ],
    math: "auto",
    shiki: {
      themes: { light: "github-light", dark: "one-dark-pro" },
      langAlias: { vue: "html" },
      defaultShowLineNumbers: true,
    },
  },
});
```

Tuple form `[plugin, options]` is supported for both arrays. Custom remark
plugins run after the built-in remark plugins but before `remark-rehype`;
custom rehype plugins run after the built-in rehype plugins (after heading
extraction) but before `rehype-stringify`.

## Validation

`pagesmith-core validate` checks:

- **Frontmatter** — Zod schemas declared in `defineCollection({ schema: ... })`
  catch missing fields, invalid enums, malformed dates, etc.
- **Relative links** — every `[text](./other.md)` and `[text](../path/README.md)`
  must resolve to a real file.
- **Image references** — `![alt](./image.png)` paths must exist and (for raster
  formats) Pagesmith reports the resolved intrinsic dimensions.

```bash
pagesmith-core validate content/                # validate every collection
pagesmith-core validate content/posts/hello.md  # single file
pagesmith-core validate content/ --json         # machine-readable
pagesmith-core validate content/ --strict       # warnings become errors
```

`PAGESMITH_NON_INTERACTIVE=1` and `CI=1` both force non-interactive output;
`--yes` skips interactive prompts.

## Authoring rules

Apply these whenever you write or audit a Pagesmith markdown file:

1. **Use markdown image syntax**, not raw `<img>` / `<picture>` HTML — the
   pipeline can only auto-add picture elements, intrinsic dimensions, themed
   variants, and zoom buttons when it owns the AST node.
2. **Pair light/dark images consecutively** with identical alt text. Put the
   title (caption) on the **light** image only.
3. **Set `markdown.math: 'auto'` for mixed content** so KaTeX/MathJax assets
   only ship when a page actually uses math.
4. **Always quote alert keywords**: `> [!NOTE]`, not `> [NOTE]`.
5. **Don't put non-code content between titled fenced blocks** when you want
   them grouped into a tab group — even a blank-line-only blockquote breaks
   the group.
6. **Prefer the `.invert.` filename for hand-drawn diagrams** without a
   dedicated dark variant. For everything else, generate `-light` / `-dark`
   variants (e.g. via `diagram-mermaid`, `diagram-graphviz`,
   `diagram-excalidraw`, or `diagram-drawio` skills).
7. **Headings auto-link.** Don't manually wrap heading text in `<a>` tags.
8. **External links are auto-`target="_blank"`** — don't repeat that attribute
   in the source.
9. **`langAlias` lives in `markdown.shiki`**, not in the markdown source.
   Add an alias once instead of changing the language tag everywhere.
10. **Keep the `MarkdownConfig` object reference stable** when wiring through
    `@pagesmith/core` directly. The processor is cached per-`MarkdownConfig`
    object identity; rebuilding the object on every render busts the cache.

## Anti-patterns

- ❌ Re-importing `unified` directly. `@pagesmith/core` owns the processor
  lifecycle and caches per-`MarkdownConfig` identity.
- ❌ Hardcoding `<img>` for themed image swaps. Use the auto-merged pair.
- ❌ Setting `math: true` "just in case" — that ships KaTeX assets on every
  page (~75 KB).
- ❌ Adding language aliases by changing fences (` ```vue ` → ` ```html `).
  Configure `markdown.shiki.langAlias` instead.
- ❌ Using CommonJS-only remark / rehype plugins — they may crash the
  pipeline. Prefer ESM-first plugins.
- ❌ Reading from disk inside a custom remark / rehype plugin. Stage the data
  in advance.

## References

- [`references/markdown-reference.md`](references/markdown-reference.md) —
  full feature-by-feature reference (every syntax form, output HTML, and
  configuration knob), version-pinned to `@pagesmith/core@0.9.9`.
- [`references/pipeline-and-config.md`](references/pipeline-and-config.md) —
  unified pipeline order, every built-in stage, where custom plugins slot
  in, and the `MarkdownConfig` shape.
- [`references/usage.md`](references/usage.md) — `pagesmith-core` CLI quick
  reference (templates, create, ai install, skills install, validate).

## Related skills

- [`diagram-mermaid`](../diagram-mermaid/SKILL.md) — produce SVGs that
  embed cleanly in Pagesmith markdown via auto-merged `-light` / `-dark`
  image pairs.
- [`diagram-graphviz`](../diagram-graphviz/SKILL.md) — same, for DOT graphs.
- [`diagram-excalidraw`](../diagram-excalidraw/SKILL.md) — same, for
  hand-drawn diagrams.
- [`diagram-drawio`](../diagram-drawio/SKILL.md) — same, for cloud /
  infrastructure diagrams.
- [`diagram-review`](../diagram-review/SKILL.md) — pre-merge audit for any
  embedded diagrams.
