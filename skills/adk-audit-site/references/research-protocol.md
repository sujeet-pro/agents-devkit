# Research Protocol

`adk-audit-site` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Lighthouse on each chosen URL (mobile + desktop).
2. axe-core scan via browser MCP.
3. Manual keyboard pass on every interactive surface.
4. HTTP headers via curl -I (security: HSTS, CSP, X-Frame-Options, etc.).
5. robots.txt / sitemap.xml / canonical / Open Graph / structured data.

## Stop condition
Every chosen URL has Lighthouse + axe + manual evidence.

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
