# `docs-publish-gdrive` — artifact format

```
.temp/task-<slug>/
├── prompt.txt                        # verbatim user prompt + timestamp
├── source.md                         # audit copy of the input
├── converted.gdoc.json               # (format=gdoc) ops body
├── converted.md                      # (format=md) stripped md
├── converted.pdf                     # (format=pdf) rendered PDF
├── existence-check.md                # match-by-name-and-parent result
├── publish-plan.md                   # summary of the upcoming write
├── published.md                      # post-publish item metadata
├── sharing-snapshot.md               # pre + post permissions (must match)
├── validation/
│   └── docs-publish-gdrive.md        # per-phase validator log
└── report.md                         # final consolidated report
```

## Slug rules

- `publish-gdrive-<source-basename>`, e.g.
  `publish-gdrive-exports-v1` from `docs/design/exports-v1.md`.
- Collision resolution: append date / numeric suffix.

## Naming in Drive

The target item's name:

- Frontmatter `title:` if present; else first H1; else the
  source-basename (kebab → sentence-cased).
- No extension appended for `--format gdoc` (GDocs don't have
  extensions; they're typed by mime).
- `<name>.md` for `--format md`.
- `<name>.pdf` for `--format pdf`.

## Rules

1. Never write outside `.temp/task-<slug>/` locally.
2. Only one remote write per run (the publish call in Phase 4);
   sharing calls are **forbidden** (per
   `references/sharing-policy.md`).
3. Keep `source.md` for audit — compare later if drift is
   suspected.
4. Never include credentials in any artifact. Connector owns auth.

## `publish-plan.md` must declare no-sharing change

Every plan contains the line:

```
Sharing: will NOT be changed by this skill.
```

Verbatim. It's a machine-grepable invariant that other validators
can check.
