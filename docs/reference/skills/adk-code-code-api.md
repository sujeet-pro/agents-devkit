---
title: 'adk-code:code-api'
description: '  Design or evolve a stable interface — REST/HTTP API, RPC contract, internal module boundary, library export surface, CLI flag set, public type definitions — using contract-first discipline, Hyrum''s Law awareness, edge-only validation, and explicit version policy. Sketches 2-3 candidate contracts with trade-offs, picks one, and produces an OpenAPI / Protobuf / TypeScript-types file plus a `design.md` rationale. Use when the deliverable is the SHAPE of the interface (the contract), not its implementation. Do NOT use for inside-the-boundary work / implementation behind the contract (use `/adk-code:code-write`), pure refactors that don''t touch the contract (use `/adk-code:code-refactor`), bug fixes (use `/adk-code:code-bugfix`), framework migrations (use `/adk-code:code-migrate`), perf (use `/adk-code:code-perf`), or security mitigations alone (use `/adk-code:code-security`).'
plugin: 'adk-code'
skill: 'code-api'
source: 'plugins/adk-code/skills/code-api/SKILL.md'
group: 'code-skills'
order: 1101
---
# adk-code:code-api

## Source

`plugins/adk-code/skills/code-api/SKILL.md`

## Skill Body

# code-api — design or evolve a contract

A Principal Engineer's "contract-first" skill. Hyrum's Law awareness, one-version rule with deprecation policy, edge-only validation, and a written design rationale.

## When to use

- "design the v2 endpoint set for `/orders`"
- "evolve the SDK export surface for the `@acme/checkout` package"
- "design the RPC contract between the order-service and the inventory-service"
- "design CLI flag set for the new `migrate` command"
- "redesign the `ProductCatalog` module's public types"
- "draft the OpenAPI for the new `/api/users/timeline` endpoint"

## When NOT to use

| If the prompt is about | Use instead |
| --- | --- |
| The implementation behind the contract (the body of the function) | `/adk-code:code-write` |
| Refactor that doesn't change the contract | `/adk-code:code-refactor` |
| Bug fix in the existing contract | `/adk-code:code-bugfix` |
| Migrating a framework's contract (React 18 → 19) | `/adk-code:code-migrate` |
| Performance | `/adk-code:code-perf` |
| Security hardening | `/adk-code:code-security` |
| Inventory of "what other repos import from this one" | (out of scope; surface as a follow-up audit-repo) |

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| "design [the] … endpoint(s)" / "design the API for …" | Default match. |
| "evolve / redesign [the] … contract" | |
| "draft the OpenAPI / Protobuf / types for …" | |
| "design the SDK / library export surface" | |
| "design the CLI flag set for …" | |
| "v2 / next-version of [the] …" + interface | |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<api-area>` | yes | the verbatim user request (which interface) |
| `--breaking` | optional | acknowledges this design has a breaking change; the skill produces a deprecation plan |
| `--auto` | optional | (default) skip per-phase approval gates |
| `-i` / `--interactive` | optional | per-phase approval; mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  - Restate the contract being designed: REST / RPC / module / SDK /
    CLI / types.
  - Resolve repo via repos.md.
  - Identify if this is a NEW contract or an EVOLUTION of an existing one.
  - Pick task slug.

Phase 1 — preflight
  - git status clean (dirty → ask).
  - Identify existing contract artifacts (OpenAPI files, .proto files,
    TypeScript declaration files, exports lists).

Phase 2 — capture use cases
  - List the top 3 use cases this contract must serve.
  - For each: who calls it, with what inputs, expecting what output.
  - Save to .temp/task-<slug>/use-cases.md.
  - Approval gate (under -i) before sketching candidates.

Phase 3 — sketch candidate contracts (2-3)
  - Sketch 2-3 candidate contracts.
  - For each: shape (URL / type / method signature), trade-offs, fit
    against the use cases.
  - Save to .temp/task-<slug>/candidates.md.

Phase 4 — pick one + rationale
  - Pick one candidate. Justify against the use cases + the constitution
    (Hyrum's Law awareness, one-version rule, edge validation).
  - Save to .temp/task-<slug>/design.md.
  - Approval gate unless --auto (this is the most-valuable gate).

Phase 5 — produce the contract artifact
  - For REST: an OpenAPI fragment (or PR-ready spec section).
  - For RPC: a Protobuf .proto.
  - For SDK / module: a TypeScript .d.ts (or equivalent in the repo's
    language).
  - For CLI: a usage spec + flag list.
  - The contract artifact lives in the working tree at the repo's
    documented contract-artifact location (or in design.md if no such
    location yet).

Phase 6 — deprecation plan (if --breaking)
  - Spec the deprecation window: warnings, dual-support period, removal
    target version.
  - Save to .temp/task-<slug>/deprecation-plan.md.

Phase 7 — report
  - .temp/task-<slug>/report.md: chosen contract, rationale, alternatives,
    migration plan, residual risk.
```

