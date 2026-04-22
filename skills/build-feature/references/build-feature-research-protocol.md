# Research Protocol

`adk-build-feature` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: target file + immediate dependencies + tests covering the touched paths.
2. Recent git log on touched paths (to avoid colliding with in-flight work).
3. Spec/roadmap at .temp/drafts/spec-<slug>.md or .temp/plans/roadmap-<slug>.md if upstream.
4. Primary docs of any new API call or library being introduced.

## Stop condition
Enough context to write the smallest correct change without surprise.

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
