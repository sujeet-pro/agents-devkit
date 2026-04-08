# Changelog

All notable changes to the Agent Development Kit (ADK) are documented in this file.

Format follows [Keep a Changelog](https://keepachangelog.com/). Versioning uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `maturity` field in skill frontmatter (`experimental`, `stable`, `battle-tested`) for skill maturity signaling
- `create-skill` meta-skill for interactive scaffolding of new skills
- `llms.txt` for AI-readable project summary
- `skills-manifest.json` for programmatic skill discovery and external indexing
- PreToolUse hooks for blocking dangerous git operations (force push, hard reset on main/master)
- Cross-agent portability documentation (Cursor, Codex, Gemini CLI installation paths)
- Workspace context convention (`.adk/context.yaml`) for project-specific defaults
- Composable workflow YAML convention with example pipelines in `workflows/`
- `CHANGELOG.md`

### Changed
- Enhanced `hooks.json` with PreToolUse safety hooks alongside existing PostToolUse and Stop hooks
- Updated `SKILL-TEMPLATE.md` with `maturity` field
- Updated `test_skills.py` to validate `maturity` field in all skills
- Updated `CONTRIBUTING.md` with maturity field, workspace context, and workflow composition docs

## [2.0.0] — 2026-04-08

### Added
- 51 skills across 4 categories: 29 task, 17 guideline/helper, 5 routing/orchestrator
- 18 reusable agent definitions with persistent memory and effort settings
- 4 workflow families: Quick Action, Standard Task, Complex Build, Investigative Loop
- Complexity-adaptive phase skipping (trivial → large)
- Token-efficient lazy loading (~200–500 lines per task from ~42,000 total)
- Self-sufficient skills with inline fallback summaries for all shared knowledge
- Plugin distribution via Claude Code (`/plugin install adk@adk-marketplace`)
- skills.sh distribution (`npx skills add sujeet-pro/agents-devkit`)
- 16 coding guidelines and 24 document-writing guidelines with lazy stack detection
- 4 connector skills: GitHub, Bitbucket, Confluence, Jira
- 4 diagram engines: Mermaid, Excalidraw, Draw.io, Graphviz (from diagramkit)
- Hooks: PostToolUse (frontmatter validation), Stop (task completion), SessionStart (routing hint)
- Template propagation system (`propagate.py`) for cross-skill common files
- Test suite (`test_skills.py`) validating structure, frontmatter, propagation, and cross-references
- `manifest.json` tracking upstream sources (diagramkit, superpowers, pagesmith)
- Pagesmith-powered documentation site (`docs/guide/`, `docs/reference/`)

### Changed
- Restructured from initial setup to plugin architecture with `adk:` namespace
- Consolidated TUI interactivity into agent-first patterns (removed external scripts)
- Reworked PR review comment format, severity tiers, and review dimensions
- Standardized skill naming: `name` field matches directory, `description` starts with `adk -`

## [1.0.0] — 2026-03-18

### Added
- Initial skill library with core development, review, and documentation skills
- Multi-model support and script infrastructure
- Claude Code configuration and setup tooling

[Unreleased]: https://github.com/sujeet-pro/agents-devkit/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/sujeet-pro/agents-devkit/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/sujeet-pro/agents-devkit/releases/tag/v1.0.0
