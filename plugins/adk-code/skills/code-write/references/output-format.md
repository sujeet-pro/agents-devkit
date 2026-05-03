# `code-write` — output format

## Per-turn status

```
[adk-code:code-write] task=<slug> phase=<0|1|2|3|4|5|6> files-planned=<N> files-changed=<M> validation=<pending|green|red>
```

## `.temp/task-<slug>/plan.md` (Phase 3)

```markdown
# code-write plan — <slug>

## Goal
<one sentence stating what the user gets when this is done>

## Scope
- Repo: <owner/repo> @ <local path>
- Branch: <branch name>
- Subtree (if --scope): <path>

## Files touched
| Path | Action | Why |
| --- | --- | --- |
| src/foo/bar.ts | edit | thread the new option through |
| src/foo/bar.test.ts | edit | add 3 tests for the new option |
| docs/foo.md | edit | document the new option |

## Approach
1. <step 1 — one bullet>
2. <step 2 — one bullet>
3. <step 3 — one bullet>

## Edge cases
| Condition | Expected behavior | Test pointer |
| --- | --- | --- |
| empty input | exit code 2 with parse error | parse-error.test.ts:42 |
| zero-day window | inclusive — 1 day worth | window-zero.test.ts:18 |

## Test changes
- New test files: <none / list>
- New tests in existing files: <list>
- Existing tests potentially affected: <list, with reason>

## Validation plan
| Command | Expected exit | Notes |
| --- | --- | --- |
| `npm run typecheck` | 0 | full package |
| `npm run lint -- --max-warnings 0` | 0 | |
| `npm test -- src/commands/export` | 0 | scoped |

## Out of scope (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/report.md` (Phase 6)

```markdown
# code-write report — <slug>

## Result
<one sentence on what was delivered>

## Files changed
| Path | +N / -M | Why |
| --- | --- | --- |
| src/foo/bar.ts | +18 / -2 | added --since option, threaded to query |
| src/foo/bar.test.ts | +47 / -0 | 3 happy + 1 boundary + 1 error |

## Validation evidence
| Command | Exit | Notes |
| --- | --- | --- |
| `npm run typecheck` | 0 | clean |
| `npm run lint -- --max-warnings 0` | 0 | |
| `npm test -- src/commands/export` | 0 | 47 passed |
Full logs: `.temp/task-<slug>/validation/per-skill/code-write.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | slug | <slug> | derived from prompt nouns |
| 3 | default duration | 7d | quoted in the prompt |
| 5 | snapshot updated | yes | (--auto) — snapshot was the only test failure, change is intentional |

## Residual risk / follow-ups
- docs/cli/export.md not updated — out of scope for this task; spawn `/adk-docs:docs-write` to update.
- The existing date-parser helper has 2 callers; not yet 3, so no extraction yet.

## NOT done (deliberate)
- Refactor the date-parser helper — only 2 callers; below the 3-caller threshold.
- Add e2e test — no e2e harness in this repo for CLI commands.

## Next steps
1. `/adk-review:review-code-changes` before push.
2. (optional) `/adk-docs:docs-write "update CLI docs for --since"`.

## Artifact index
.temp/task-<slug>/
  prompt.txt              verbatim user prompt + ISO timestamp
  plan.md                 the plan (Phase 3)
  validation/per-skill/code-write.md  command logs
  report.md               this file
```

## Decision-table guidelines

- Always include the phase the decision was made in.
- Always include the rationale (why this option, not alternatives).
- Never list more than 8 decisions; group related ones.
- Decisions made under `--auto` (because the user did not get a gate to choose) are listed in **bold**, prefixed with `(--auto)`.

## Hand-off note shape

When `code-write` finishes, it ends with a 3-line hand-off:

```
Result: <one sentence>
Validation: <commands run + exit codes summary>
Next: /adk-review:review-code-changes <slug>   # before push
```

Plus the offer-depth question: "Need more detail on any decision?".
