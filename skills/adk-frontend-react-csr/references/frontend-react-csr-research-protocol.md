# Research Protocol

`adk-frontend-react-csr` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Latest stable versions of: vite, @vitejs/plugin-react, react/react-dom, babel-plugin-react-compiler, @tanstack/react-router/query/hotkeys, radix-ui, oxlint/oxfmt, @typescript/native-preview, typescript, vitest.
2. Each pinned lib's release notes for the chosen version.
3. Existing app in the target repo (for feature/audit modes).
4. WCAG 2.2 AA + WAI-ARIA APG for any new interactive surface.

## Stop condition
Versions captured, deps install cleanly, full validation matrix passes.

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
