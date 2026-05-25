# adk-implement — workflow

Five phases, all wrapped by `shared/advisor.md`. Mode-aware (`--plan` skips Phase 2+; `--act` skips Phase 1 if a stale-checked plan.md exists).

## Phase 0 — context-gather

- `shared/workflows/phase-0-context-gather.md`
- Run `scripts/classify-input.py` to determine sub-flow.
- Fan-out fetch all URLs/keys (Jira, GH, Confluence, Slack). One hop only.
- Optional RAG enrichment if `core.yaml.rag.enabled` and prompt matches `rag.trigger_keywords`.
- Build `.temp/adk/implement/<task>/context.md`.

## Phase 1 — advise

- `shared/workflows/phase-1-advise.md` + `shared/advisor.md` + `shared/question-first.md`.
- Up to 3 questions: **scope** (vertical-slice / full / spike), **constraints** (deadline / blocker / specific reviewer), **test-coverage** (when not derivable from context).
- **Challenge fires** if `grep` of the repo suggests the task may already be done.
- Recommend 2–4 approaches; record fork `approach`.
- Write `.temp/adk/implement/<task>/plan.md`.

## Phase 2 — execute

- `shared/workflows/phase-2-execute.md` + `references/<sub-flow>.md`.
- Edit format: SEARCH/REPLACE blocks per `shared/edit-format.md`.
- Read every file before writing it (constitution §V).
- Auto-load applicable guidelines (frontend / api / data / security / testing / performance / accessibility).
- Each checkpoint runs narrow validators.
- Diffs → `.temp/adk/implement/<task>/diffs/applied.jsonl`.

## Phase 3 — validate

- `shared/workflows/phase-3-validate.md`.
- Repo-native typecheck + lint + narrow tests.
- Constitution check (force-push / protected-branch / no-verify).
- Self-coherence: delivered matches plan; deviations explained.

## Phase 4 — report

- `shared/workflows/phase-4-report.md`.
- `.temp/adk/implement/<task>/report.md` — risk-first ordering.
- Session summary → `$ADK_DATA_HOME/improve/learning/sessions/<date>-implement-<slug>.md`.
- Next-best suggestions: `/adk-document --type pr-body`, `/adk-sync --to gh-pr-body`.

## Personas loaded

- `shared/personas/implementer.md` — Phase 2 author.
- `shared/personas/test-engineer.md` — Phase 2 test checkpoint.
- `shared/personas/code-reviewer.md` — Phase 3 self-review.
- `shared/personas/security-reviewer.md` — Phase 3 when diff touches auth / input / crypto / deps.

## Mode awareness

- `--plan`: stops after Phase 1. Allowed tools restricted to Read/Grep/Glob/WebFetch (no Edit/Write/Bash-write). See `shared/plan-act-mode.md`.
- `--act`: starts at Phase 2 if a plan.md exists. Re-runs Phase 1 if plan.md is older than 24h OR repo has new commits since plan was generated.
- (no flag): runs all 5 phases in one invocation, with a confirm gate at the Phase 1 → Phase 2 boundary.
