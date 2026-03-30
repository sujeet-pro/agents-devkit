---
name: coding
description: "[helper] [guidelines] Helper skill that detects repo tools, frameworks, and languages, then loads matching coding guidelines from the shared guideline library — invoked by review, PR, and development skills, not directly by users"
user-invocable: false
argument-hint: "[--scope scoped|full] [--help]"
allowed-tools: [Glob, Grep, Read, Bash]
dependencies:
  commands: [git]
workflow-tier: helper
---

# Coding Guidelines Loader

This skill detects the repository's languages, frameworks, and tooling, then loads the matching coding guidelines from `${CLAUDE_SKILL_DIR}/references/coding-guidelines/`. Other skills invoke this before review, fix, or audit work.

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--scope` | `scoped`, `full` | `scoped` | Detection scope: scoped (changed files only) or full (entire repo) |

### Behavior Variations

- **`--scope scoped`** (default for PRs and branch reviews): only detects frameworks relevant to changed files
- **`--scope full`** (for codebase reviews): detects all frameworks present in the repository
- Always loads `general.md` and `architecture.md` guidelines
- Conditionally loads stack-specific guidelines (frontend, backend, language-specific)
- Conditionally loads area-specific guidelines (security, testing, observability, API design)
- Also loads repo-local guidelines (CLAUDE.md, .cursorrules, .editorconfig)

### Examples

```
(invoked automatically by /review, /develop, /pr)
/coding --scope full
/coding --scope scoped
```

---



Load references: `references/workflow-6phase.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`. For Medium/Large: also load `references/agentic-teams.md`, `references/principal-engineer.md`.


## Workflow

This is a helper skill invoked by other skills, not directly by users. It does not own the 6-phase workflow — the invoking skill does.

## Framework Detection

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

## Guideline Loading

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

## Scoped vs Full Detection

- **Scoped** (default for PRs and branch reviews): Only detect frameworks relevant to the changed files. Avoids loading Java guidelines when the PR only touches Python files.
- **Full** (for codebase reviews): Detect all frameworks present in the repository.

## Output

Produce a list of guideline file paths to load. The calling skill reads these files and incorporates the guidelines into its review or fix context.

```text
## Coding Guidelines Loaded

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
