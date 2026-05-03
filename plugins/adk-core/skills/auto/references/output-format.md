# `auto` — output format

## Per-turn status (each turn opens with this)

```
[adk-core:auto] task=<slug> phase=<0|1|2|3|4|5> status=<in-progress|blocked|done> mode=<auto|interactive>
```

## Final report (Phase 5 done)

Written to `.temp/task-<slug>/report.md`:

```markdown
# auto report — <slug>

## Result
<one sentence on what was delivered>

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | slug | <slug> | derived from prompt nouns |
| 0 | classification | code, review | both verbs detected |
| 3 | chain | code-bugfix → review-code-changes | bug-shaped + pre-PR check |

## Skills run
- `/adk-code:code-bugfix` — `.temp/task-<slug>/report.md` — status: ok
- `/adk-review:review-code-changes` — `.temp/task-<slug>/review/findings.md` — status: ok (1 Suggestion, 0 Blockers)

## Validation evidence
- Local: `.temp/task-<slug>/validation/per-skill/code-bugfix.md`
- MCP health: all required reachable
- CI: N/A (no push)

## Residual risk / follow-ups
- The hot-path query is now cached for 60s. Watch DD `cache_hit_ratio` over the next 24h.

## Artifact index
.temp/task-<slug>/
  prompt.txt           verbatim user prompt
  context.md           context-gather summary (if any)
  skill-plan.md        the chosen chain + reasoning
  dispatch.md          per-slice subagent results
  validation/          per-skill validators
  report.md            this file
```

## Status-banner glossary

- `phase=0` — prompt expansion
- `phase=1` — preflight (deps + MCP + meta-info + git)
- `phase=2` — context-gather (conditional)
- `phase=3` — propose skill chain
- `phase=4` — dispatch (subagents running)
- `phase=5` — validate + report

## Decision-table guidelines

- Always include the phase the decision was made in.
- Always include the rationale (why this option, not alternatives).
- Never list more than 8 decisions; group related ones.

