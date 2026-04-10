---
title: 'coding'
description: 'Helper skill that detects repo tools, frameworks, and languages, then loads matching coding guidelines from the shared guideline library — invoked by review, PR, and development skills, not directly by users'
skill_name: coding
category: guideline
workflow_tier: helper
user_invocable: false
---

# coding

`coding` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`coding` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--scope` | `scoped`, `full` | `scoped` | Detection scope: scoped (changed files only) or full (entire repo) |

### Parameter Notes

- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.

## How It Works

Helper skills do not usually own the top-level conversation. The calling skill decides when to load them, passes just enough context to resolve the right rules or references, and then consumes the returned guidance inside its own execution flow.

The important developer contract is therefore: when the helper is loaded, what context it reads, what rules or artifacts it returns, and how that changes the calling skill's behavior.

### Workflow

This is a helper skill invoked by other skills, not directly by users. It does not own the workflow — the invoking skill does.

### Guideline Loading

### Always Load

These apply to every codebase:

- `${CLAUDE_SKILL_DIR}/references/coding-guidelines/general.md`
- `${CLAUDE_SKILL_DIR}/references/coding-guidelines/architecture.md`

### Conditional — Based on Detected Stack

| Detection | Guidelines |
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

### Area-Specific — Based on Changed Files

Load these when the changes touch the relevant area:

| Area | Guideline | Trigger |
|------|-----------|---------|
| Security | `security.md` | Auth files, crypto, secrets, permission checks, input sanitization |
| Testing | `testing.md` | Test files, test configs, `*.test.*`, `*.spec.*`, `__tests__/` |
| Observability | `observability.md` | Logging, metrics, tracing, monitoring, alerting code |
| API design | `api-design.md` | API route handlers, OpenAPI specs, GraphQL schemas, controller files |
| Code formatting in docs | `expressive-code.md` | Markdown files with code blocks, documentation with examples |

### Repo-Local Guidelines

Also check for and load project-specific coding guidance:

- `CLAUDE.md` coding sections
- `.cursor/rules` or `.cursorrules`
- Project README sections on contributing or code style
- `.editorconfig`, lint configs for style conventions

## Modes & Variations

Most helpers do not have end-user modes in the same sense as task skills, but they still vary by scope, invoking context, selected family, or fallback behavior.


### Behavior Variations

- **`--scope scoped`** (default for PRs and branch reviews): only detects frameworks relevant to changed files
- **`--scope full`** (for codebase reviews): detects all frameworks present in the repository
- Always loads `general.md` and `architecture.md` guidelines
- Conditionally loads stack-specific guidelines (frontend, backend, language-specific)
- Conditionally loads area-specific guidelines (security, testing, observability, API design)
- Also loads repo-local guidelines (CLAUDE.md, .cursorrules, .editorconfig)

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


### Output

Produce a list of guideline file paths to load. The calling skill reads these files and incorporates the guidelines into its review or fix context.

```text

## Additional Reference

### Framework Detection

Scan the repository root and changed files to identify the tech stack.

### Package and Config Files

| File | Signals |
|------|---------|
| `package.json` | Node.js; check `dependencies`/`devDependencies` for `next`, `react`, `vue`, `svelte`, `express`, `fastify`, `nestjs` |
| `tsconfig.json` | TypeScript |
| `next.config.*` | Next.js frontend |
| `pom.xml` | Java (Maven) |
| `build.gradle`, `build.gradle.kts` | Java or Kotlin (Gradle); check for `kotlin` plugin |
| `pyproject.toml`, `requirements.txt`, `setup.py` | Python; check for `fastapi`, `django`, `flask` |
| `go.mod` | Go |
| `Cargo.toml` | Rust |
| `.storybook/` | Design system |

### File Extension Scanning

When a set of changed files is provided (from a PR diff or branch changes), scan extensions:

- `.java` -> Java backend
- `.kt`, `.kts` -> Kotlin backend
- `.py` -> Python backend
- `.ts`, `.tsx`, `.jsx` -> TypeScript/JavaScript; `.tsx`/`.jsx` signals frontend
- `.vue` -> Vue frontend
- `.svelte` -> Svelte frontend
- `.go` -> Go backend
- `.rs` -> Rust
- `.sh`, `.zsh`, `.bash` -> Scripts
- `.css`, `.scss`, `.less` -> Frontend styling

### Directory Structure Signals

- `src/main/java/` -> Java
- `src/main/kotlin/` -> Kotlin
- `pages/`, `app/`, `components/` -> Frontend
- `scripts/`, `bin/` -> Scripts and tooling

### Scoped vs Full Detection

- **Scoped** (default for PRs and branch reviews): Only detect frameworks relevant to the changed files. Avoids loading Java guidelines when the PR only touches Python files.
- **Full** (for codebase reviews): Detect all frameworks present in the repository.

### Coding Guidelines Loaded

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

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
(invoked automatically by /adk:code-review-pr, /adk:dev-build, and PR workflows)
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:coding --scope full
/adk:coding --scope scoped
```
