# `review-handoff` — artifact format

## `.temp/task-<slug>/` canonical layout

```
.temp/task-<slug>/
├── prompt.txt                              # written by the original skill (review-handoff doesn't author this)
├── ... (artifacts from the prior skill chain — review-handoff READS these) ...
├── handoff.md                              # written by review-handoff (Phase 3)
├── handoff-postback.md                     # written by review-handoff (Phase 5; only if --post-to ran)
├── .archive/<iso-ts>/                      # prior handoff.md(s) moved here on re-run
│   └── handoff.md
├── validation/
│   └── per-skill/
│       └── review-handoff.md               # per-phase validator log
└── report.md                               # written by review-handoff (Phase 6; pointer to handoff.md)
```

## File-by-file purpose

| File | Author | Lifecycle |
| --- | --- | --- |
| `prompt.txt` | ORIGINAL skill (not review-handoff) | read-only here |
| Other prior artifacts | their respective skills | read-only here |
| `handoff.md` | review-handoff | written Phase 3; on re-run, prior is moved to `.archive/<iso-ts>/` first |
| `handoff-postback.md` | review-handoff | Phase 5 only when `--post-to` set |
| `validation/per-skill/review-handoff.md` | review-handoff | append per phase boundary |
| `report.md` | review-handoff | Phase 6; pointer (the handoff IS the deliverable) |

## Naming conventions

- **Slug:** inherited from the prior skill chain (review-handoff doesn't generate a new slug).
- **`.archive/`** subfolder per re-run, keyed by ISO timestamp (`.archive/2026-05-03T18-42Z/`).
- **`handoff.md` is THE handoff.** No fancy naming; readers know to look here.

## Rules

1. **Read-only on prior artifacts.** Never modifies anything written by other skills.
2. **Never writes outside `.temp/task-<slug>/`** unless `--post-to` is set (in which case the post writes to Slack / Jira / GitHub).
3. **Re-runs don't overwrite `handoff.md`.** Always archive first.
4. **`.temp/` is in `.gitignore`** at the repo root.
5. **Anonymizes env-var values** before writing. Names only.
6. **Truncates the uncommitted diff** in `handoff.md` to 200 lines (or omits if >500 lines, replaced with a reference to `git diff`).
7. **Slack-friendly truncation** for `--post-to slack` is per `references/output-format.md`'s Slack-friendly mode.
8. **POST-CONFIRMATION re-fetch** for `--post-to pr` per `/adk-review:review-pr` `references/post-confirmation.md`.

## Cross-reference: how this differs from other review-* artifact formats

| Aspect | Other review-* | `review-handoff` |
| --- | --- | --- |
| Authors `findings.md` | yes | NO |
| Authors `classification.md` | review-feedback only | NO |
| Authors `postback.md` | review-pr / review-feedback | only `handoff-postback.md` (if `--post-to` set) |
| Reads `.temp/task-<slug>/` wholesale | partial (each skill writes its own) | yes (the WHOLE skill is reading and synthesizing) |
| Writes outside `.temp/task-<slug>/` | only with `--fix` | only with `--post-to` (and goes to a remote service, not the filesystem) |
| Has `.archive/` discipline | yes (review-pr archives prior receipts) | yes (handoff.md is the durable artifact; archive on re-run) |