See `references/workflow.md` for the detailed step list.

## Persona

> Contract-first designer. Aware of Hyrum's Law (every observable behavior becomes someone's depended-on contract). Conservative with breaking changes — every breaking change is documented with a migration plan and a deprecation window. Validation lives at the boundary; internal callers are trusted. Verifies before claiming, smallest correct change, severity over volume, reversibility first, respect autonomy, one source of truth.

See `references/persona.md`.

## Constitution

**Must do:**

1. Capture the top 3 use cases the contract must serve.
2. Sketch 2-3 candidate contracts with trade-offs.
3. Pick one with a written rationale (`design.md`).
4. Produce a concrete contract artifact (OpenAPI / Protobuf / .d.ts / CLI spec).
5. Apply the One-Version Rule: a single canonical version; explicit deprecation policy for breaking changes.
6. Validate at the edge — input validation belongs at the boundary, not in inner layers.
7. Document Hyrum's Law assumptions: "this is what the contract guarantees; this is what is observable but unsupported".

**Must not do:**

1. Ship inside-the-boundary defensive code as if it were the contract.
2. Assume internal callers will read release notes (they won't; design accordingly).
3. Make breaking changes without a deprecation window.
4. Add two near-duplicate endpoints because nobody wanted to touch the existing one.
5. Wave at the design as "we'll figure it out in implementation".
6. Push, commit, or open a PR.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "We'll add validation everywhere, just in case" — that's how trust collapses.
- Two near-duplicate endpoints because nobody wanted to touch the existing one.
- Breaking changes without a deprecation window.
- "The contract is whatever the code does" — Hyrum's Law eats this.
- Designing without capturing use cases.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + ISO timestamp |
| `.temp/task-<slug>/use-cases.md` | Top 3 use cases the contract must serve |
| `.temp/task-<slug>/candidates.md` | 2-3 candidate contracts with trade-offs |
| `.temp/task-<slug>/design.md` | Chosen contract + rationale |
| `.temp/task-<slug>/contract.<ext>` | The artifact (OpenAPI YAML / .proto / .d.ts / CLI spec) |
| `.temp/task-<slug>/deprecation-plan.md` | (if `--breaking`) deprecation window + migration |
| `.temp/task-<slug>/report.md` | Final report |

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Contract-first designer persona + status banner |
| `references/workflow.md` | Detailed Phase 0–7 stage list |
| `references/modes.md` | What `--auto` and `-i` mean for `code-api` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 4 worked examples (REST, RPC, SDK, CLI) |
| `references/output-format.md` | Shape of `use-cases.md`, `candidates.md`, `design.md` |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase validation gates |
| `references/how-it-works.md` | Mermaid diagrams: design flow + Hyrum's Law decision tree |
| `references/clarifying-questions.md` | Questions Phase 2/4 may ask under `-i` |
| `references/contract-versioning.md` | One-version rule, deprecation, semver, header-vs-URL versioning |

## Additional links

The skill may WebFetch these for extra context when relevant:

- The repo's existing OpenAPI / Protobuf files.
- API design guides: Google's API Improvement Proposals (AIPs), RESTful Web Services Cookbook, gRPC API Design Guide.
- Industry references: Stripe's API design philosophy, GitHub's API versioning approach.
