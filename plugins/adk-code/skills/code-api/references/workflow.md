# `code-api` — workflow detail

## Phase 0 — prompt expand

1. **Restate** the contract being designed in one sentence: "Design v2 of the `/orders` REST endpoint set" / "Evolve the `@acme/checkout` SDK export surface" / "Design the RPC contract between order-service and inventory-service".
2. **Resolve repo** via `cwd → .git → repos.md`.
3. **Identify**:
    - Type: REST / RPC (gRPC / Twirp / etc.) / GraphQL / SDK module / CLI flag set / public types.
    - Status: NEW (greenfield) or EVOLUTION (existing → new shape).
    - If `--breaking` flag set: explicit acknowledgement that this design has breaking changes; deprecation plan required.
4. **Pick task slug**: usually `api-<scope>-<noun>` (e.g. `api-orders-timeline-v2`, `api-checkout-sdk-exports`).
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt`.
6. **Approval gate** unless `--auto`.

## Phase 1 — preflight

1. `git status` clean. Dirty → ask.
2. Branch — protected → prompt `api/<slug>`.
3. Identify existing contract artifacts:
    - REST: existing OpenAPI files (`openapi.yaml`, `swagger.json`, etc.) — read to understand the existing patterns.
    - RPC: existing `.proto` files.
    - SDK / module: existing `.d.ts` / `index.ts` exports.
    - CLI: existing usage spec / `--help` output.
4. If evolving an existing contract, identify external consumers:
    - For REST APIs: `grep -r 'api.acme.com/<path>'` across the org's other repos (if accessible).
    - For SDKs: `npm` consumers of the package.
    - For RPCs: services that import the `.proto` shapes.

## Phase 2 — capture use cases

List the top 3 use cases the contract must serve. For each:

- **Caller**: who is calling? (the buyer's device, the admin dashboard, an internal service, a CLI script, …)
- **Inputs**: what state / args do they have?
- **Expected output**: what do they get back; what shape?
- **Error modes**: what can go wrong; what response should they see?

Save to `.temp/task-<slug>/use-cases.md` (shape in `references/output-format.md`).

If the user can't enumerate use cases, push back. A contract without use cases is design-by-vibes.

**Approval gate** under `-i`. Under `--auto`, proceed.

## Phase 3 — sketch candidate contracts (2-3)

For each candidate:

- **Shape** — the URL pattern (REST), method signature (RPC), type definition (SDK), or flag set (CLI).
- **One-line summary** of the approach.
- **Trade-offs** — pros + cons (3-4 bullets each).
- **Use-case fit** — checked against the 3 use cases (does it serve each? at what cost?).

Common candidates by interface type:

### REST

- Resource-oriented: `GET /orders/{id}/timeline` → `{events: [...]}`.
- Action-oriented: `POST /orders/{id}/timeline:get` (Google AIP-style for non-CRUD actions).
- Filter-by-query: `GET /events?order={id}&type=timeline`.

### RPC

- Single method: `OrderService.GetTimeline(GetTimelineRequest) → GetTimelineResponse`.
- Streaming: `OrderService.StreamTimeline(GetTimelineRequest) → stream TimelineEvent`.

### SDK

- Default export: `import checkout from '@acme/checkout'`.
- Named exports: `import { processCheckout } from '@acme/checkout'`.
- Builder / factory: `import { CheckoutClient } from '@acme/checkout'; const c = new CheckoutClient(opts);`.

### CLI

- Subcommand-shaped: `acme orders timeline <id>`.
- Flag-shaped: `acme orders --timeline <id>`.
- Long-arg-shaped: `acme orders timeline --id=<id>`.

Save to `.temp/task-<slug>/candidates.md`.

## Phase 4 — pick one + rationale

1. **Pick** one candidate.
2. **Justify** in 1-2 paragraphs:
    - Why this candidate fits the use cases best.
    - What constraints in the existing repo / org / industry this honors.
    - What you traded away (and why).
3. **Document Hyrum's Law assumptions**:
    - What the contract GUARANTEES (the named, versioned, supported behavior).
    - What is OBSERVABLE BUT UNSUPPORTED (incidental implementation details that callers MUST NOT depend on, e.g. ordering of fields, exact error messages, response time).
4. **Document validation strategy**: what gets validated at the boundary; what is trusted internally.
5. **Save** to `.temp/task-<slug>/design.md`.
6. **Approval gate** unless `--auto`. (This is the most-valuable gate; the operator may have org context the skill doesn't.)

## Phase 5 — produce the contract artifact

The deliverable. Concrete. Not handwaving.

### REST

OpenAPI YAML fragment for the new / evolved endpoint(s):

```yaml
paths:
  /orders/{id}/timeline:
    get:
      operationId: getOrderTimeline
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: OK
          content:
            application/json:
              schema:
                type: object
                required: [events]
                properties:
                  events:
                    type: array
                    items:
                      $ref: '#/components/schemas/TimelineEvent'
        '404': { description: Order not found }
        '401': { description: Unauthenticated }
