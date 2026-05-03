# `docs-review` — artifact format

```
.temp/task-<slug>/
├── prompt.txt
├── input.md                    # the fetched doc content (non-local targets)
├── claims.md                   # per-claim verification table
├── review.md                   # tiered findings with evidence
├── fixes-applied.md            # (under --fix) applied corrections
├── fixes-deferred.md           # (under --fix) controversial findings
├── backup/
│   └── <target-basename>       # backup before any --fix write
├── validation/
│   └── docs-review.md          # per-phase validator log
└── report.md                   # final consolidated report
```

## Rules

1. Never write to the target doc before `--fix` + validator pass.
2. Always back up the target (to `.temp/task-<slug>/backup/`) before
   the first write.
3. For Confluence / GDoc, `input.md` stores the fetched content in
   markdown-normalized form; the connector-native format (ADF / XHTML
   storage / GDoc ops) lives alongside in `input.raw.json`.
4. `review.md` is the user-facing artifact. `claims.md` is the
   evidence trail.
5. Slug is derived from the target basename (or short URL segment).

## Target-kind handling

| Target kind | `input.md` from | Write-back path |
| --- | --- | --- |
| local md | `Read` on the path | edit in place (under `--fix`) |
| fetched URL | `WebFetch` | no write-back; findings only |
| Confluence | Atlassian connector | connector `update` endpoint (under `--fix`) |
| GDoc | GDrive connector | connector `update` endpoint (under `--fix`) |
