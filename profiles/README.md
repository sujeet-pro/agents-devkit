# Profiles

Profiles determine how claude-devkit adapts its behavior based on the type of repository being worked on.

## How It Works

The profiles system has two components:

1. **Detection** (`detect.md`): Rules for automatically identifying what kind of repo you are in (design system, frontend, library, backend, scripts, etc.) based on file patterns, package.json fields, and directory structure.

2. **Tag overrides**: Explicit tags like `[ds]`, `[fe]`, `[lib]`, `[be]`, or `[script]` placed in PR titles or descriptions to override auto-detection.

## What Profiles Control

Once a repo type is identified, the profile influences:

- Which **guidelines** are loaded for PR reviews and code generation
- Which **repo-config CLAUDE.md** template is suggested for new repos
- What **context instructions** are added to the session

## Files

- `detect.md` — Full detection rules, heuristics, and tag definitions
- `README.md` — This file

## Adding a New Profile Type

1. Add detection heuristics to `detect.md` under a new heading.
2. Assign a tag (e.g., `[mobile]`).
3. Create a corresponding `repo-configs/<type>/CLAUDE.md` template.
4. Optionally add guidelines under `guidelines/` that are specific to the new type.
