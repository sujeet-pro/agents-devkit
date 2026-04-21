# Research Protocol

`adk-build-deps` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: package manifest + lockfile + tooling configs.
2. Vendor advisories: GitHub Advisory DB, OSV.dev, ecosystem-native (npm audit, pip-audit, cargo-audit).
3. Each dep's changelog (CHANGELOG.md / GitHub releases) for any non-patch bump.
4. License metadata via tooling (license-checker, pip-licenses, etc.).

## Stop condition
Every change has a justification (security, performance, fix, license) and tests still pass.

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
