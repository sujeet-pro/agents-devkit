# `docs-write` — artifact format

Canonical `.temp/task-<slug>/` layout (per `adk-core:temp-folder`).

```
.temp/task-<slug>/
├── prompt.txt                   # verbatim user prompt + ISO timestamp
├── sources.md                   # evidence map: claim → file:line
├── draft.md                     # the drafted doc with inline citations +
│                                # <!-- validation --> block at the end
├── validation/
│   └── docs-write.md            # per-phase validator log
└── report.md                    # final consolidated report
```

## Canonical target paths (under `--fix`)

| Doc type | Default path | Source of default |
| --- | --- | --- |
| README | `README.md` at repo root | inferred |
| nested README | `<subservice>/README.md` | inferred from `--scope` |
| ADR | `<adr_path>/NNNN-<slug>.md` | `docs.md.adr_path` (default `docs/adr/`) |
| runbook | `<runbook_path>/<slug>.md` | `docs.md.runbook_path` (default `docs/runbooks/`) |
| migration guide | `docs/migrations/<from>-to-<to>.md` | inferred |
| API reference | `docs/api/<subject>.md` | inferred |
| free-form | `.temp/task-<slug>/draft.md` only | (not promoted under --fix) |

## Slug rules

1. Kebab-case; 3-6 words. Derived from the prompt's nouns + verbs.
2. ADR slugs get the zero-padded number prefix under `--fix`:
   `adr-0007-oidc-service-to-service` → target `docs/adr/0007-oidc-service-to-service.md`.
3. Date prefix only when disambiguation is needed (e.g. two runbook
   drafts in the same session).

## Rules

1. Never write outside `.temp/task-<slug>/` before the validator passes.
2. `.temp/` is in `.gitignore` at repo root. Verify before first write.
3. On `--fix`, write only to the target canonical path. Do not touch
   other files (no drive-by edits to README when writing an ADR).
4. Staging is done via `git add <path>`; never `git commit` or
   `git push` from this skill.
5. Existing canonical path is backed up to
   `.temp/task-<slug>/backup/<basename>` before overwrite — lets the
   user compare / revert.
