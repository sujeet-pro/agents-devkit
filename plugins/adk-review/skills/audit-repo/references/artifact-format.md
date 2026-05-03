# `audit-repo` — artifact format

## `.temp/reports/audit-<slug>(-evidence)/` canonical layout

```
.temp/reports/
├── audit-<slug>.md                                  # the canonical full report
└── audit-<slug>-evidence/
    ├── inventory.md                                 # repo inventory (Phase 2)
    ├── security.md                                  # per-dimension report
    ├── performance.md
    ├── quality.md
    ├── deps.md
    ├── test-coverage.md
    ├── architecture.md
    ├── healthy.md                                   # "what's healthy" assembly across dimensions
    ├── methodology.md                               # what was/wasn't covered; tools; time
    └── per-finding/
        ├── sec-001-admin-role-check.md
        ├── perf-001-n-plus-one-orders.md
        ├── quality-001-god-class-calculator.md
        └── ...                                      # per-finding deep evidence (when needed)
```

## Why `.temp/reports/`, not `.temp/task-<slug>/`

Audits are repo-wide point-in-time snapshots, NOT task-tied work. A task is "fix the bug where checkout times out" (single user goal); an audit is "what's the state of acme/checkout-api" (an evaluation).

Per `/adk-core:auto` `references/artifact-format.md`:

> | `.temp/reports/<slug>.md` | Reviews, audits, investigations not tied to a task |

`audit-repo` writes to `.temp/reports/` so audits can be diffed across runs without overlapping with task artifacts.

## Slug convention

`audit-<repo-name>-<YYYY-MM-DD>` — date-stamped because audits are point-in-time. Re-running tomorrow produces a different slug; the user can `diff` two reports to see what changed.

For same-day re-runs:

- The prior `audit-<slug>.md` is moved to `.archive/<iso-ts>/audit-<slug>.md`.
- The new run writes a fresh `audit-<slug>.md`.

For different-day re-runs:

- Both reports coexist (different slugs).
- The user can `diff` `.temp/reports/audit-<repo>-2026-05-03.md` `.temp/reports/audit-<repo>-2026-05-10.md`.

## File-by-file purpose

| File | Lifecycle | Used by |
| --- | --- | --- |
| `audit-<slug>.md` | Phase 6 (write-once; archive prior on same-day re-run) | the report deliverable; user reads this |
| `audit-<slug>-evidence/inventory.md` | Phase 2 (write-once) | informs all dimension passes |
| `audit-<slug>-evidence/<dimension>.md` | Phase 3 (per-dimension write-once) | input to aggregation (Phase 4) |
| `audit-<slug>-evidence/healthy.md` | Phase 4 (write-once after aggregation) | Section 4 of the full report |
| `audit-<slug>-evidence/methodology.md` | Phase 6 (write at end) | Section 6 of the full report |
| `audit-<slug>-evidence/per-finding/<id>.md` | Phase 3-4 (write per-finding when needed) | linked from Top-10 + per-dimension tables |

## Naming conventions

- **Slug:** `audit-<repo-name>-<YYYY-MM-DD>` (date-stamped).
- **Per-finding file IDs:** `<dimension-prefix>-<seq>-<short-name>.md`. Prefixes:
  - `sec-` for security
  - `perf-` for performance
  - `quality-` for quality
  - `deps-` for dependencies
  - `test-` for test-coverage
  - `arch-` for architecture
- **Sequence number:** `001`, `002`, `003`, ... per-dimension.
- **Short name:** kebab-case derived from the finding's one-line summary.

Examples: `sec-001-admin-role-check.md`, `perf-001-n-plus-one-orders.md`, `arch-001-cyclic-dep-services.md`.

## Rules

1. **Read-only on the repo.** Never modifies any source file; never modifies anything written by another skill.
2. **Never writes outside `.temp/reports/audit-<slug>(-evidence)/`.**
3. **Same-day re-runs archive the prior report.** Different-day re-runs coexist (different slugs).
4. **`.temp/` is in `.gitignore`** at the repo root. Verify before any write.
5. **All findings include file-anchored evidence.** Every finding has a file:line range and a ≤15-word verbatim quote. No "the auth module looks suspicious".
6. **Anonymize secrets / PII.** Security findings name type + file:line; never the bytes. Customer data is anonymized.
7. **Per-finding deep evidence is OPTIONAL.** Only the findings warranting longer exhibits (long tool outputs, dep-tree dumps, code excerpts) get a per-finding file. Top-10 cards in the main report are sufficient for most.
8. **All MD files include an ISO timestamp** in the first line.

## Cross-reference: how this differs from `audit-pr` artifact format

| Aspect | `audit-pr` | `audit-repo` |
| --- | --- | --- |
| Output location | `.temp/task-<slug>/audit/` | `.temp/reports/audit-<slug>(-evidence)/` |
| Slug | `audit-<repo>-pr-<num>` | `audit-<repo>-<YYYY-MM-DD>` |
| Verdict model | Pass/Warn/Fail per check | severity-tiered findings |
| Per-check files | yes (one per check, fixed 10) | NO; instead per-dimension files (6) + per-finding (variable) |
| `inventory.md` | NO (PR scope is the diff) | YES (whole-repo scope requires inventory) |
| `healthy.md` | NO | YES (required) |
| `methodology.md` | NO (workflow is fixed) | YES (variable scope; coverage report) |
| `--fix` | yes (safely-fixable subset) | NEVER (read-only) |
| Comment posting | `--post-comment` opt-in | NEVER (read-only) |

## Validation log

Per the universal contract, this skill writes a validator log to:

```
.temp/reports/audit-<slug>-evidence/validator.md
```

(NOT `.temp/task-<slug>/validation/per-skill/audit-repo.md` — because there's no task slug for an audit.)

The validator log records each phase's checks (per `references/validator.md`).
