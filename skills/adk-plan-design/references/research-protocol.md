# Research Protocol

`adk-plan-design` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. Repo: existing architecture, related services, deployed topology, current data model.
2. Spec artifact (if upstream): .temp/drafts/spec-<slug>.md.
3. Production telemetry / metrics / SLOs when available.
4. Primary docs of any external system being integrated.
5. Comparable architectures from well-known open-source projects (cite specifically).

## Stop condition
Every alternative is rejected with reason, every failure mode has a mitigation, rollout has a rollback.

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
