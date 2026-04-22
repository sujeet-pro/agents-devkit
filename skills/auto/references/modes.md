# `auto` — mode contract

`auto` supports only `--mode auto` (the default). It IS the orchestration loop; review-only and fix-only modes do not make sense at this layer.

If the user wants:

- **Just a review of an existing PR** → use `@adk:review-pr` directly, not `auto`.
- **Just a code fix without planning** → use `@adk:build-feature` (or `build-bugfix`) directly with `--mode fix --auto`.
- **Just a doc** → use `@adk:docs-write` directly.

`auto` ends every run with `validate-browser`, `review-local`, and (if applicable) `cicd-monitor`. None of these can be skipped.

`--auto` (orthogonal to `--mode`) skips approval gates between phases but keeps every validator gate active.
