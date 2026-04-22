# pagesmith-core CLI — quick reference

This skill is pinned to `@pagesmith/core@0.9.9`. Install globally once
(`npm install -g @pagesmith/core@0.9.9`) — the bundled
`scripts/validate-markdown.sh` does this automatically with permission.

## Commands

```bash
pagesmith-core --version
pagesmith-core --help
pagesmith-core <command> --help
```

| Command                            | What it does                                                                |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `pagesmith-core templates`         | List available starter templates (blog, doc-site, framework integrations).  |
| `pagesmith-core create [name]`     | Scaffold a starter project from one of the templates.                       |
| `pagesmith-core ai install`        | Install Pagesmith AI memory artifacts (AGENTS.md / CLAUDE.md / skill pack). |
| `pagesmith-core skills install`    | Install consumer skills shipped from Pagesmith packages.                    |
| `pagesmith-core validate [dir]`    | Validate markdown content (frontmatter, links, images).                     |

## Validate (the focus of this skill)

```bash
pagesmith-core validate                    # validate ./content (default)
pagesmith-core validate content/           # explicit content directory
pagesmith-core validate content/posts/x.md # single file
pagesmith-core validate content/ --json    # machine-readable output
pagesmith-core validate content/ --strict  # warnings become errors
```

Validation covers:

- **Frontmatter** — Zod schemas declared in `defineCollection({ schema: ... })`
  catch missing fields, invalid enums, malformed dates, etc.
- **Relative links** — every `[text](./other.md)` and
  `[text](../path/README.md)` must resolve to a real file.
- **Image references** — every `![alt](./image.png)` path must exist; for
  raster formats Pagesmith reports the resolved intrinsic dimensions.

`PAGESMITH_NON_INTERACTIVE=1` and `CI=1` both force non-interactive output;
`--yes` skips confirmation prompts. The bundled script sets
`PAGESMITH_NON_INTERACTIVE=1` automatically.

## Where authoring rules live

The full markdown feature reference is bundled inside this skill:

- [`./markdown-reference.md`](./markdown-reference.md) — every syntax form,
  the rendered HTML, and the configuration knob that controls it.
- [`./pipeline-and-config.md`](./pipeline-and-config.md) — unified pipeline
  order, every built-in stage, where custom plugins slot in, and the
  `MarkdownConfig` shape.

Stock `@pagesmith/docs` keeps `pagesmith.config.json5` JSON-safe and does
**not** execute function-valued remark / rehype plugins. Drop down to
`@pagesmith/core`'s `defineConfig({ markdown: { remarkPlugins, rehypePlugins } })`
when you need custom plugin functions or a custom site shell.
