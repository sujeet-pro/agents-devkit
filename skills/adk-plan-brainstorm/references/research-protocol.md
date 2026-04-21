# Research Protocol

`adk-plan-brainstorm` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo evidence first: file paths, recent git log, existing tests, related PRs, current behavior reproductions.
2. Primary docs of any framework/library involved (vendor docs, RFCs, ADRs already in the repo).
3. Comparable open-source projects only when needed to differentiate options.

## Stop condition
Each option has at least one verified pro and one verified con; no remaining unknown is direction-changing.

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
