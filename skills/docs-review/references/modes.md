# `docs-review` — modes

This skill supports the following `--mode` values:

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Source-aware delivery: post comments back when the source supports it (Confluence inline + footer), otherwise write a Markdown review file under `.temp/reports/`. Approval gates active unless `--auto`. |
| `review` | Force findings-only. On Confluence this overrides the default `post` and emits a dry-run report. Never edits source. |
| `fix` | Run `--mode auto` to finalize findings, then hand off auto-fixable findings to `adk-docs-write` to edit the source Markdown, then re-validate by re-running `--mode review` and appending residuals to the report. Confluence pages cannot be auto-edited; `--fix` only applies to Markdown sources. |

`--auto` is orthogonal and skips approval gates regardless of `--mode`.
The `--fix` flag is a shorthand for `--mode fix`.
See `@adk:mode-contract` (a.k.a. `adk-mode-contract`) for the universal contract.

## Source-aware default delivery

When `--mode` is `auto` (the default), this skill picks the deliverable from the source type:

| Source type | Default deliverable | Why |
| --- | --- | --- |
| Confluence page (`*.atlassian.net/wiki/...`) | Inline + footer comments posted on the live page | The source supports comments — that IS the natural deliverable |
| Local Markdown / fetched URL | Markdown review file at `.temp/reports/doc-review-<slug>.md` | No live posting target exists, so the review IS the artifact |

`--mode review` always falls back to a Markdown report regardless of source.
