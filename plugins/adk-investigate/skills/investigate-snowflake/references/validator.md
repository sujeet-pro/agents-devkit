# `investigate-snowflake` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/investigate-snowflake.md`.

## Phase 0 — pre-execution

- [ ] User's question captured verbatim.
- [ ] Resolved view exists in `~/.config/adk/snowflake.md.common_views` OR explicitly noted as `inferred` (and the operator has confirmed under `-i`).
- [ ] **PII precheck completed.** Question + candidate columns matched against `pii_columns.block_substring` and `pii_columns.block_token_columns`. If any matched, the skill REFUSED and stopped here.
- [ ] Warehouse + role resolved (defaults from `snowflake.md`).
- [ ] Database + schema resolved.

## Phase 1 — preflight

- [ ] `claude mcp list` shows `Snowflake (Quince)` workspace connector as `Connected`.
- [ ] `bin/adk-info --check snowflake` returns 0.
- [ ] `.temp/` is in the repo's `.gitignore` (production data must not leak).
- [ ] The resolved view exists (cheap `DESCRIBE` call).

## Phase 2 — build SQL

- [ ] SQL string composed.
- [ ] **SQL string validator (read-only policy).** SQL contains NONE of: `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `CREATE`, `ALTER`, `DROP`, `GRANT`, `REVOKE`. If any present → REJECT.
- [ ] **SQL string validator (PII).** SQL `SELECT` clause names NO column matched by the PII block list. If any present → REJECT.
- [ ] `LIMIT <N>` is present (`100` default; `--limit` value otherwise).
- [ ] SQL is printed to the operator BEFORE execution.
- [ ] First query of session has a confirmation gate (even under `--auto`).
- [ ] If `--limit > 100`, confirmation gate (even under `--auto`).

## Phase 3 — execute

- [ ] Query was executed via the resolved warehouse + role (no escalation).
- [ ] Raw result saved to `.temp/task-<slug>/investigation/snowflake/raw/<query-id>.json`.
- [ ] Raw save path is inside `.temp/` (validated against the path).

## Phase 4 — pre-handoff

- [ ] `.temp/task-<slug>/investigation/snowflake.md` exists.
- [ ] Sections in correct order: `Question`, `Resolved entities`, `SQL`, `Result summary`, `Row count`, `Warehouse + role`, `Caveats`, `Cost` (if available), `Raw result path`, `Follow-up queries`.
- [ ] Result summary is aggregated (no 100+ row dumps).
- [ ] Caveats include freshness if known.
- [ ] Final status banner printed.

## On any check failure

- Log to `validation/investigate-snowflake.md` with the failing check + remediation.
- For PII or read-only-policy violations: BLOCK execution. Do not retry. Surface the matched rule.
- For other failures: block next phase; same check failing 3 times → surface, do not loop.
