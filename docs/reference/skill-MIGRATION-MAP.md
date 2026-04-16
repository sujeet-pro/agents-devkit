---
title: Skill Migration Map
description: Legacy-to-public parity map and deletion gate for removing legacy-skills
order: 5
---

# Skill Migration Map

This page tracks where each legacy skill landed after the public-catalog refactor.

## Status Key

- `covered`: replaced by a focused public `adk-*` skill
- `merged`: functionality absorbed into another public skill or shared guidance
- `shared`: moved into `ai-guidelines/` or copied references
- `runtime`: intentionally handled by runtime MCP/config or an existing non-ADK built-in skill
- `open`: still needs an explicit successor before `legacy-skills/` can be deleted safely

## Covered Or Merged Into Public Skills

| Legacy Skill | Current Destination | Status | Notes |
| --- | --- | --- | --- |
| `plan` | `adk-plan` | covered | direct planning successor |
| `research` | `adk-research` | covered | direct research successor |
| `dev-build` | `adk-build` | covered | implementation and validation |
| `dev-refactor` | `adk-refactor` | covered | behavior-preserving structure work |
| `dev-migrate` | `adk-migrate` | covered | migration-specific workflow |
| `dev-commit` | `adk-commit` | covered | commit, PR, and changelog packaging |
| `diagram` | `adk-diagram` | covered | direct visual-diagram successor |
| `diagram-mermaid` | `adk-diagram` | merged | engine selection moved inside one skill |
| `diagram-excalidraw` | `adk-diagram` | merged | engine selection moved inside one skill |
| `diagram-drawio` | `adk-diagram` | merged | engine selection moved inside one skill |
| `diagram-graphviz` | `adk-diagram` | merged | engine selection moved inside one skill |
| `code-review-pr` | `adk-review-pr` | covered | hosted PR review |
| `code-review-fix` | `adk-address-review-feedback` | covered | fix-and-close-loop successor |
| `code-review-repo` | `adk-audit-repo` | merged | whole-repo findings and prioritization |
| `docs-write` | `adk-write-docs` | covered | authoring and updates |
| `docs-review` | `adk-review-docs` | covered | review-only successor |
| `docs-crud` | `adk-write-docs` | merged | `create`, `update`, `improve`, and `publish` actions |
| `docs-repo` | `adk-write-docs` | merged | repo-doc work now uses scope plus project/reference templates |
| `docs-confluence` | `adk-write-docs` | merged | publish/template URL behavior depends on runtime connector support |
| `spec` | `adk-plan` + `adk-write-docs` | merged | plan-first plus `tdd`/`rfc`/`prd`-style templates |
| `audit` | `adk-audit-repo` + `adk-audit-site` | merged | repo audits and live-site audits split cleanly |
| `test` | `adk-test` | covered | acceptance, regression, and webapp testing |
| `design` | `adk-design` | covered | UI and UX audit/design work |
| `chart` | `adk-chart` | covered | chart-specific output instead of diagrams |

## Moved Into Shared Guidance

| Legacy Skill | Current Destination | Status | Notes |
| --- | --- | --- | --- |
| `workflow` | per-skill `references/workflow.md` + `ai-guidelines/constitution.md` | shared | no longer a standalone public skill |
| `output-format` | `ai-guidelines/output-format.md` | shared | copied into public skills under `references/_shared/` |
| `communication` | `ai-guidelines/output-format.md` + personas | shared | tone and result-shape rules centralized |
| `principal-engineer` | `ai-guidelines/constitution.md` + personas | shared | accuracy-over-speed and evidence bar |
| `review-standards` | review skill contracts + `ai-guidelines/output-format.md` | shared | findings-first review rules embedded in public review skills |
| `preflight-check` | per-skill `scripts/preflight.py` | shared | dependency validation stays per skill |
| `docs-guidelines` | `adk-write-docs` template catalog + workflow | shared | doc-type guidance now ships with the docs skill |
| `docs-md` | `ai-guidelines/output-format.md` | shared | markdown portability rules centralized |
| `coding` | `ai-guidelines/constitution.md` + build/refactor/migrate personas | shared | implementation rules moved to shared guidance |
| `architecture` | `adk-write-docs` templates + `adk-diagram` | merged | architecture writing and diagrams split by artifact |
| `interaction` | runtime interaction rules + skill-specific parameter contracts | shared | no standalone public surface |
| `interactivity` | runtime interaction rules + skill-specific parameter contracts | shared | no standalone public surface |
| `agentic-teams` | shared repo/runtime orchestration guidance | shared | not a public specialist task skill |
| `workspace-conventions` | `AGENTS.md`, `CLAUDE.md`, repo-only maintenance guidance | shared | repo-specific, not public |

## Intentionally Removed As Public Routers

| Legacy Skill | Current Destination | Status | Notes |
| --- | --- | --- | --- |
| `use` | direct public skill selection | merged | router removed to avoid duplicated entrypoints |
| `dev` | direct public development skills | merged | use `adk-build`, `adk-refactor`, `adk-migrate`, `adk-commit` directly |
| `docs` | direct public documentation skills | merged | use `adk-write-docs` or `adk-review-docs` directly |
| `code-review` | direct public review skills | merged | use the specific review skill that matches the artifact |

## Handled By Runtime Or Existing External Skills

| Legacy Skill | Current Destination | Status | Notes |
| --- | --- | --- | --- |
| `setup` | `docs/reference/config/README.md` + `settings/mcp-setup.md` | runtime | runtime-specific configuration and MCP setup should not require a public ADK skill |
| `create-skill` | existing built-in `create-skill` runtime skill | runtime | do not duplicate generic skill-authoring helpers in the public ADK catalog |
| `github` | runtime MCP server | runtime | use the MCP server directly instead of a public connector skill |
| `bitbucket` | runtime MCP server | runtime | use the MCP server directly instead of a public connector skill |
| `confluence` | runtime MCP server | runtime | use the MCP server directly instead of a public connector skill |
| `jira` | runtime MCP server | runtime | use the MCP server directly instead of a public connector skill |

## Still Open Before Safe Deletion

| Legacy Skill | Current Destination | Status | Notes |
| --- | --- | --- | --- |
| `project` | none yet | open | project and milestone workflows were not re-homed in this pass |
| `handoff` | none yet | open | session continuity flow still needs a destination |
| `team` | none yet | open | explicit multi-agent coordination is not published yet |
| `deps-tracker` | none yet | open | dependency-tracking workflow was not migrated |

## Deletion Gate

`legacy-skills/` is safe to delete only when all of these are true:

1. every `open` row above has either a successor or an explicit deprecation decision
2. `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared` succeeds and public skills are refreshed
3. `python3 scripts/generate-skills-manifest.py --check` passes
4. `python3 tests/test_skills.py` passes
5. `npm run docs:build` passes

## Current Decision

Do not delete `legacy-skills/` yet. Connector/setup-style skills are no longer blockers, but `project`, `handoff`, `team`, and `deps-tracker` still need an explicit resolution.
