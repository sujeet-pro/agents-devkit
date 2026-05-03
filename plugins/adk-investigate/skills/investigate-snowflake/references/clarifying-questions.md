# `investigate-snowflake` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently — except for the three confirmation gates documented in `modes.md`.

## Phase 0 questions

1. **View: `<resolved>` from `snowflake.md.common_views`. Right one?**
   - _When asked:_ multiple candidates match; OR no candidate matches (so we'd be inferring).
   - _Default under `--auto`:_ pick the verified candidate; refuse to infer across pods (ask).

2. **Warehouse: `<resolved>`. Role: `<resolved>`. OK?**
   - _When asked:_ user passed `--warehouse` or `--role` flag with a non-default value.
   - _Default under `--auto`:_ use the defaults from `snowflake.md`. Non-default flags require confirmation.

3. **Window: `<resolved>`. OK?**
   - _When asked:_ ambiguous NL window in the question.

## Phase 2 questions

4. **SQL constructed: `<sql>`. Run it?**
   - _When asked:_ first query of any session — even under `--auto`.
   - _Default under `--auto` for subsequent queries:_ run silently (SQL still printed to the operator).

5. **`--limit > 100`. Confirm: return up to `<N>` rows?**
   - _When asked:_ always when `--limit > 100`, even under `--auto`.
   - _Default under `--auto`:_ NEVER auto-run > 100 rows; stop and ask.

## Phase 4 questions

6. **Aggregation choice: top-`<N>` by `<metric>` OR histogram OR raw table?**
   - _When asked:_ ambiguous question shape (e.g. "show me skus").
   - _Default under `--auto`:_ top-20 by primary metric; histogram if the question implies a distribution.

7. **Report ready. Anything to redo?**
   - _Default under `--auto`:_ `(no)`.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` EXCEPT the three confirmation gates (first SQL, `--limit > 100`, non-default warehouse/role).
- Never ask "are you sure?" before a refusal — the refusal is the answer.
- Never ask the operator to override the PII guardrail. The block list is enforced; the only way to change it is to edit `~/.config/adk/snowflake.md` directly.
