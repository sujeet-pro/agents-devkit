# Research Protocol

`adk-publish-commit` consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. git diff (staged + unstaged or branch vs base).
2. git log of last 20 commits for style detection.
3. Branch name (often carries ticket ID).
4. Existing PR template (.github/PULL_REQUEST_TEMPLATE.md).

## Stop condition
Message reads cleanly to a stranger and matches repo convention.

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
