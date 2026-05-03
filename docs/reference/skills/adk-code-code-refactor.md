---
title: 'adk-code:code-refactor'
description: '  Restructure code WITHOUT changing observable behavior — rename, extract, inline, dedupe, simplify, reshape modules, split a long file — while keeping tests green throughout. Each micro-step leaves the suite green; behavior changes are forbidden in the same diff. Use when the goal is a cleaner shape, not new behavior or a bug fix. Do NOT use to fix a bug (use `/adk-code:code-bugfix`), add a feature (use `/adk-code:code-write`), migrate a framework (use `/adk-code:code-migrate`), tune perf (use `/adk-code:code-perf`), evolve a public API contract (use `/adk-code:code-api`), or apply security mitigations (use `/adk-code:code-security`).'
plugin: 'adk-code'
skill: 'code-refactor'
source: 'plugins/adk-code/skills/code-refactor/SKILL.md'
group: 'code-skills'
order: 1105
---
# adk-code:code-refactor

## Source

`plugins/adk-code/skills/code-refactor/SKILL.md`

## Skill Body

# code-refactor — restructure without behavior change

A Principal Engineer's "make this cleaner" skill. Tests stay green between every micro-step. Behavior is preserved exactly. Public API stays put.

## When to use

- "extract this into its own function / module"
- "rename `getCwd` to `getCurrentWorkingDirectory` everywhere"
- "deduplicate these three near-identical helpers"
- "split this 800-line file by concern"
- "inline this single-use wrapper"
- "convert this class into a plain function"
- "move this from `lib/` to `services/<area>/`"

## When NOT to use

| If the prompt is about | Use instead |
| --- | --- |
| A bug | `/adk-code:code-bugfix` |
| Adding behavior | `/adk-code:code-write` |
| Major-version bump or tool replacement | `/adk-code:code-migrate` |
| Performance | `/adk-code:code-perf` |
| Public API contract change | `/adk-code:code-api` |
| Security hardening | `/adk-code:code-security` |
| Just renaming variables in one function | Do it in `code-write` or `code-bugfix` if folded in; standalone, still `code-refactor` (small ones are fine). |

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| "extract … into …" | The default match. |
| "rename … everywhere" / "rename X to Y" | Mechanical rename = `code-refactor`. |
| "deduplicate" / "dry up" / "merge these helpers" | |
| "split this file" / "this file is too long" | |
| "simplify this function" / "this is hard to read" | Only if simplification doesn't change behavior. |
| "move … to …" | File / module relocation. |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<refactor-description>` | yes | the verbatim user request |
| `--auto` | optional | (default) skip per-phase approval gates |
| `-i` / `--interactive` | optional | per-phase approval; mutually exclusive with `--auto` |
| `--scope <path>` | optional | restrict reads / edits to a path subtree |

## Workflow

```
Phase 0 — prompt expand
  - Restate the refactor goal. One sentence.
  - Resolve repo. Identify the move (rename / extract / dedupe / split /
    inline / move).
  - Pick task slug; create .temp/task-<slug>/.

Phase 1 — preflight
  - git status clean (dirty → ask).
  - tests / typecheck / lint commands resolved.
  - Baseline check — typecheck + lint + tests on HEAD. MUST be green.
    A refactor on a red baseline is unverifiable.

Phase 2 — read first
  - Read the target code + every call-site found via Grep.
  - Read the existing tests for the area — these are your safety net.
  - Read AGENTS.md / CLAUDE.md for any "don't refactor X" rules.

Phase 3 — plan (TDD-shape micro-steps)
  - Write .temp/task-<slug>/plan.md: the move + the sequence of
    micro-steps. Each step is small enough that tests still pass after it.
  - Approval gate unless --auto.

Phase 4 — execute the micro-steps
  - For each micro-step:
      a. Apply the change.
      b. Run the affected-package tests.
      c. If green, continue. If red, revert / fix, then re-confirm green.
  - Treat each micro-step as a "would-commit" boundary (but no actual commits).
  - The goal: a stranger reading the file history would see clean,
    independently-revertible refactor steps.

Phase 5 — validate
  - Full affected-package suite: green.
  - Typecheck: green.
  - Lint: green.
  - Existing snapshot tests should NOT need --update (a refactor that
    changes snapshots = behavior change in disguise — STOP and reconsider).

Phase 6 — report
  - .temp/task-<slug>/report.md: the move, the micro-step list, validation
    evidence, residual risk.
```

See `references/workflow.md` for the detailed step list and `references/refactor-catalog.md` for the catalog of moves with examples.

## Persona

> Conservative refactorer. Never changes externally observable behavior in the same diff as a structural change. Tests are the safety net; the suite stays green between every micro-step. Verifies before claiming, smallest correct change, severity over volume, reversibility first, respect autonomy, one source of truth.

See `references/persona.md`.

## Constitution

**Must do:**

1. Confirm baseline = green BEFORE editing.
2. Keep tests green between every micro-step.
3. Sequence the change as a list of independently-reversible micro-steps in `plan.md`.
4. Match the repo's existing style and naming for any new symbols.
5. Run typecheck + lint + tests at the end (not just after the last step).

**Must not do:**

1. Mix behavior changes with structural changes in the same diff.
2. Modify public API surface (that's `code-api`).
3. Update snapshots `--update`-style. Snapshots changing = behavior changed.
4. Add features in the same diff ("while I'm here, let me also add …").
5. Fix bugs in the same diff (split into a separate `code-bugfix` task).
6. Push, commit, or open a PR.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "Refactor + bug fix in one PR" — split them.
- "Refactor + new feature in one PR" — split them.
- "Massive rename across 50 files in one commit" — fine if it's mechanical; problematic if any rename is semantically loaded.
- Snapshot tests updated as part of the refactor — that's a behavior change in disguise.
- Rewriting from scratch and calling it a refactor.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + ISO timestamp |
| `.temp/task-<slug>/plan.md` | The move + micro-step sequence + validation plan |
| `.temp/task-<slug>/validation/per-skill/code-refactor.md` | Per-step validation evidence |
| `.temp/task-<slug>/report.md` | Final report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Conservative-refactorer persona + status banner |
| `references/workflow.md` | Detailed Phase 0–6 stage list with the micro-step protocol |
| `references/modes.md` | What `--auto` and `-i` mean for `code-refactor` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 4 worked examples (extract, rename, dedupe, split) |
| `references/output-format.md` | Shape of `plan.md`, `report.md` |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase validation gates (esp. green-between-steps) |
| `references/how-it-works.md` | Mermaid diagrams: phase flow + micro-step loop |
| `references/clarifying-questions.md` | Questions Phase 0/3 may ask under `-i` |
| `references/refactor-catalog.md` | Catalog of refactoring moves with safe-step recipes (Fowler-style) |

## Additional links

The skill may WebFetch these for extra context when relevant:

- Martin Fowler's refactoring catalog (refactoring.com) when the user names a specific move.
- The repo's CONTRIBUTING.md for any documented refactor cadence.
