---
title: Edit format
description: SEARCH/REPLACE block discipline for /adk-implement — inspired by Aider's diff edit-format. Prevents whole-file rewrites and silent regressions.
order: 10
---

# Edit format (SEARCH/REPLACE blocks)

Inspired by Aider's `diff` edit-format. Used by `adk-agent-implementer` for every file mutation in `/adk-implement`.

Source: `shared/edit-format.md`.

## Why

Without explicit edit-format discipline, models silently regress to whole-file rewrites. That:

- Bloats diffs (1000-line file replaced when 5 lines changed).
- Burns tokens (re-emit content that already exists).
- Hides intent (review now means re-reading the whole file).
- Breaks the "smallest correct change" principle.

SEARCH/REPLACE blocks force the model to name the exact lines being changed.

## Format

```text
path/to/file.py
<<<<<<< SEARCH
def existing_function(x):
    return x + 1
=======
def existing_function(x: int) -> int:
    """Return x incremented by one."""
    return x + 1
>>>>>>> REPLACE
```

**Rules:**

1. **File path** = first non-empty line. Repository-relative; no leading `./`. No absolute paths.
2. **SEARCH** = EXACT current text, byte-for-byte, including whitespace and surrounding context. Min 1 line, max ~40 lines. No paraphrase, no `…` elision.
3. **REPLACE** = EXACT new text. Empty replace = deletion. Empty search + new file = insertion at file start.
4. **Markers** are literal: `<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE` (7 angle brackets, 7 equals signs).
5. **One block per logical change.** Three regions in one file → three blocks (same path repeated).
6. **Anchor enough context** so SEARCH is unique within the file.

## New files

Empty SEARCH section:

```text
path/to/new-file.py
<<<<<<< SEARCH
=======
"""new module."""

def hello():
    return "world"
>>>>>>> REPLACE
```

## Deletions

Empty REPLACE:

```text
path/to/file.py
<<<<<<< SEARCH
def deprecated_function():
    return None
=======
>>>>>>> REPLACE
```

Whole-file removal uses `rm <path>` (logged separately, not via block).

## Renames

Two operations: delete-block on old path + create-block on new path. Don't try to express a rename as one block.

## Pre-edit verification (the implementer does this)

Before emitting a block, the implementer:

1. **Has Read the file in this session** (constitution §V).
2. **Verifies SEARCH is exactly current.** If a previous edit changed the region, re-Read first.
3. **Verifies SEARCH is unique** in the file. If not, expands context until unique.

If any verification fails, the implementer stops and reports — does not silently retry.

## Apply step

The skill's runtime apply step:

1. Validates each block against actual file content.
2. On any mismatch: stops, surfaces the diff, asks user to confirm or abort.
3. On match: applies via the agent's `Edit` tool.
4. Each applied block produces one entry in `<task-slug>/diffs/applied.jsonl` for traceability.

## Anti-patterns

- **Whole-file replace** when one block changed — forbidden, defeats the discipline.
- **Paraphrased search** ("change the function to add types") — forbidden.
- **Search with `…` elision** — forbidden; must be byte-exact.
- **Multiple files in one block** — forbidden.
- **Search that matches multiple locations** — forbidden; disambiguate.

## Why this format specifically

- **Smaller diffs than whole-file.** Same edit, 1/20th the tokens for a 200-line file.
- **Catches drift.** If the model "remembers" the file differently from disk, validation fails immediately rather than overwriting work.
- **Reviewable.** A human can read the block in seconds and know exactly what changed.
- **Composable.** Multiple blocks in one report are independently apply-able and individually revertible.

## Next

- [Plan/Act mode](./plan-act-mode.md) — when the implementer is allowed to emit blocks
- [Hooks](./hooks.md) — what catches block-format violations
