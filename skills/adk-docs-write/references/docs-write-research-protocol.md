# Research Protocol

`adk-docs-write` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: code, configs, scripts, CI files, env files, related docs already present.
2. If multi-repo: each repo passed via URL or path; clone HTTPS URLs into .temp/reference-repos/ if not already local.
3. Recent git log on the documented surface (catch drift since last doc update).
4. Issues / tickets that prompted the doc.
5. Primary docs of any external system referenced in examples.

## Stop condition
Every example is verified, every link resolves, the validation checklist passes.

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
