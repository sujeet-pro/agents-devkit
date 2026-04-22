# Anti-patterns

Things this skill must never do, with examples.

## Don't re-implement the upstream tools

```diff
- # bad: hand-rolled SVG render in Node
- import { renderMermaid } from './local-mermaid.mjs'
+ # good: shell out to the local diagramkit CLI
+ exec('npx diagramkit render <page-dir>/diagrams --force --json')
```

`diagramkit` and `pagesmith-docs` are version-pinned in `node_modules/`. Anything we
re-implement will silently drift across upgrades.

## Don't document wished-for behaviour

Every page is grounded in `git ls-files` evidence. If the source says "TODO: support
parallel runs", the doc says the same — it does **not** describe parallel runs as if they
already worked.

```diff
- ## Workflow
- 1. Plan the change
- 2. Run in parallel across all repos      # source has no parallel mode
+ ## Workflow
+ 1. Plan the change
+ 2. Run sequentially against each repo    # matches source
+
+ > [!NOTE]
+ > Parallel execution is tracked in [#123](https://github.com/...) but not yet
+ > implemented.
```

## Don't add diagrams as decoration

Every diagram earns its slot. Use a list, table, or short paragraph first. If the prose
is genuinely unclear (branching flow, dependency graph, architecture overview), add the
diagram per [`diagram-policy.md`](diagram-policy.md).

## Don't hand-edit rendered SVGs

```diff
- # bad: open .diagramkit/foo-light.svg in an editor and tweak the fill
+ # good: edit the source, re-render with --force
+ vim diagrams/foo.mermaid
+ npx diagramkit render diagrams --force
```

## Don't skip the build smoke test

The run does not finish with `--mode auto` until `npx pagesmith-docs build` returns 0.
Skipping the build is the single easiest way to ship docs that don't load.

## Don't skip the WCAG contrast loop

`LOW_CONTRAST_TEXT` warnings from `diagramkit validate` are always-fix. ~8% of male
engineers have red-green colour-vision deficiency; broken contrast is an accessibility
defect, not a stylistic preference.

## Don't merge or split artifacts

One artifact = one page. Don't combine three small skills into one page "for brevity",
and don't split a complex skill across multiple pages "for readability".

The aggregates documented in `inventory-rules.md` (`hooks/hooks.json`, `.mcp.json`,
`monitors/monitors.json`) are deliberate: they have one source file with multiple entries,
so they get one page with one section per entry.

## Don't change `pagesmith.config.json5` silently

Any change to the site config (`basePath`, `editLink`, `theme.layouts`, etc.) must:

1. Be diffed against the previous value.
2. Be surfaced in the report under "Follow-ups".
3. Be left to the user to commit. Never auto-commit config changes.

## Don't fall back to globally installed binaries

```diff
- pagesmith-docs build      # bad: uses whatever is on PATH
+ npx pagesmith-docs build  # good: resolves to ./node_modules/.bin
```

If `node_modules/...` is missing, run `npm install` and re-read the upstream REFERENCE.md
files — never `npm i -g`.

## Don't bypass the drift manifest

The manifest at `.temp/prj-update-docs/state/drift-manifest.json` is the source of truth
for "what was last in sync". Bypassing it (e.g. forcing a full regenerate every run) loses
the manual-edit detection — the only signal that catches a human edit being silently
overwritten.

The right way to force-regenerate is `--mode fix`, which surfaces every overwrite in the
final report.

## Don't skip the link checker

Internal-link breakage is the single most common drift signal users notice in the wild.
The link checker is cheap (single pass over the generated tree); skipping it just defers
the bug to the reader.
