# `temp-folder` workflow

## Slug derivation

Implemented in `bin/adk-task-slug`. The algorithm:

1. **Strip URLs.** `https?://[^\s]+` → ` `.
2. **Lowercase.**
3. **Replace non-alphanumeric with spaces.**
4. **Filter common stop-words** (the, a, an, and, or, for, of, in, on, at, to, from, with, by, is, are, was, were, be, been, being, do, does, did, this, that, these, those, it, its, as, into, about, across, against, between, through, that's, i, we, you, they, fix, make, build, write, create, please, can, could, would, should).
5. **Deduplicate** consecutive identical words.
6. **Take the first 6 distinct words**.
7. **Join with `-`.**

If the result is empty, fall back to `task-<YYYYMMDD-HHMMSS>`.

If `--date` is set, prepend `<YYYY-MM-DD>-`.

## Folder creation

Unless `--print-only`:

```bash
mkdir -p ".temp/task-${slug}"
```

Idempotent. Safe to re-run with the same slug.

## Output

```
slug: <slug>
path: /absolute/path/to/.temp/task-<slug>/
```

(also creates the folder unless `--print-only`)

## Integration with other skills

When `auto` (or any other top-level skill) starts a task:

1. Calls `temp-folder` with the user's prompt → gets the slug + path.
2. Writes `.temp/task-<slug>/prompt.txt` with the verbatim prompt.
3. Passes the slug down to every dispatched subagent / skill.
4. Each subagent writes its artifacts under that path.

## Special cases

- **Same prompt re-issued in the same session** → same slug, same folder. Existing artifacts are preserved (downstream skills append or overwrite per their convention).
- **Two different tasks in the same session that produce the same slug** → use `--date` to disambiguate (`2026-05-03-checkout-bug-fix`).
- **Empty prompt** → fall back to date-only slug (`task-20260503-134242`).
