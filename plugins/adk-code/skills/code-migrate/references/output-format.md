# `code-migrate` — output format

## Per-turn status

```
[adk-code:code-migrate] task=<slug> phase=<0|1|2|3|4|5|6|7> from=<X> to=<Y> groups=<done>/<total> validation=<green|red>
```

## `.temp/task-<slug>/migration-notes.md` (Phase 2)

```markdown
# Migration notes — <from> → <to>

## Source
- Official guide: <URL>
- Fetched: <ISO timestamp>
- Version observed: <Y> stable / RC / etc.

## Breaking changes (required)
### 1. <rule name>
- Source URL: <link>
- Quote (≤15 words): "<verbatim quote>"
- What it means: <one-paragraph plain-English summary>
- Applies to our codebase: yes / partial / no — <one-line evidence>

### 2. <rule name>
…

## Recommended changes (optional)
### A. <rule name>
- Source URL: <link>
- Quote (≤15 words): "<verbatim quote>"
- Reason for / against adopting: <one-paragraph>

## Decision
- Adopt: rules <list>
- Skip: rules <list> (reasons in inventory + plan)
```

## `.temp/task-<slug>/migration-inventory.md` (Phase 3)

```markdown
# Inventory — <from> → <to>

## Per-rule call-site count

| Rule | Pattern (regex / AST) | Files | Sites |
| --- | --- | --- | --- |
| useRef requires init | `useRef\(\s*\)` | 23 | 31 |
| Context.Provider → Context | `<\w+\.Provider` | 11 | 38 |
| Legacy refs removed | `findDOMNode\|string-ref` | 3 | 3 |

## Sample sites (for the implementer to anchor on)

### useRef requires init
- src/components/Foo.tsx:42 — `const r = useRef()`
- src/hooks/useFoo.ts:18 — `const r = useRef<HTMLDivElement>()`
- src/lib/refs.ts:7 — `const r = useRef()`

### Context.Provider → Context
…
```

## `.temp/task-<slug>/plan.md` (Phase 4)

```markdown
# code-migrate plan — <slug>

## Migration
From: <X> → To: <Y>
Repo: <owner/repo>
Scope: <subtree, if --scope, else "whole repo">

## Groups
| # | Name | Files | Strategy | Validation |
| --- | --- | --- | --- | --- |
| 1 | <name> | N | mechanical / manual / config | typecheck + tests scoped to changed files |
| 2 | <name> | N | mechanical | typecheck + tests scoped |
| Z | bump dependency version | 1 | last | full validation |

## Validation plan (final)
| Command | Expected exit | Notes |
| --- | --- | --- |
| `<full build>` | 0 | mandatory for migrations |
| `<full test>` | 0 | full suite |
| `<typecheck>` | 0 | full |
| `<lint>` | 0 | full |
| `<smoke check>` | 0 | per migration type |

## Items NOT applied
| Rule | Reason | Follow-up |
| --- | --- | --- |
| <rule> | recommended-but-optional; out of scope for this task | spawn /adk-code:code-write later |

## Out of scope (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/report.md` (Phase 7)

```markdown
# code-migrate report — <slug>

## Migration
From: <X> → To: <Y>
Repo: <owner/repo>
Scope: <subtree>

## Files changed
| Path | +N / -M | Role |
| --- | --- | --- |
| package.json | +1 / -1 | bumped react / react-dom |
| src/.../Foo.tsx | +2 / -2 | Context.Provider → Context |
… (truncate to top 20 if >20; full list in validation log)

Total files changed: <N>
Total +N: <sum>
Total -M: <sum>

## Groups applied
| # | Name | Files | Status |
| --- | --- | --- | --- |
| 1 | useRef init values | 23 | applied; tests green |
| 2 | Context.Provider → Context | 11 | applied; tests green |
…

## Migration guide rules applied
| Rule | Quote (≤15 words) | Files |
| --- | --- | --- |
| useRef requires init | "useRef must be called with one argument" | 23 |
| Context bare component | "context can render directly: <Context value={...}>" | 11 |

## Migration guide rules NOT applied
| Rule | Reason | Follow-up |
| --- | --- | --- |
| Adopt the new use() hook | optional; out of scope | follow-up code-write task |

## Validation evidence (final)
| Command | Exit | Notes |
| --- | --- | --- |
| `<build>` | 0 | clean |
| `<test>` | 0 | 1,247 passed (matches baseline) |
| `<typecheck>` | 0 | clean |
| `<lint>` | 0 | clean |
| `<smoke check>` | 0 | dev server starts; HMR works |
Full logs: `.temp/task-<slug>/validation/per-skill/code-migrate.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | from / to versions | 18.2.0 → 19.0.0 | resolved via package.json + WebFetch |
| 4 | group order | useRef → Context → legacy refs → version bump | low-blast-radius first |

## Residual risk / follow-ups
- <bullet> — <reason>
- New use() hook recommended but not adopted — follow-up code-write task.

## NOT done (deliberate)
- <bullet> — <reason>

## Next steps
1. `/adk-review:review-code-changes` before push.
2. (optional) follow-up `code-write` to adopt new APIs.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  migration-notes.md
  migration-inventory.md
  plan.md
  validation/per-skill/code-migrate.md
  report.md
```
