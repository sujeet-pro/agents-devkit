# Pagesmith Markdown Guidelines (fallback)

> Inline fallback for the supported markdown features and authoring rules in `@pagesmith/docs`. When the package is installed, prefer:
> - `node_modules/@pagesmith/docs/skills/pagesmith-docs-setup/references/markdown-guidelines.md`
> - `.pagesmith/markdown-guidelines.md` (written by `pagesmith-docs init --ai`)
> - `node_modules/@pagesmith/docs/REFERENCE.md`

`@pagesmith/docs` inherits the shared markdown pipeline from `@pagesmith/core`, then adds docs-specific link and asset transforms. The `pagesmith.config.json5` markdown field is intentionally JSON-safe; if a syntax or renderer is not documented here, treat it as unsupported unless the project intentionally drops to lower-level `@pagesmith/core` APIs.

## Pipeline order (high level)

```
remark-parse → remark-gfm → remark-frontmatter → remark-github-alerts → remark-smartypants
  → remark-math (when configured)
  → remark-rehype
  → applyPagesmithCodeRenderer (dual themes, line numbers, titles, copy, collapse, mark/ins/del)
  → rehype-code-tabs → rehype-scrollable-tables
  → rehype-slug → rehype-autolink-headings
  → rehype-external-links → rehype-accessible-emojis → rehype-local-images
  → docs link/asset transforms → rehype-stringify
```

## GitHub Flavored Markdown

Tables, strikethrough, task lists, autolinks, footnotes — all enabled.

```md
| Left | Center | Right |
| :--- | :----: | ----: |

~~strikethrough~~

- [x] done
- [ ] todo

Visit https://example.com (autolink).

Content[^1]
[^1]: footnote text.
```

Tables auto-wrap for horizontal scroll on small screens (`rehype-scrollable-tables`).

## GitHub Alerts

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

## Math

Use `$` for inline (`$E = mc^2$`) and `$$` for block math. Rendered to SVG via MathJax. The `$` delimiters must not have spaces immediately inside them.

## Smart typography

ASCII typography is automatically converted (in prose only, not in code blocks):

| Input     | Output | Description    |
| --------- | ------ | -------------- |
| `"hello"` | curly double quotes |
| `'hello'` | curly single quotes |
| `--`      | en dash        |
| `---`     | em dash        |
| `...`     | ellipsis       |

## External links

Absolute URLs starting with `http://` or `https://` automatically get `target="_blank"` and `rel="noopener noreferrer"`. Relative links and anchors stay in the same tab.

## Accessible emojis

Unicode emoji characters are automatically wrapped:

```md
Great job! 🎉
```

renders as `<span role="img" aria-label="party popper">🎉</span>`.

## Local images

Stock `@pagesmith/docs` provides intrinsic dimensions (`width`, `height`, `style="max-width:min({width}px,100%)"`) for relative local images. All raster images render as a `<picture>` element with AVIF + WebP `<source>` variants. SVG images are not wrapped in `<picture>`.

Every markdown image is wrapped in `<figure class="ps-figure">`. The title attribute (`![alt](src "title")`) becomes a `<figcaption>`.

```md
![Hero](./hero.jpg)
![Logo with caption](./logo.png "Company Logo")
```

### Auto light/dark pair merging

Consecutive images whose filenames end with `-light` and `-dark` are merged into a themed `<figure class="ps-figure ps-figure-themed">` with intrinsic dimensions from the light variant:

```md
![Architecture overview](./diagrams/arch-light.svg "Build pipeline architecture")
![Architecture overview](./diagrams/arch-dark.svg)
```

In auto mode the browser natively evaluates `<source media>` queries — zero JavaScript needed. **Both variants must be present** as consecutive images — a lone variant throws an error.

For manual control, the `.only-light` / `.only-dark` CSS classes still work in raw HTML.

## Heading anchors

