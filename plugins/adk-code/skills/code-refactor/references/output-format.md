# `code-refactor` — output format

## Per-turn status

```
[adk-code:code-refactor] task=<slug> phase=<0|1|2|3|4|5|6> microsteps=<done>/<total> validation=<green|red>
```

## `.temp/task-<slug>/plan.md` (Phase 3)

```markdown
# code-refactor plan — <slug>

## Move
<one sentence — extract / rename / dedupe / split / inline / move>

## Scope
- Repo: <owner/repo>
- Branch: <branch>
- Files affected: <count> (<created/edited/deleted breakdown>)
- Call-site count (for renames / extractions): <count>
- Subtree (if --scope): <path>

## Existing test coverage
<one paragraph: which tests cover the affected behavior; whether
coverage is adequate or thin. If thin, recommend code-test as a
prerequisite.>

## Micro-steps
1. <step 1 — leaves suite green>
2. <step 2 — leaves suite green>
3. <step 3 — leaves suite green>
…

## Validation plan
| Command | Expected exit | Notes |
| --- | --- | --- |
| `<typecheck>` | 0 | full package |
| `<lint>` | 0 | |
| `<test>` | 0 | scoped |

## Out of scope (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/report.md` (Phase 6)

```markdown
# code-refactor report — <slug>

## Move
<one sentence>

## Files changed
| Path | +N / -M | Role |
| --- | --- | --- |
| services/cart/validate.ts | +47 / -0 | created (extracted from checkout.ts) |
| services/checkout/checkout.ts | +1 / -47 | edited (delete + import from new path) |
| tests/checkout.test.ts | +1 / -1 | edited (import path updated) |

## Micro-steps
| # | Description | Suite size after | Exit |
| --- | --- | --- | --- |
| 1 | Create services/cart/validate.ts (cut-paste; alias in checkout.ts) | 187 | 0 |
| 2 | Update checkout.ts to import from new path; delete alias | 187 | 0 |
| 3 | Move 4 tests to services/cart/validate.test.ts | 187 | 0 |

## Validation evidence (final state)
| Command | Exit | Notes |
| --- | --- | --- |
| `<typecheck>` | 0 | clean |
| `<lint>` | 0 | clean |
| `<test>` | 0 | 187 passed (same count as baseline) |
Full logs: `.temp/task-<slug>/validation/per-skill/code-refactor.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | slug | <slug> | derived from move + area |
| 3 | extract vs full dedupe | extract common core | full dedupe would change input acceptance — behavior change |

## Residual risk / follow-ups
- <bullet> — <reason>

## NOT done (deliberate)
- <bullet> — <reason>

## Next steps
1. `/adk-review:review-code-changes` before push.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  plan.md
  validation/per-skill/code-refactor.md
  report.md
```

## Hand-off note shape

```
Move: <one sentence>
Micro-steps: <N> done; suite green at every step (count <count>)
Next: /adk-review:review-code-changes <slug>   # before push
```

Plus the offer-depth question.
