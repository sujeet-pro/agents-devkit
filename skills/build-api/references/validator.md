# `build-api` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/build-api.md`.

## Phase 1 — pre-execution

- [ ] Surface, consumers, and change-kind (`new`/`evolve`/`breaking`) are explicit.
- [ ] `.temp/task-<slug>/` exists.
- [ ] Repo's existing API style has been read (sibling endpoints, error envelope, naming).
- [ ] If `change-kind = breaking`, every named consumer has a migration owner identified.

## Phase 2 — mid-flow

- [ ] Contract draft (types/schema) was written **before** any implementation file changed.
- [ ] Hyrum's-Law audit log exists at `.temp/task-<slug>/notes/api-<slug>-hyrums-audit.md`.
- [ ] Validation is designed at exactly ONE boundary (the edge).
- [ ] Error envelope matches the repo's existing shape (or the user explicitly chose to introduce a new one repo-wide).

## Phase 3 — pre-handoff

- [ ] Schema source is committed (`openapi.yaml` / `proto/` / `src/types/api.ts` — whichever the repo uses).
- [ ] Repo-native typecheck + lint pass on changed files.
- [ ] Smoke test against the contract ran and is captured (curl / supertest / OpenAPI conformance / consumer-side import test).
- [ ] If `evolve` or `breaking`, the diff against the prior contract is in the report (added / removed / retyped fields, added / removed status codes).
- [ ] Additive vs breaking classification is in the report and matches the actual diff.
- [ ] No second-pass validation introduced deeper in the call stack.

## Phase 4 — post-execution

- [ ] Final report exists with contract summary, consumer-impact table, Hyrum-Law note.
- [ ] If breaking, deprecation/migration plan is referenced (handed off to `@adk:build-migrate` or filed as a separate task).
- [ ] User acknowledged (or `--auto`).
