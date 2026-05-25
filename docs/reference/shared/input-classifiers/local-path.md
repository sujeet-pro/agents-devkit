---
title: 'input-classifiers/local-path'
description: '- Absolute: `/Users/.../file.py`'
source: 'shared/input-classifiers/local-path.md'
group: 'shared-input-classifiers'
order: 6205
---
# shared/input-classifiers/local-path

> Source: `shared/input-classifiers/local-path.md`

# input classifier: local path

## Patterns

- Absolute: `/Users/.../file.py`
- Relative: `./src/foo.ts`, `src/foo.ts`
- Glob: `src/**/*.py`
- Directory: `services/auth/`
- Special: `.` (current directory)

## Extract into context.md

```markdown
### [local-path] <path>
type: file | dir | glob
resolved: <absolute path>
exists: yes | no
matched files: <N>  (for glob/dir)
language(s): typescript / python / mixed
size summary: <line count, file count>
recent edits (git log -1 per file, top 5): <bullet>
related test files: <list, if any>
```

## Hints

- `/adk-review` with `.`: review the working tree (uncommitted + staged + branch-vs-baseline).
- `/adk-implement` with a dir: the implementation target boundary.
- `/adk-document` with a file/dir: regenerate / refresh docs for that scope.

## Validation

- If the path doesn't exist: ask the user (typo? need to cd?). Don't guess.
- If the path is enormous (> 5000 files / > 500k LOC): warn and ask for a narrower scope.
- If the path is outside the working repo (and outside `$ADK_CONFIG_HOME/`): refuse without explicit confirmation.
