# Research Protocol

`adk-doc-site-setup` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. node_modules/@pagesmith/docs/REFERENCE.md + schemas/.
2. node_modules/diagramkit/REFERENCE.md + llms.txt.
3. Existing docs-like dirs (docs/, documentation/, guide/, content/, wiki/).
4. Existing diagram sources (*.mermaid / *.dot / *.drawio / *.excalidraw).
5. Harness folders present (.claude/, .cursor/, .codex/, .continue/, .agents/).

## Stop condition
render + validate + build + preview all exit 0 with no errors and no LOW_CONTRAST_TEXT / ASPECT_RATIO_EXTREME warnings.

## Evidence buckets

For every finding / claim, label it:

- `Verified` — backed by primary source or repo evidence with citation.
- `Inferred` — extrapolated from related evidence; explicitly say so.
- `Open` — could not verify; goes in the Open Questions section.

## Citation discipline

- Cite file paths as `path/to/file.ext:LINE-LINE`.
- Cite URLs with retrieval date (e.g. "fetched 2026-04-21").
- Cite git commits as short SHAs from the host repo.
- Cite cloned reference repos as `.temp/reference-repos/<owner>__<repo>/path:LINE`.

## Freshness

Treat any web source older than 6 months for fast-moving libraries (React, Vite, browser APIs) as suspect — verify against the latest official changelog before using.
