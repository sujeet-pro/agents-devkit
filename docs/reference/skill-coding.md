---
title: "coding"
description: "Detects repo tools, frameworks, and languages, then loads matching coding guidelines"
skill_name: coding
category: guideline
workflow_tier: helper
user_invocable: false
---

# coding

Helper skill that detects the repository's languages, frameworks, and tooling, then loads matching coding guidelines from a shared guideline library. Invoked by review, PR, and development skills before analysis work — not directly by users.

## Purpose

- Auto-detect the tech stack from package files, config files, file extensions, and directory structure
- Load the right subset of coding guidelines for the detected stack
- Support scoped detection (changed files only) for PRs and full detection for repo-wide reviews
- Load repo-local guidelines (CLAUDE.md, .cursorrules, .editorconfig) alongside stack-specific standards

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--scope` | `scoped` \| `full` | `scoped` | Detection scope: `scoped` analyzes only changed files; `full` scans the entire repository |

## Key Behaviors

### Framework Detection

Scans the repository root and changed files to identify the tech stack through three signal types:

**Package and config files:**

| File | Signals |
|------|---------|
| `package.json` | Node.js; dependencies for `next`, `react`, `vue`, `svelte`, `express`, `fastify`, `nestjs` |
| `tsconfig.json` | TypeScript |
| `next.config.*` | Next.js frontend |
| `pom.xml` | Java (Maven) |
| `build.gradle`, `build.gradle.kts` | Java or Kotlin (Gradle) |
| `pyproject.toml`, `requirements.txt`, `setup.py` | Python; dependencies for `fastapi`, `django`, `flask` |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `.storybook/` | Design system |

**File extensions:** `.java` → Java, `.kt`/`.kts` → Kotlin, `.py` → Python, `.ts`/`.tsx`/`.jsx` → TypeScript/JavaScript (`.tsx`/`.jsx` signals frontend), `.vue` → Vue, `.svelte` → Svelte, `.go` → Go, `.rs` → Rust, `.sh`/`.zsh`/`.bash` → Scripts, `.css`/`.scss`/`.less` → Frontend styling.

**Directory structure:** `src/main/java/` → Java, `src/main/kotlin/` → Kotlin, `pages/`/`app/`/`components/` → Frontend, `scripts/`/`bin/` → Scripts and tooling.

### Guideline Loading Logic

**Always loaded** (every codebase):
- `general.md` — universal coding standards
- `architecture.md` — architecture principles

**Conditionally loaded** (based on detected stack):

| Detection | Guideline |
|-----------|-----------|
| Next.js, React, Vue, Svelte, or frontend files | `frontend-nextjs.md` |
| Design system or Storybook | `design-system.md` |
| Backend (any language) | `backend-general.md` |
| Java | `backend-java.md` |
| Kotlin | `backend-kotlin.md` |
| Node.js backend (Express, Fastify, NestJS) | `backend-nodejs.md` |
| Python backend (FastAPI, Django, Flask) | `backend-python.md` |
| JS/TS library (publishable npm package) | `js-ts-library.md` |
| Shell scripts or tooling | `scripts.md` |

**Area-specific** (based on changed files touching the relevant area):

| Area | Guideline | Trigger |
|------|-----------|---------|
| Security | `security.md` | Auth files, crypto, secrets, permission checks, input sanitization |
| Testing | `testing.md` | Test files, test configs, `*.test.*`, `*.spec.*`, `__tests__/` |
| Observability | `observability.md` | Logging, metrics, tracing, monitoring, alerting code |
| API design | `api-design.md` | API route handlers, OpenAPI specs, GraphQL schemas, controller files |
| Code formatting in docs | `expressive-code.md` | Markdown files with code blocks, documentation with examples |

**Repo-local guidelines**: CLAUDE.md coding sections, `.cursor/rules` or `.cursorrules`, project README contributing/code style sections, `.editorconfig`, lint configs.

### Scoped vs Full Detection

- **Scoped** (default for PRs and branch reviews): only detects frameworks relevant to changed files. Avoids loading Java guidelines when the PR only touches Python files.
- **Full** (for codebase reviews): detects all frameworks present in the repository.

## What It Provides

A list of guideline file paths for the calling skill to read and incorporate into its review or fix context:

```
Always:
- general.md
- architecture.md

Stack-specific:
- backend-general.md
- backend-nodejs.md

Area-specific:
- testing.md
- api-design.md

Repo-local:
- CLAUDE.md (coding sections)
```

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | guideline loading phase |
| `code-review-repo` | guideline loading phase (with `--scope full`) |
| `code-review-fix` | guideline loading phase |
| `audit` | guideline loading phase |
| `dev-build` | guideline loading phase |
| `dev-refactor` | guideline loading phase |
| `dev-migrate` | guideline loading phase |
