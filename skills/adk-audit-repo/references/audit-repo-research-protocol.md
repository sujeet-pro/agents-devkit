# Research Protocol

`adk-audit-repo` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: file tree, languages, frameworks, package managers, test frameworks, total LOC.
2. Analyzers: lint, typecheck, security audit (npm audit / pip-audit / cargo-audit / govulncheck), license-checker, SAST if available.
3. Manifests + lockfiles for every package manager in use.
4. Recent git log to spot active hotspots.
5. If multi-repo: clone each into .temp/reference-repos/ and audit independently, reporting per-repo findings.

## Stop condition
Each requested dimension has been inspected with at least one verified pass.

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