All headings receive a slug (`id`) and are wrapped in an autolink. Slug rules: lowercase, hyphenate spaces, strip punctuation, collapse multiple hyphens.

| Heading                 | Slug               |
| ----------------------- | ------------------ |
| `## Getting Started`    | `getting-started`  |
| `## What's New in v2?`  | `whats-new-in-v2`  |
| `## API Reference (v3)` | `api-reference-v3` |

## Docs-specific link/asset transforms

- Relative markdown links between pages (e.g. `../getting-started`, `./sub-page`) resolve to root-relative routes under `basePath`, formatted per the `trailingSlash` config (default: slashless).
- Absolute internal links are normalized and prefixed with `basePath`.
- Relative image refs publish under flat content-hashed `/assets/name.hash.ext` paths.
- Markdown images ending in `.inline.svg` inline the SVG into HTML when the file stays inside the current page directory subtree.
- Filename `.invert.` convention (e.g. `simple-flow.invert.svg`) auto-applies `invert(1) hue-rotate(180deg)` in dark mode.

## Code blocks

All features via meta strings after the language identifier:

| Meta                | Example                                   | Effect                                           |
| ------------------- | ----------------------------------------- | ------------------------------------------------ |
| `title="..."`       | `js title="app.js"`                       | File title above the code block                  |
| `showLineNumbers`   | `js showLineNumbers`                      | Show line numbers                                |
| `startLineNumber=N` | `js showLineNumbers startLineNumber=5`    | Start numbering at N                             |
| `mark={lines}`      | `js mark={3,5-7}`                         | Highlight lines                                  |
| `ins={lines}`       | `js ins={4}`                              | Insert (green)                                   |
| `del={lines}`       | `js del={5}`                              | Delete (red)                                     |
| `collapse={lines}`  | `js collapse={1-5}`                       | Collapse by default                              |
| `wrap`              | `js wrap`                                 | Word wrap                                        |
| `frame="..."`       | `js frame="terminal"`                     | Frame style: `none`, `code`, `terminal`, `lines` |

Automatic features (no meta needed): copy button, language badge, dual theme syntax highlighting.

### Code tabs

Consecutive titled code blocks are grouped into tabs automatically:

````md
```ts title="TypeScript"
const greeting: string = "hello"
```

```js title="JavaScript"
const greeting = "hello"
```
````

### Default language aliases

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

## JSON-safe markdown config

```json5
{
  markdown: {
    allowDangerousHtml: true,
    math: "auto",
    shiki: {
      themes: { light: "github-light", dark: "github-dark" },
      langAlias: { shell: "bash" },
      defaultShowLineNumbers: true,
    },
  },
}
```

Function-valued `remarkPlugins` and `rehypePlugins` are **not** supported through `pagesmith.config.json5`. Drop to `@pagesmith/core` for custom plugins.

## Diagram fences are NOT auto-rendered

Stock `@pagesmith/docs` does **not** render `mermaid`, `dot`, `excalidraw`, or `drawio` fences as live diagrams. Those language names are useful for syntax-highlighted source examples only. Published diagrams should be rendered with diagramkit and embedded as image assets.

See `diagramkit-engine-routing.md`.

## Built-in content validators

Three validators run automatically on markdown collections:

- **linkValidator** — warns on bare URLs, empty link text, suspicious protocols.
- **headingValidator** — enforces single h1, sequential heading depth.
- **codeBlockValidator** — warns on missing language, unknown meta properties.

## Key rules for content authors

- Use fenced code blocks **with a language identifier** (validator warns otherwise).
- Do **not** add manual copy-button JS — the built-in renderer handles it.
- One `# h1` per page (validator enforces).
- Sequential heading depth (no skipping h2 → h4).
- Prefer relative links for internal content; absolute URLs get external-link treatment.
- Keep page-local images and diagrams beside the page.
- Raw `mermaid`, `dot`, `excalidraw`, and `drawio` fences are source examples, not rendered diagrams.
