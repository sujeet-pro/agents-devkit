# `code-api` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/code-api.md` (or, if no validation/ subfolder exists yet, create it).

## Phase 0 — pre-execution

- [ ] `.temp/task-<slug>/` exists; `.temp/` is gitignored.
- [ ] User's prompt captured in `prompt.txt`.
- [ ] Repo resolved.
- [ ] Contract type identified (REST / RPC / SDK / CLI / types).
- [ ] Status identified (NEW / EVOLUTION).
- [ ] If EVOLUTION: existing artifact location identified.
- [ ] Slug derived.

## Phase 1 — preflight

- [ ] `git status` clean.
- [ ] Branch captured. Protected → branch-creation prompt.
- [ ] Existing contract artifacts read (OpenAPI / .proto / .d.ts / etc.).
- [ ] If EVOLUTION: external consumers identified (best-effort grep across repos accessible).

## Phase 2 — capture use cases

- [ ] `use-cases.md` exists.
- [ ] At least 1 use case listed (3 strongly recommended).
- [ ] Per use case: Caller, Input, Output, Errors documented.
- [ ] Out of scope listed.
- [ ] Approval gate fired (unless `--auto`).
- [ ] If 0 use cases were captured, STOP — design without use cases is by-vibes.

## Phase 3 — sketch candidates

- [ ] `candidates.md` exists.
- [ ] 2-3 candidates listed (1 candidate alone is not a design).
- [ ] Each candidate: Shape, Pros, Cons, Use-case fit.
- [ ] Candidates are genuinely different (not 3 variations of the same shape).

## Phase 4 — pick + rationale

- [ ] `design.md` exists.
- [ ] One candidate picked.
- [ ] Rationale (1-2 paragraphs) explains the choice + what was traded.
- [ ] Hyrum's Law caveats listed: Guaranteed vs Observable-but-unsupported.
- [ ] Validation strategy documented (boundary-only).
- [ ] Versioning approach documented.
- [ ] Approval gate fired (unless `--auto`).

## Phase 5 — produce artifact

- [ ] Concrete artifact produced (OpenAPI YAML / .proto / .d.ts / CLI spec).
- [ ] Artifact lives at the repo's documented location OR at `.temp/task-<slug>/contract.<ext>` with a "where to land it" recommendation.
- [ ] Artifact compiles / parses / passes its own format-tool's validation:
    - OpenAPI → `swagger-cli validate openapi.yaml` / `redocly lint`.
    - Protobuf → `protoc --proto_path=. ...` doesn't error.
    - TS .d.ts → `tsc --noEmit` doesn't error.

## Phase 6 — deprecation plan (if `--breaking`)

- [ ] `deprecation-plan.md` exists (only when `--breaking` set or design implies breaking changes).
- [ ] Old contract identified (file/version).
- [ ] Migration path with steps.
- [ ] Deprecation window stated (default: ≥ 1 major + 90 days).
- [ ] Warning emission documented (header / log / stderr).
- [ ] Removal target stated.
- [ ] Communication plan documented.

## Phase 7 — pre-handoff

- [ ] `report.md` covers: Contract, Use cases, Candidates considered, Picked, Hyrum's Law caveats, Contract artifact, Versioning, Deprecation (if any), Validation evidence, Decisions, Residual risk, NOT done, Next steps.
- [ ] Every artifact referenced in `report.md` exists.
- [ ] Decisions table includes every auto-pick.
- [ ] No remote write.
- [ ] Final status banner printed.
- [ ] Offer-depth question asked.

## Hard checks

1. `use-cases.md` exists.
2. `candidates.md` has ≥2 candidates.
3. `design.md` has the picked candidate + rationale + Hyrum's Law caveats.
4. A concrete contract artifact exists (in repo or `.temp/`).
5. If breaking: `deprecation-plan.md` exists.
6. Artifact passes its format tool's validation (OpenAPI / Protobuf / TS / CLI parser).

If any hard check fails:

- The skill is BLOCKED.
- The status banner shows `artifact=pending` or `picked=pending`.

## On any check failure

1. Log under `## Validator failures`.
2. Block the next phase.
3. If 0 use cases captured → STOP, ask the operator.
4. If only 1 candidate → STOP, sketch a second.
5. If artifact format validation fails → fix; don't proceed with an invalid artifact.
6. If design implies breaking changes but `--breaking` not set → STOP, surface, ask the operator to confirm + re-invoke with `--breaking`.
