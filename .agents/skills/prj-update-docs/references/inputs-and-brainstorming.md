# Inputs + brainstorming questions

Skipped under `--auto`. When interactive, ask one question at a time per the project
[interaction contract](../../../../bin/canonical/interaction-contract.md). Each question
documents the safe `--auto` default in column 3 — the skill picks that default unattended
and logs the choice into the final report so the user can override afterwards.

| #  | Question                                                                                                                  | Safe `--auto` default                                              |
| -- | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| 1  | **Scope**: full repo, or one of `skills` / `agents` / `hooks` / `bin` / `mcp` / `monitors` / `config` / `diagrams-only`?   | `all` (full sync)                                                  |
| 2  | **Mode**: `auto` (write + validate), `review` (read-only drift report), `fix` (regenerate only changed pages)?            | `auto`                                                             |
| 3  | **Diagram budget**: regenerate every diagram, or only those whose source changed since `<since>`?                         | Regenerate every diagram (matches `diagramkit-review` policy).     |
| 4  | **Approval gates between phases**?                                                                                        | Off (per `--auto`).                                                |
| 5  | **`pagesmith-docs build` smoke test** — run it after page write?                                                          | Yes.                                                               |
| 6  | **`pagesmith-docs dev` smoke test** — start the dev server and curl the freshly-generated section index pages?            | Off (only run interactively).                                      |
| 7  | **Page deletion** — when an artifact's source is gone, delete the orphan page, or just propose deletion in the report?    | Propose only (no destructive default).                             |
| 8  | **Schema-pinned config** — should `pagesmith.config.json5` `$schema` be re-pointed to the installed package version?      | Yes (idempotent: matches the installed `node_modules/...` schema). |
| 9  | **Cross-link enforcement** — should this run also enforce the dual-form `@adk:foo (a.k.a. adk-foo)` convention on first mention? | Yes (matches `bin/adk-validate`).                              |
| 10 | **Diagram engine override** — force one engine for any new diagrams this run?                                             | None (delegate to `diagramkit-auto` selection table).              |

## Output of brainstorming

Append to the final report under "Choices":

```markdown
## Choices

| # | Question | Selected |
| - | -------- | -------- |
| 1 | Scope    | all      |
| 2 | Mode     | auto     |
| ...                          |
```

Every choice is overrideable by re-running with explicit flags (e.g. `--scope skills`).

## What this skill never asks

- Anything related to the docs site **bootstrap** — that's `adk-doc-site-setup`.
- Anything related to **adding** a new skill or agent — that's `adk-build-feature` /
  `adk-build-refactor` plus the relevant scaffolding skill. This skill only documents
  what's already shipped.
- Whether to install `diagramkit` or `pagesmith-docs` — they must already be in
  `node_modules/`, otherwise the skill stops with a "missing dependency" error in the
  report.
