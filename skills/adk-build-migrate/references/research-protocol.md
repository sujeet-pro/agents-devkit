# Research Protocol

`adk-build-migrate` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Upstream migration guide (vendor docs) — the authoritative source.
2. Upstream changelog between source and target version.
3. Repo: every call site of the deprecated APIs (use grep/AST tooling).
4. Open issues / discussions on the upstream repo for known gotchas at the target version.

## Stop condition
Every breaking change in the changelog has a planned step or an explicit not-applicable note.

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
