# `config-update` — output format

Stdout report (always). Under `--auto`, also `.temp/config-update-report.md` (gitignored).

## Header

```
[adk-core:config-update] target=<all|topic> mode=<auto|interactive> fix=<yes|no> since=<duration|defaults>
```

## Per-topic block

Three states a topic can be in:

### State 1 — refreshable, has changes

```
<topic>.md
  source: <source-name>                                                  reachable
  current entries: <N> <kind1>, <M> <kind2>
  code refs scanned in: <repo1>, <repo2>, ...
  proposed changes:
    + <field>.<entry>                                                    provenance: <source-query>
                                                                          code-confirmed: <yes|NO|n/a>
    ~ <field>.<entry> → <new-value> (was <old-value>)                    provenance: <reason>
    - <field>.<entry>                                                    proposed removal: <reason>
  code-confirmation rate: <found>/<total> (<pct>%)
  apply? <"applied (validated)" | "not under --fix; re-run with --fix to write." | "skipped by user">
```

### State 2 — refreshable, no changes

```
<topic>.md  no changes proposed (current entries match <source>)
```

### State 3 — unreachable

```
<topic>.md   skipped: source unreachable (<short reason>)
```

### State 4 — not refreshable by this skill

```
<topic>.md   not refreshable by this skill (<one-line reason>)
```

The `not refreshable` line is printed for `info`, `slack`, `review`, `docs` so the user knows they were considered, not forgotten.

## Symbols

- `+ <entry>` — proposed addition.
- `~ <entry>` — proposed change (value differs between source and config).
- `- <entry>` — proposed removal (only displayed; never auto-applied without per-removal confirmation).

## Annotations

- `provenance:` — the source query / reason that surfaced this change. The user must be able to follow the chain back to the source.
- `code-confirmed: yes` — the entry name was found via `rg --fixed-strings` in at least one configured repo path.
- `code-confirmed: NO` — not found; flagged as low confidence in the report.
- `code-confirmed: n/a` — cross-reference doesn't apply (e.g. for repos.md, dashboards).

## Doctor footer

```
doctor: <N> warnings, <M> errors
  - <warning or error description, one per line>
```

Examples:
- `mixpanel.md skipped — workspace mixpanel connector unreachable` (warning)
- `~/.config/adk/datadog.md failed --check before refresh; refused to update` (error)

## Next-steps footer

A short bulleted list. Common next steps:
- "Re-run with `--fix` to apply proposed changes after review."
- "Investigate `<entry>` (in source but not referenced in code)."
- "Either clone `<missing-repo>` into `~/code/<org>/` or skip the addition."
- "Source `<X>` was unreachable — check workspace connector status and re-run."

## Status legend

- `reachable` — smoke-ping succeeded.
- `unreachable` — smoke-ping failed; topic skipped.
- `applied (validated)` — file was written and post-write `--check` passed.
- `restored` — file was written but post-write `--check` failed; original restored from in-memory backup.
- `not refreshable` — topic is preference-driven (`info`, `slack`, `review`, `docs`); skill doesn't touch.

## Why the verbose format

Drift is silent until something breaks. The verbose per-line provenance lets the user audit the proposed change before accepting it — "why did the skill think this should be added?" must be answerable from the report alone, without re-running the source query manually.

## Doctor counts

- `errors` — anything that BLOCKED a topic refresh (current file failed `--check`; post-write validation failed and original was restored).
- `warnings` — anything DEGRADED (source unreachable; low-confidence additions flagged; user-rejected removal that the skill thinks is still stale).
