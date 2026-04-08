---
title: "coding"
description: Detects repo tech stack and loads matching coding guidelines
skill_name: coding
category: guideline
workflow_tier: helper
user_invocable: false
---

# coding

Detects the repository's languages, frameworks, and tools, then loads matching coding guidelines from a shared library of 16 guideline files.

## Purpose

Provides stack-specific coding standards to review, PR, and development skills. Detects from `package.json`, file extensions, directory conventions, and config files.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--scope` | `scoped`, `full` | `scoped` | Load only relevant guidelines vs all |

## Detection

Detects stack from signals like:
- `package.json` → JavaScript/TypeScript, framework (React, Next.js, Vue, etc.)
- File extensions → Python, Go, Rust, Java, etc.
- Directories → `src/`, `api/`, `infra/`, `test/`
- Config files → `.eslintrc`, `tsconfig.json`, `pyproject.toml`

## Guidelines Loaded

Always loads `general.md` + `architecture.md`. Conditionally loads stack-specific files:
- Frontend: `frontend.md`, `react.md`, `vue.md`, `angular.md`
- Backend: `backend-node.md`, `backend-python.md`, `backend-go.md`
- Areas: `security.md`, `testing.md`, `api.md`, `database.md`

Also reads repo-local hints from `CLAUDE.md`, `.cursorrules`, etc.

## Output

Produces a "Coding Guidelines Loaded" list for the parent skill to consume.

## Invoked By

`code-review-pr`, `code-review-repo`, `code-review-fix`, `dev-build`, `dev-refactor`, `audit`.
