# Research Protocol

`adk-plan-research` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: existing code, tests, configs, ADRs, prior research notes in .temp/.
2. Primary docs: vendor documentation, RFCs, official changelogs, language specs.
3. Source code: tagged release of the library (clone into .temp/reference-repos/ if needed).
4. Standards: W3C, IETF, ECMA, IEEE for protocol-level facts.
5. Reference projects: well-known open-source repos using the same framework — only to verify common usage.
6. Last resort: blog posts / Stack Overflow, only with publish date ≥ current major version.

## Stop condition
Confidence target reached and at least 2 independent primary sources agree, or contradiction is documented.

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
