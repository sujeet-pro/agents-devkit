# Research Protocol

`adk-plan-roadmap` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: file tree, existing module boundaries, test layout, build pipeline.
2. Source spec/design at .temp/drafts/spec-<slug>.md or .temp/drafts/design-<slug>.md.
3. Recent git log on touched paths (to spot in-flight work).
4. Open PRs and tickets that touch the same files.

## Stop condition
Every step is small enough to validate independently and the order keeps the codebase buildable.

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