```

Saved to either:

- The repo's documented OpenAPI file (working tree edit).
- `.temp/task-<slug>/contract.yaml` if no existing OpenAPI file (and the report recommends "where to land it").

### RPC (Protobuf)

```proto
service OrderService {
  rpc GetTimeline(GetTimelineRequest) returns (GetTimelineResponse);
}

message GetTimelineRequest {
  string order_id = 1;  // UUID
}

message GetTimelineResponse {
  repeated TimelineEvent events = 1;
}

message TimelineEvent {
  string id = 1;          // UUID
  google.protobuf.Timestamp at = 2;
  string type = 3;        // 'created' | 'paid' | 'shipped' | etc.
  string actor = 4;       // user ID or 'system'
}
```

### SDK (TypeScript)

```ts
// in the package's index.ts (or a new exports file)
export interface CheckoutClient {
  initiate(input: InitiateInput): Promise<InitiateResult>;
  finalize(input: FinalizeInput): Promise<FinalizeResult>;
  cancel(orderId: string): Promise<void>;
}

export type InitiateInput = {
  cart: Cart;
  customer: Customer;
};
// …
```

### CLI

```
acme orders timeline <id>

Print the timeline for an order.

ARGS:
  <id>            The order's UUID.

FLAGS:
  --since <duration>    Only events since duration ago. Default: all.
  --json                Output JSON instead of human-readable text.
```

Saved to a `usage.txt` or a Cobra/Commander spec file in the working tree (or `.temp/task-<slug>/contract-cli.txt`).

## Phase 6 — deprecation plan (if `--breaking`)

Required when `--breaking`. Skipped otherwise.

Write `.temp/task-<slug>/deprecation-plan.md`:

- **Old contract** — what's going away; cite the file/version.
- **Migration path** — what callers should switch to. Step-by-step.
- **Deprecation window** — how long the old contract will continue to work. Recommended: at least one major version + 90 days.
- **Warning emission** — for SDK/CLI: when old API is invoked, log a deprecation warning. For REST: include a `Deprecation` HTTP header per RFC 8594.
- **Removal target** — the version / date the old contract goes away.
- **Communication plan** — release notes, doc updates, Slack announcement.

## Phase 7 — report

Write `.temp/task-<slug>/report.md`:

- **Contract** — what was designed; new or evolution; type (REST / RPC / SDK / CLI / types).
- **Use cases** — the 3.
- **Candidates** — 2-3 considered.
- **Picked** — which one + the one-paragraph rationale.
- **Hyrum's Law boundary** — guaranteed vs observable-but-unsupported.
- **Validation strategy** — boundary-only.
- **Contract artifact** — link to the OpenAPI / .proto / .d.ts / CLI spec.
- **Versioning** — version number; semver implications.
- **Deprecation plan** (if applicable) — link to the plan.
- **Decisions** — every auto-pick.
- **Residual risk / follow-ups** — bullet list.
- **Next steps** — typical: `/adk-review:review-code-changes` if the artifact is a working-tree change; `/adk-docs:docs-publish-confluence` if the design needs a published RFC; `/adk-code:code-write` for the implementation behind the contract.

End with the offer-depth question.

## Loop control

- If the operator can't enumerate 3 use cases, push back: "What's use case 2?" Don't proceed with 1.
- If the candidates are all "essentially the same", widen the search; produce 3 genuinely-different options.
- If picking-one is hard because the candidates are too similar, the candidates were the wrong set; revisit Phase 3.
- If the contract evolution requires breaking the existing contract and `--breaking` was NOT set, STOP and ask. Surface that the design implies breaking changes.
