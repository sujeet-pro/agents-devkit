# `docs-publish-confluence` — artifact format

```
.temp/task-<slug>/
├── prompt.txt                       # verbatim user prompt + timestamp
├── source.md                        # copy of the input markdown (for audit)
├── storage.xhtml                    # converted Confluence storage format
├── existence-check.md               # match-by-title-and-parent result
├── publish-plan.md                  # summary of the upcoming write
├── diff.txt                         # (for updates) unified diff old -> new
├── published.md                     # post-publish page metadata
├── validation/
│   └── docs-publish-confluence.md   # per-phase validator log
└── report.md                        # final consolidated report
```

## Slug rules

- `publish-conf-<source-basename>`, e.g.
  `publish-conf-oncall` from `docs/runbooks/oncall.md`.
- If the same slug would collide with a previous run, append
  `-<ISO date>` or a numeric suffix.

## Rules

1. Never write outside `.temp/task-<slug>/` locally. The only remote
   write is the Confluence create/update (and only after the
   ask-once gate).
2. Keep `source.md` as an audit copy — allows the user to compare
   what-we-thought-we-published vs what's on Confluence later.
3. Never include credentials in any artifact. The connector handles
   auth; the skill never sees the token.
4. `diff.txt` format: `diff -u old-storage new-storage`. Useful for
   the `diff` response in the ask-once gate.

## `publish-plan.md` is the canonical pre-write contract

Every field the publish call will send should appear in
`publish-plan.md`. Other artifacts are supplementary evidence. The
validator checks that no field changes between `publish-plan.md`
and the actual connector call.
