# Research Protocol

`adk-review-pr` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. PR diff + description + linked issue (gh/bitbucket CLI or MCP).
2. Files in their post-PR state, plus immediate dependencies and tests.
3. Existing comments on the PR (do not re-file what's already raised).
4. Repo conventions (lint config, code-style doc, .editorconfig).

## Stop condition
Every finding has evidence and severity; verdict is justified by the highest-severity findings.

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
