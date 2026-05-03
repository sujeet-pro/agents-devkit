# `temp-folder` — output format

## Stdout

Two lines:

```
slug: <slug>
path: /absolute/path/to/.temp/task-<slug>/
```

## Filesystem effect

Unless `--print-only`:

```
.temp/task-<slug>/   (created if missing)
```

No other files are created by this skill. Other skills are responsible for their own artifacts.

## When invoked from another skill

The caller captures the two lines:

```bash
out=$(bin/adk-task-slug "<prompt>")
slug=$(echo "$out" | head -1 | awk '{print $2}')
# (or just use bin/adk-task-slug directly, which prints just the slug)
```

In Node:

```js
const { execSync } = require("node:child_process");
const slug = execSync(`bin/adk-task-slug "${prompt}" --print`).toString().trim();
```

## Documentation rendering

When invoked interactively without `--print-only`, the skill renders:

```markdown
Created workspace:
- slug: <slug>
- path: /absolute/path/to/.temp/task-<slug>/

Layout reference: see ./references/artifact-format.md (in adk-core:auto's references).
```
