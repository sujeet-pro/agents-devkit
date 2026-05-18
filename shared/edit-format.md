# shared/edit-format.md — canonical edit format for `/adk-implement`

> Inspired by Aider's `diff` edit-format. Used by `adk-agent-implementer` for every file mutation. Prevents whole-file rewrites and silent regressions.

## Format

Every code edit is a **SEARCH/REPLACE block** anchored to a specific file path.

```
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

1. **File path** is the first non-empty line of the block. Repository-relative; no leading `./`. Absolute paths are forbidden.
2. **`SEARCH` section** contains the EXACT current text, byte-for-byte, including whitespace and surrounding context. Minimum 1 line, maximum ~40 lines. No paraphrase, no "…" elision, no comments-explaining-edits.
3. **`REPLACE` section** contains the EXACT new text. Empty replace = deletion. Empty search = insertion at file start (requires the file to be new or the location to be unambiguous; otherwise use an anchored search).
4. **Markers** are literal: `<<<<<<< SEARCH`, `=======`, `>>>>>>> REPLACE`. Exactly 7 angle brackets, 7 equals signs.
5. **One block per logical change.** If you're touching three regions in one file, emit three blocks (same path repeated). Don't merge.
6. **Anchor enough context** so the search is unique within the file. If the file has two `def existing_function` definitions, include the class name or surrounding line that disambiguates. The implementer must verify uniqueness BEFORE writing the block.

## New files

For a new file, use an empty SEARCH:

```
path/to/new-file.py
<<<<<<< SEARCH
=======
"""new module."""

def hello():
    return "world"
>>>>>>> REPLACE
```

The implementer's tool then creates the file with the REPLACE content.

## Deletions

For a deletion, use an empty REPLACE:

```
path/to/file.py
<<<<<<< SEARCH
def deprecated_function():
    return None
=======
>>>>>>> REPLACE
```

If you're removing an entire file, the implementer uses `rm <path>` (logged separately, not via block).

## Renames

Two operations: a delete-block on the old path + a create-block on the new path. Don't try to express a rename as a single block.

## Anti-patterns

- **Whole-file replace** when one block changed. Forbidden — defeats the discipline.
- **Paraphrased search** ("change the function to add types"). Forbidden — the implementer can't apply a vague search.
- **Search with `...` elision**. Forbidden — must be byte-exact.
- **Multiple files in one block.** Forbidden — one block, one file.
- **Search that matches multiple locations.** Forbidden — disambiguate with context.
- **Trailing newline mismatch.** The implementer's apply step must respect the file's trailing-newline convention; the model is expected to preserve it.

## Pre-edit verification (the implementer does this, NOT the human)

Before emitting a block, the implementer must:

1. **Have Read the file in this session.** Constitution §V; non-negotiable.
2. **Verify the SEARCH is exactly current.** If a previous edit in this session changed the relevant region, re-Read first.
3. **Verify SEARCH is unique in the file.** If not, add surrounding context until unique.

If any verification fails, the implementer stops and reports — not silently retries.

## Output channel

SEARCH/REPLACE blocks are emitted by the implementer agent. The skill's runtime apply step:

1. Validates each block against the actual file content.
2. On any mismatch: stop, surface the diff, ask user to confirm or abort.
3. On match: apply via `Edit` tool.
4. Each applied block produces one entry in `<task-slug>/diffs/applied.jsonl` for traceability.

## Why this format

- **Smaller diffs than whole-file.** Same edit, 1/20th the tokens for a 200-line file.
- **Catches drift.** If the model "remembers" file content differently from disk, validation fails immediately rather than overwriting the user's work.
- **Reviewable.** A human can read the block in seconds and know exactly what changed.
- **Composable.** Multiple blocks in one report are independently apply-able and individually revertible.
