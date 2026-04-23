---
title: 'build-api'
description: '|'
skill_name: build-api
category: router
---
# build-api — contract-first interface design

Standalone task skill under the `@adk:build` (a.k.a. `adk-build`) category router. Produces a typed, validated, additively-evolvable interface, plus the smallest correct implementation that satisfies it.

## When to use

- A new HTTP/REST/gRPC/GraphQL endpoint or resource.
- A new RPC method or message contract.
- A new internal module boundary (the public types another module imports).
- A new library export surface (the `index.ts` someone else will pin a version to).
- A new CLI command, flag, or environment variable contract.
- An evolution to any of the above (additive field, deprecation, response shape change).

## When NOT to use

- Implementation-only change behind an existing contract → `@adk:build-feature` (a.k.a. `adk-build-feature`).
- Architecture write-up across multiple components → `@adk:plan-design` (a.k.a. `adk-plan-design`).
- Library/runtime version migration → `@adk:build-migrate` (a.k.a. `adk-build-migrate`).
- Authoring tests for an existing API → `@adk:build-test` (a.k.a. `adk-build-test`).
- Documenting an existing API as a reference doc → `@adk:docs-write` (a.k.a. `adk-docs-write`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<surface>` | yes | What contract is being designed (resource, method, module, CLI). |
| `<consumers>` | yes | Who couples to this — internal callers, partner services, public users, future-self. |
| `<change kind>` | optional | `new` / `evolve` / `breaking`. Default `new`. |
| `<scope>` | optional | Path filter for the implementation. |
| `--auto` | optional | Skip approval gates (still validates). |

## Workflow

1. **Confirm intent** — restate the surface, the consumers, and whether this is `new` / `evolve` / `breaking`. Approval gate unless `--auto`.
2. **Inventory existing surface** — read sibling endpoints/methods, error envelopes, naming conventions, status code patterns, pagination approach, ID format. The new surface MUST match the repo's already-established style unless the user explicitly asks to break with it.
3. **Draft the contract first, no implementation** — types in TypeScript / OpenAPI / Protobuf / JSON Schema (whatever the repo uses). Includes:
   - Input shape with ALL fields named, typed, and marked required vs optional.
   - Output shape including the success envelope and the error envelope.
   - Status codes / error codes mapped to semantic meaning (use the table in `references/error-semantics.md`).
   - Pagination / filtering / sorting decisions if a list endpoint.
   - Idempotency contract (which verbs / which keys).
   - Versioning posture (URL-versioned, header-versioned, additive-only, etc.).
4. **Hyrum's Law audit** — list every observable behavior consumers may come to depend on (response field order, default values, error message strings, timing, retry-after, log line shape). Decide explicitly which are part of the contract and which are not — and document the not-in-contract ones with "may change without notice" notes.
5. **Edge validation only** — design validation at the boundary (Zod / Pydantic / protobuf / OpenAPI middleware). Internal types are trusted; external inputs are not. Validate ONCE at the edge.
6. **Implement** — smallest correct implementation behind the contract. Use the smallest mock / fake for downstream dependencies that are out of scope.
7. **Validate** — run repo-native typecheck + lint + tests. For HTTP, exercise the contract with a request smoke test (curl / supertest / OpenAPI conformance). For libraries, write a consumer-side import test in the same repo.
8. **Report** — contract diff, consumer impact, breaking-change call-out, additive vs breaking classification, residual risk.

## Hard rules

- **Contract before implementation.** No code is written until the types/schema exist.
- **One-Version Rule.** The repo runs ONE version of the contract at a time. Branching internal callers across two versions is forbidden — use a flag/transform layer if you must.
- **Additive evolution by default.** New fields are optional. Existing fields keep their type. Status codes are not re-mapped.
- **Validation at the edge, exactly once.** No second-pass validation deeper in the call stack.
- **Untrusted inputs from third parties** (including other internal services on a different deploy cadence) are validated like external inputs.
- **Errors are part of the contract.** A new error code is a contract change.
- **Naming is part of the contract.** Renaming a field IS a breaking change even if you keep the old field as a duplicate.

## Anti-patterns

- Implementing first and "deriving" the contract from the implementation — Hyrum's Law guarantees the implementation's quirks become the contract.
- Multiple versions of the same contract in the same deployable to "be backward compatible" — collapse them, or version externally.
- Sneaking a breaking change in as a "bug fix" because the old behavior was wrong — it's still breaking; classify it correctly and migrate consumers.
- Validating in three places "to be safe" — duplicate validation drifts and lies.
- Re-using HTTP 200 with `success: false` body — pick the correct status code (4xx for client error, 5xx for server error).
- Untyped `any` / `dict` / `interface{}` on the public surface to "stay flexible" — flexible APIs are the ones that break consumers when they finally have to be made strict.
- Inventing a new error envelope shape per endpoint — pick one envelope for the whole repo and reuse it.

## Examples

```
adk-build-api "Add a paginated GET /api/customers endpoint" --consumers internal-admin-app
```

```
adk-build-api "Add an optional 'expand' query param to GET /api/orders/:id" --change-kind evolve
```

```
adk-build-api "Replace the legacy /v1/login response envelope with the standard error shape" --change-kind breaking --consumers mobile-app,web-app,partner-sdk
```

## Clarifying questions (default-ask)

1. **Is this contract NEW, an evolution, or an outright breaking change?** — _How to pick:_ New = no existing consumer; evolution = additive only; breaking = renames/removes/retypes/re-statuses anything observable.
2. **Who are the consumers and what's their deploy cadence?** — _How to pick:_ Internal monorepo callers can be migrated lockstep; separately-deployed services need a deprecation window; public users need a versioning story.
3. **What's the error envelope shape this repo already uses?** — _How to pick:_ Match it; do not invent a new one for one endpoint. If the repo has none, propose one and reuse it everywhere.

## Default vs detailed output

**Default report:** Contract summary + diff (additive / breaking) + consumer-impact table + validation evidence + Hyrum's-Law note.

**Detailed report (on request or `--verbose`):** Full schema (request + response + error envelope), the rejected alternatives with reasoning, and a migration playbook for each consumer if breaking.

**Artifact:** `interface-contract` — Schema source committed to repo + a one-page contract summary in `.temp/plans/api-<slug>.md`.

**Artifact path:** `.temp/plans/api-<slug>.md` (contract summary), `.temp/notes/api-<slug>-hyrums-audit.md` (observable-behavior log). Schemas land in the repo proper (e.g. `openapi.yaml`, `proto/`, `src/types/api.ts`).
