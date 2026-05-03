# `docs-write` — clarifying questions

Asked under `-i` / `--interactive`, one at a time, only when the answer
changes the plan. Under `--auto`, defaults apply silently and surface in
the final report.

## Phase 0 questions

1. **Doc type: `<inferred>`. Is this correct?**
   - _How to pick:_ See `references/how-it-works.md` classification
     tree. Default is the highest-scoring match.
   - _Default under `--auto`:_ the inferred type.

2. **Subject / scope: `<repo or subservice>`. Narrow the scope?**
   - _How to pick:_ Useful for monorepos where the prompt is ambiguous
     ("README for the dashboard" — which dashboard?).
   - _Default under `--auto`:_ repo root; scope inferred from `--scope`.

## Phase 1 questions

3. **Target canonical path: `<path>`. Use this, or a different path?**
   - _How to pick:_ Default is `references/artifact-format.md`'s table.
     Override when the project has a non-standard layout.
   - _Default under `--auto`:_ the table's default.

4. **Audience: `<audience>`. Override?**
   - _How to pick:_ Default from `docs.md.audience_default`. Override
     when the doc will land in a different audience's folder (e.g.
     ADR → mostly engineers; migration guide → mixed).

## Phase 3 questions

5. **Draft is ready. Review now, or proceed to validation?**
   - _Default under `--auto`:_ proceed.

## Phase 4 questions (only under `--fix`)

6. **Target `<path>` exists (last edited by `<author>` on `<date>`).
   Overwrite?**
   - _Default under `--auto --fix`:_ still asks once before overwrite
     to catch human-authored files.

7. **Stage the change with `git add <path>`?**
   - _Default under `--auto`:_ yes (staging-only; no commit).

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something `docs.md` already answers (resolved ≠
  ambiguous).
- Never ask under `--auto` unless the overwrite-gate triggers.
- If the user already answered the same question earlier in this
  session, don't re-ask.
