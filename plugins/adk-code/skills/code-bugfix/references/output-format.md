# `code-bugfix` — output format

## Per-turn status

```
[adk-code:code-bugfix] task=<slug> phase=<0|1|2|3|4|5|6> reproducer=<pending|red|green> patch=<pending|applied> regression=<pending|red|green>
```

## `.temp/task-<slug>/reproducer.md` (Phase 2)

```markdown
# Reproducer — <slug>

## Symptom
<one-paragraph description of the bug as observed>

## Pre-conditions / environment
- Repo: <owner/repo>
- Branch: <branch>
- Versions: Node 20.11 / pnpm 9.x / OS macOS 14.5 (or whatever is relevant)
- Inputs / state: <what data / config triggers the bug>

## Failing test
File: `<repo-relative path>`
```ts
it("<behavior-named test>", () => {
  // arrange
  // act
  // assert
});
```

## Failing output (verbatim)
```
<paste the full failing output, truncate to 100 lines if huge>
```

## Notes
<anything unusual: flakiness rate, env-specific, only-on-Sundays, etc.>
```

## `.temp/task-<slug>/plan.md` (Phase 3)

```markdown
# code-bugfix plan — <slug>

## Symptom
<verbatim from reproducer.md>

## Root cause
<one sentence — falsifiable, specific, points at the actual line(s)>

## Why it happened
<2-4 bullets of context: when introduced, why the original code was wrong,
what assumption broke. Not required, but improves the report.>

## Patch
| File | Lines | Action | Why |
| --- | --- | --- | --- |
| src/foo/bar.ts | 47-49 | edit | use `===` instead of `==` so empty string ≠ 0 |

## Regression test
File: <path::test-name>
- (the test from reproducer.md, possibly tightened)

## Validation plan
| Command | Expected exit | Notes |
| --- | --- | --- |
| `<reproducer test>` | 0 | confirm red→green |
| `<full package suite>` | 0 | confirm no regressions |
| `<typecheck>` | 0 | |
| `<lint>` | 0 | |

## Out of scope (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/report.md` (Phase 6)

```markdown
# code-bugfix report — <slug>

## Symptom
<one sentence>

## Root cause
<one sentence — verbatim from plan.md>

## Patch
| File | +N / -M | Why |
| --- | --- | --- |
| src/foo/bar.ts | +1 / -1 | use `===` instead of `==` |

## Regression test
| File | Test name | Red→green |
| --- | --- | --- |
| src/foo/bar.test.ts | "returns wrong value when total is exactly 0" | red on HEAD before patch; green after |

## Validation evidence
| Command | Exit | Notes |
| --- | --- | --- |
| `<reproducer test>` | 0 | green after patch |
| `<full package suite>` | 0 | 187 passed |
| `<typecheck>` | 0 | clean |
| `<lint>` | 0 | clean |
Full logs: `.temp/task-<slug>/validation/per-skill/code-bugfix.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | slug | <slug> | derived from prompt |
| 3 | fix at boundary vs internal | boundary | per AGENTS.md "validate at boundary" rule |

## Residual risk / follow-ups
- <bullet> — <reason>
- Other write-then-cache code paths may have the same race — spawn `/adk-review:audit-repo` scoped to cache patterns.

## NOT done (deliberate)
- <bullet> — <reason>

## Next steps
1. `/adk-review:review-code-changes` before push.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  reproducer.md
  plan.md
  validation/per-skill/code-bugfix.md
  report.md
```

## Hand-off note shape

When `code-bugfix` finishes, end with a 4-line hand-off:

```
Symptom: <one sentence>
Root cause: <one sentence>
Patch: <files>; regression test red→green
Next: /adk-review:review-code-changes <slug>   # before push
```

Plus the offer-depth question.
