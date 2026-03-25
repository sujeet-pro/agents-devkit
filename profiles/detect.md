# Repo Type Detection Rules

This document defines how to automatically detect what type of repository you are working in. Detection is used to apply the correct guidelines, review standards, and CLAUDE.md templates.

## Detection Order

1. **Explicit tag override** (highest priority) — check PR title/description for tags
2. **File-based heuristics** — inspect the repo's files and configuration

If multiple heuristics match, prefer the most specific one (e.g., "design system" over "library").

---

## Repo Types and Detection Heuristics

### Design System

A repository containing UI component libraries, design tokens, or design primitives.

**Detect when any of the following are true:**
- Has a `design-tokens/` directory
- Has a `packages/` directory containing subdirectories named `tokens`, `primitives`, `components`, `icons`, or `themes`
- `package.json` contains keywords like `"design-system"`, `"component-library"`, `"design-tokens"`, or `"ui-kit"`
- `package.json` `name` field contains `design-system`, `ds-`, or `-ds`
- Has a `.storybook/` directory AND a `packages/` directory (monorepo with Storybook)

**Tag:** `[ds]`

### Frontend Next.js

A web application built with Next.js.

**Detect when:**
- `package.json` has `next` as a dependency or devDependency
- Has a `next.config.js`, `next.config.mjs`, or `next.config.ts` file
- Has an `app/` or `pages/` directory alongside a `package.json` with `next`

**Tag:** `[fe]`

### JS/TS Library

A JavaScript or TypeScript package intended for consumption by other packages (not an application).

**Detect when:**
- `package.json` has a `main`, `module`, or `exports` field
- Has a `tsconfig.json`
- Does NOT have framework dependencies (`next`, `react-scripts`, `vue`, `angular`, `svelte`)
- OR has a `rollup.config.*`, `tsup.config.*`, or `vite.config.*` with `lib` mode

**Tag:** `[lib]`

### Backend Java

A Java or Kotlin backend service.

**Detect when:**
- Has a `pom.xml` file (Maven)
- Has a `build.gradle` or `build.gradle.kts` file (Gradle)
- Has a `src/main/java/` directory structure

**Tag:** `[be]`

### Backend Python

A Python backend service or application.

**Detect when:**
- Has a `requirements.txt` file
- Has a `pyproject.toml` file
- Has a `setup.py` or `setup.cfg` file
- Has a `Pipfile`
- Has a `manage.py` file (Django)

**Tag:** `[be]`

### Scripts

A repository or directory containing primarily utility scripts.

**Detect when:**
- The majority of files are `.sh`, `.py`, or `.js` files
- There is no `package.json`, `pom.xml`, `build.gradle`, `requirements.txt`, or `pyproject.toml`
- May have a `Makefile` but no other build system

**Tag:** `[script]`

### Default

Anything that does not match the above categories.

**Tag:** none (no tag needed)

---

## Tag System for PR Reviews

Tags can be placed in the PR title or description to explicitly specify the repo type. Tags override auto-detection.

### Supported Tags

| Tag        | Repo Type         |
|------------|-------------------|
| `[ds]`     | Design System     |
| `[lib]`    | JS/TS Library     |
| `[fe]`     | Frontend Next.js  |
| `[be]`     | Backend           |
| `[script]` | Scripts           |

### Tag Placement

Tags can appear in:
- **PR title**: `[ds] Add new color tokens for dark mode`
- **PR description**: first line or anywhere in the body, e.g., `Type: [ds]`

### Tag Behavior

- If a tag is present, it takes priority over file-based detection.
- If multiple tags are present, the first one encountered is used.
- Tags are case-insensitive: `[DS]`, `[ds]`, and `[Ds]` are all equivalent.
- If no tag is present and auto-detection fails, the `default` profile is used.

---

## Using Detection Results

Once a repo type is detected:

1. **PR Reviews**: Load the corresponding guidelines from `skills/_references/guidelines/` for the detected type.
2. **Repo Config**: Suggest the appropriate `repo-configs/<type>/CLAUDE.md` if the repo lacks one.
3. **Context**: Add type-specific context instructions for the session.
