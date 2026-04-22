# Research Protocol for `adk-docs-review`

The skill consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. **The doc itself** — local file or fetched URL / Confluence page in current revision. Read end-to-end.
2. **The source-of-truth files / configs** — every code file, schema, env var definition, command, etc. that the doc claims to describe. Read in current state.
3. **Recent git log on the source surface** — `git log --oneline -- <changed-paths>` to detect drift since the doc's last touch (helps explain WHY a finding exists).
4. **(Confluence mode) Existing inline + footer comments** — fetched once at the start; used by `doc-comment-reconciliation.md`. Do NOT re-file what is already raised.
5. **Related ADRs / RFCs / specs** — any decision document that should be reflected in the doc but is not.
6. **External docs** — official upstream docs (framework, library, language). Use sparingly; only when the finding turns on a published API contract that the doc cites.

## Stop condition

Every doc claim that can be checked against the live source HAS been checked. Every finding has Type, Severity, Confidence, doc anchor, source anchor, quoted evidence, and a justified suggested fix. The verdict is justified by the highest-severity finding.

## Evidence buckets

For every finding, label it (in `.temp/notes/`, not in the posted comment):

- `Verified` — the doc claim was checked against the live source-of-truth and they disagree (or agree, in the case of Praise). Evidence: doc anchor + source anchor + quoted snippet from each.
- `Inferred` — the doc claim could not be checked against an explicit source; the finding is based on a related signal (e.g., the doc mentions a CLI flag that does not appear in any `--help` output, but no source file was named). Cap `Confidence` at 70/100 and label clearly.
- `Open` — could not verify; goes in the `Question` section of the report, not as a posted Issue. Cap `Confidence` at 50/100.

## Citation discipline

- Doc anchors:
  - Local: `path/to/doc.md:LINE-LINE` OR section heading slug.
  - Confluence: page ID + section heading + (when posting inline) the verbatim text snippet.
- Source anchors: `path/to/file.ext:LINE-LINE` OR URL with retrieval date.
- Cite git commits as short SHAs (the commit that last touched the source surface).
- Cite cloned reference repos as `.temp/reference-repos/<owner>__<repo>/path:LINE`.
- Cite external docs with retrieval date (e.g., "fetched 2026-04-21").

## Freshness

Treat any external web source older than 6 months for fast-moving libraries (React, Vite, Next.js, browser APIs) as suspect — verify against the latest official changelog before citing.

For internal docs, the git log on the source surface is the freshness signal. If the source has changed since the doc's last touch, flag for `freshness` review.

## Doc-vs-source trade-off

The doc and the source both have to be re-read every run. Caching is not safe — both sides drift.

If the doc is huge and the source is huge, propose batching to the user (per `doc-review-clarifying-questions.md`):

- batch by section (one section at a time)
- batch by focus (one of accuracy / freshness / structure / etc. at a time)
- batch by source area (find drift in one module at a time)
