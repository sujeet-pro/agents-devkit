# Changelog

All notable changes to the `adk` marketplace are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the marketplace adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-05-03

Initial release. **5 plugins, 37 skills, 3 custom MCPs.**

### Added

#### Marketplace

- `.claude-plugin/marketplace.json` — registers the `adk` marketplace with 5 plugins.
- `README.md` — install paths (A-D), audience matrix, MCP strategy.
- `SETUP.md` — env-var walkthrough per MCP with verifier curl one-liners.
- `scripts/verify_marketplace.py` — manifest + SKILL.md validator.

#### `adk-core` (7 skills)

- `auto` — top-level prompt-routing dispatcher (the default entry point).
- `prompt-expand` — standalone prompt-expansion skill any other skill can call.
- `setup` — bootstrap `~/.config/adk/*.md` from templates; check CLI deps + env vars.
- `info` — read & merge `~/.config/adk/*.md` into structured JSON.
- `temp-folder` — canonical `.temp/task-<slug>/` working-artifact layout.
- `mode-contract` — universal `--auto / -i / --fix` definition.
- `context-gather` — follow links in a prompt (Jira / Confluence / GDoc / Slack / GitHub) and produce `context.md`.
- Hooks: `PreToolUse:Bash` (safety), `SessionStart` (status banner), `PostToolUse:Edit|Write` (touch task).
- Bin scripts: `adk-info`, `adk-task-slug`, `adk-mcp-health`.
- Agents: `dispatcher`, `prompt-expander`, `context-gatherer`.
- Templates: starter `~/.config/adk/*.md` for all 10 topics.

#### `adk-code` (8 skills)

- `code-write` — implement a new feature.
- `code-bugfix` — fix a bug with reproducer + smallest patch + regression test.
- `code-refactor` — restructure without behavior change.
- `code-migrate` — framework / runtime / library migration.
- `code-test` — author or expand automated tests.
- `code-perf` — diagnose and fix a perf regression.
- `code-api` — design or evolve an API contract.
- `code-security` — implement a security-hardening change.
- Agents: `implementer`, `test-engineer`.

#### `adk-review` (6 skills)

- `review-pr` — review a remote PR (own or peer); ownership-aware.
- `review-code-changes` — self-review of local working-tree changes.
- `review-feedback` — triage existing reviewer comments and address them.
- `review-handoff` — capture a session-handoff document.
- `audit-pr` — fast fixed-set audit on a single PR.
- `audit-repo` — whole-repo multi-dimensional audit.
- Agents: `code-reviewer`, `security-reviewer`.
- MCP: `github` (Docker, pinned `v1.0.3`, read-only by default; `gh` CLI as fallback).

#### `adk-docs` (8 skills)

- `docs-write` — author README / runbook / ADR / migration guide / etc.
- `docs-review` — review existing markdown / Confluence / GDoc.
- `docs-pr-description` — draft a PR description from the diff.
- `docs-commit-message` — draft a commit message from the staged diff.
- `docs-changelog` — append / update CHANGELOG.md.
- `docs-diagram` — author Mermaid diagrams.
- `docs-publish-confluence` — publish markdown as a Confluence page.
- `docs-publish-gdrive` — publish markdown to Google Drive.
- Agents: `doc-writer`, `doc-reviewer`.

#### `adk-investigate` (8 skills)

- `investigate-datadog` — DD logs / metrics / traces / monitors / dashboards.
- `investigate-mixpanel` — funnels / cohorts / engagement.
- `investigate-statsig` — experiment pulse / gates / audit log.
- `investigate-snowflake` — read-only non-PII queries.
- `investigate-deploy` — recent deploy timeline via `gh run list`.
- `investigate-incident` — multi-source triage (DD + deploys + Slack).
- `investigate-experiment` — Statsig + Mixpanel + DD cross-check for ship/iterate/kill.
- `investigate-rca` — full root-cause analysis composite.
- Agent: `incident-investigator`.
- MCPs: `datadog` (hosted), `statsig` (hosted).

### MCP strategy

- 3 custom MCPs shipped: GitHub (Docker), Datadog (hosted), Statsig (hosted).
- 7 workspace connectors consumed (no re-shipping): Atlassian, Google Drive, Gmail, Google Calendar, Slack, Mixpanel, Snowflake.

### Notes

- Per-user only — no multi-user / org-shared meta-info.
- `--auto + --fix` composes but never auto-merges, never force-pushes protected branches, never deletes branches.
- All working artifacts live under `.temp/task-<slug>/` (gitignored).
- Skill descriptions are "pushy" so Claude's matcher auto-routes natural-language prompts to the right skill without `/adk-...` invocation.
