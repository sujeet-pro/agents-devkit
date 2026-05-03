# `docs-changelog` — artifact format

```
.temp/task-<slug>/
├── prompt.txt               # verbatim user prompt + timestamp
├── commits.txt              # git log <from>..<to> (unit-separated)
├── detected-style.txt       # kaC | semantic | free + confidence + evidence
├── classified.md            # commit -> group + user-readable draft + PR ref
├── changelog-entry.md       # the block to insert
├── backup/
│   └── CHANGELOG.md         # pre-write backup (only under --fix)
├── validation/
│   └── docs-changelog.md    # per-phase validator log
└── report.md                # final consolidated report
```

## Slug rules

- `changelog-<to-tag-normalized>`, e.g.
  - `v1.2.0` → `changelog-v1-2-0`
  - `HEAD` → `changelog-head-<date>` (date-prefix for disambiguation)
- If the same slug would collide with a previous run, add a `-N`
  suffix (`changelog-v1-2-0-2`).

## `classified.md` format

```markdown
# classified — <slug>

| SHA (short) | Subject | Group (kaC) | Breaking? | PR | Draft entry |
| --- | --- | --- | --- | --- | --- |
| a1b2c3d | feat(orders): partial-refund hook | Added | no | #2840 | Adds support for partial refunds on gift orders. |
| b2c3d4e | fix(checkout): clamp add-to-cart qty | Fixed | no | #2841 | Clamps add-to-cart quantity to current inventory. |
| c3d4e5f | feat!: remove legacyLogin | Breaking changes | yes | #2901 | `AuthClient.legacyLogin()` is removed; migrate to `loginWithOidc()`. |
```

## Rules

1. Never write outside `.temp/task-<slug>/` or `CHANGELOG.md` (and
   `CHANGELOG.md` only under `--fix`).
2. `backup/CHANGELOG.md` is made before the first `--fix` write.
3. The validator preserves exact byte-level structure of the
   existing file outside the insertion point (leading whitespace,
   code fences, footnote definitions, etc.).
4. `detected-style.txt` is machine-readable; other skills can
   consume it if needed.
