# `auto` — output format

## Per-phase status (each turn opens with this)

```
[adk:auto] task=<slug> phase=<A|B|C|D1|D2|D3> status=<in-progress|blocked|done> mode=auto auto-flag=<on|off>
```

## Final report (Phase D3 done)

Written to `.temp/task-<slug>/report.md`:

```markdown
# auto report — <slug>

## Result
<one sentence of what was delivered>

## Decisions
| Phase | Question | Picked | Rationale |
|-------|----------|--------|-----------|
| A     | ...      | ...    | ...       |
| B     | ...      | ...    | ...       |
| C     | ...      | ...    | ...       |

## Skills run
- `<skill>` — `<artifact path>` — status: <ok|warn|fail>
- ...

## Validation evidence
- Local: <link to .temp/task-<slug>/validation/d1.md>
- Browser: <link to .temp/task-<slug>/browser-validation/...> (or N/A)
- CI: <gh run URL>

## Residual risk / follow-ups
- ...

## Artifact index
.temp/task-<slug>/
  context.md           (context-gather)
  requirements.md      (requirements)
  scope.md             (scoping)
  brainstorm.md        (plan-brainstorm, if used)
  spec.md              (plan-spec, if used)
  design.md            (plan-design, if used)
  preview/sample-N.html (frontend-mockup, if UI)
  plan.md              (plan-roadmap, if used)
  validation/d1.md     (review-local)
  browser-validation/... (validate-browser)
  report.md            (this file)
```
