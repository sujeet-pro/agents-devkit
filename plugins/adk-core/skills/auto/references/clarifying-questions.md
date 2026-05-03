# `auto` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 0 questions

1. **Is this slug correct: `<proposed-slug>`?**
   - _How to pick:_ Slug becomes `.temp/task-<slug>/`. Default: derived from the first 3-5 nouns/verbs in the prompt, kebab-cased.
   - _Skip when:_ Always show under `--auto` only as info, not a question.

2. **Should I gather context from these links: `<list>`?**
   - _How to pick:_ If the user pasted any link, default `yes`. Skip only if the user says "the prompt is self-contained".

3. **Verb classification: `<comma-separated>`. Is the primary verb correct?**
   - _How to pick:_ Default is the highest-scoring verb. Show all; let the user reorder if needed.

## Phase 3 questions

4. **Recommended skill chain: `<list>`. Approve, edit, or change?**
   - _How to pick:_ Default `(approve)` under interactive mode; under `--auto` it dispatches without asking.
   - The user can edit by saying "drop step 2" or "use review-feedback instead of review-pr".

5. **Modes per skill: `--auto` for non-mutation, `-i` for mutation. Override?**
   - _How to pick:_ Default `--auto` for read-only skills (`investigate-*`, `audit-*`, `info`, `docs-review`). Default `-i` for mutation skills if not under top-level `--auto`. Under top-level `--auto`, propagate `--auto` to all.

6. **Confidence target: 80, 90, or 95?**
   - _How to pick:_ Production-safe = 95. Standard feature/refactor = 90 (default). Exploratory / personal = 85.

7. **Change tolerance: surgical, bounded, or transformative?**
   - _How to pick:_ Surgical = touch only what must change; reversible in <1h. Bounded (default) = touch one subsystem; reversible in <1d. Transformative = many subsystems; reversibility hard.

## Phase 5 questions

8. **Final report ready. Anything to redo?**
   - _How to pick:_ Default `(no)`. Surface the one-line result; offer depth.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers (resolved entity ≠ ambiguous entity).
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered the same question earlier in this session, don't re-ask.
