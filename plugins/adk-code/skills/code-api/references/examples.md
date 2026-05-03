# `code-api` — worked examples

## Example 1 — REST endpoint design

**Prompt:** `/adk-code:code-api "design the v2 endpoint set for /orders"`

**Phase 0:** Slug `api-orders-v2`. Repo `~/code/acme/checkout-api`. Type: REST evolution. Status: existing v1 endpoints exist (`GET /orders`, `POST /orders`, etc.).

**Phase 1:** Existing OpenAPI at `openapi.yaml`. v1 endpoints documented there. External consumers: 2 internal services + the storefront app + a partner integration.

**Phase 2 use cases:**

```markdown
## Use cases
1. Storefront: list a buyer's recent orders with status + ETA.
   - Input: buyer auth token; optional date range; pagination.
   - Output: array of OrderSummary {id, status, total, eta}.
   - Errors: 401 unauthenticated.

2. Order admin: search orders across all buyers by status / date / SKU.
   - Input: admin auth; query (status / date range / SKU).
   - Output: paginated array of OrderDetails.
   - Errors: 403 (non-admin); 400 (malformed query).

3. Partner integration: fetch a single order's full detail by external order ID.
   - Input: partner API key; external order ID.
   - Output: OrderFull (with items, payments, shipments).
   - Errors: 404 (not found); 401 (unauthenticated); 403 (not partner's order).
```

**Phase 3 candidates:**

```markdown
## Candidate A — multiple resources
- GET /v2/orders                  → list (use case 1, 2)
- GET /v2/orders/{id}             → detail (use case 3)
Pros: Idiomatic REST; cache-friendly; existing tooling.
Cons: List endpoint must serve 2 use cases (storefront + admin) → query
parameters proliferate.

## Candidate B — separate list endpoints by audience
- GET /v2/buyers/me/orders        → use case 1
- GET /v2/admin/orders            → use case 2
- GET /v2/orders/{id}             → use case 3 (with auth-aware filtering)
Pros: Each endpoint serves one audience; auth + parameter sets diverge naturally.
Cons: Three list-shapes to maintain; consumers must pick the right one.

## Candidate C — single search-shape
- POST /v2/orders:search          → all list cases via body query
- GET /v2/orders/{id}             → detail
Pros: Flexible; expressive; one endpoint to evolve.
Cons: Non-idiomatic REST (POST for search); cache-unfriendly; harder to
GET-share.
```

**Phase 4 picked:** Candidate B.

```markdown
## design.md
Picked: Candidate B (separate list endpoints by audience).

Rationale: each consumer (buyer, admin, partner) has fundamentally
different inputs and authorization needs. Sharing a single list endpoint
across audiences pushes complexity into the parameters; sharing across
two audiences (Candidate A) tries to merge parameter sets that don't
overlap (buyer doesn't search by SKU; admin doesn't filter by their own
buyer ID).

The detail endpoint is shared across audiences with auth-aware filtering
(admin sees all fields; buyer sees their own; partner sees order they own).

Hyrum's Law caveats:
- Guaranteed: the schemas in `components/schemas/Order*` are the contract.
- Observable but unsupported: the order of items in arrays (clients must
  not rely on item ordering); error message text (only error codes are
  contract).
- Observable but unsupported: response time SLAs (informally targeted but
  not part of the contract; SLA is documented separately in datadog.md).

Validation strategy:
- Request bodies validated by the OpenAPI schema at the boundary
  (express-openapi middleware).
- Internal services trust the parsed types and don't re-validate.
- Error responses follow the `Problem+JSON` shape (RFC 7807).

Versioning: v2 prefix in URL. v1 endpoints continue to work. Deprecation
plan in deprecation-plan.md.
```

**Phase 5 artifact:** OpenAPI YAML fragment with the 3 endpoints + the schemas. ~120 lines added to `openapi.yaml`.

**Phase 6 deprecation plan:** `deprecation-plan.md`:

```markdown
## Deprecation
v1 endpoints are deprecated:
- GET /orders → migrate to GET /v2/buyers/me/orders or /v2/admin/orders.
- GET /orders/{id} → migrate to GET /v2/orders/{id}.

Window: v1 stays available until 2026-08-01 (90 days from this design + 1
major version of the SDK). After 2026-08-01, v1 returns HTTP 410 Gone.

Warnings: starting today, v1 responses include `Deprecation: true` header
and `Sunset: 2026-08-01` header per RFC 8594.

Communication: release-notes entry; #api-changes Slack post; partner
integration team email.
```

**Phase 7 report:** Lists the 3 use cases, the 3 candidates, the picked one, the artifact location, and the deprecation plan.

---

## Example 2 — RPC contract between services

**Prompt:** `/adk-code:code-api "design the RPC contract between order-service and inventory-service for stock reservation"`

**Phase 0:** Slug `api-order-inventory-rpc`. Repo `~/code/acme/inventory-service`. Type: RPC (gRPC, per repo convention). Status: NEW (no existing contract).

**Phase 1:** Existing `.proto` files in `proto/`. Read 2 representative ones for style. Naming convention: `<Service>.<Method>`; request/response messages suffixed `Request` / `Response`.

**Phase 2 use cases:**

```markdown
## Use cases
1. Reserve stock for a cart at checkout (the most common path).
   - Input: cart with line items.
   - Output: reservation ID + per-item available quantity.
   - Errors: insufficient stock for one or more items.

2. Release a stock reservation (e.g. when a cart is abandoned).
   - Input: reservation ID.
   - Output: ack.
   - Errors: reservation not found / already released.

3. Confirm a reservation (e.g. after payment succeeds).
   - Input: reservation ID.
   - Output: ack with the confirmed line items.
   - Errors: reservation not found / already confirmed / expired.
```

**Phase 3 candidates:**

```markdown
## Candidate A — three RPCs
- ReserveStock, ReleaseStock, ConfirmStock
Pros: each operation is a clear method; idiomatic gRPC.
Cons: caller orchestrates the lifecycle; risk of orphan reservations.

## Candidate B — single RPC with operation enum
- StockOperation(reservation_id, op: RESERVE | RELEASE | CONFIRM)
Pros: single endpoint to monitor.
Cons: harder to express different inputs (RESERVE needs cart; others
need only ID); over-flexibility.

## Candidate C — three RPCs + auto-expiration
- Same as A, but reservations have a TTL (e.g. 15 min); inventory-service
  auto-releases expired reservations.
Pros: A's clarity + reduces orphan risk via server-side TTL.
Cons: orchestration is now distributed across timer-triggered server
events; harder to reason about.
```

**Phase 4 picked:** Candidate C.

```markdown
## design.md
Picked: Candidate C (three RPCs + auto-expiration).

Rationale: clear lifecycle methods (idiomatic gRPC) plus server-side TTL
mitigates the orphan-reservation risk that plain Candidate A has. The
distributed-state concern is real but bounded — the TTL is short, and
the order-service can always re-reserve if it sees a stale reservation
ID.

Hyrum's Law caveats:
- Guaranteed: the message shapes in InventoryProto.proto.
- Observable but unsupported: the exact reservation ID format
  (caller must treat it as opaque).
- Observable but unsupported: per-item ordering in ReserveStockResponse
  (matches request order today; do not rely).

Validation strategy:
- Request validation at the gRPC handler (proto-defined types + custom
  validation for cart shapes).
- Internal trust between services.

Versioning: this is v1 (new). Future versions: add new RPC methods or
new fields with `optional` keyword (proto3); never re-number fields.
```

**Phase 5 artifact:** A `proto/inventory_v1.proto` file with the 3 messages and 3 RPCs. + the auto-expiration timer is documented (the implementation behind the contract).

**Phase 6 deprecation plan:** N/A — this is a new contract.

**Phase 7 report:** Lists the use cases, candidates, pick, artifact location.

---

## Example 3 — SDK export surface

**Prompt:** `/adk-code:code-api "design the export surface for @acme/checkout package v1"`

**Phase 0:** Slug `api-checkout-sdk-v1`. Repo `~/code/acme/checkout-sdk`. Type: TypeScript SDK. Status: NEW.

**Phase 1:** Empty `src/index.ts`. Read sibling SDK packages in the org for style cues.

**Phase 2 use cases:**

```markdown
## Use cases
1. Initiate a checkout session from a customer-facing app.
   - Input: cart, customer details.
   - Output: a CheckoutSession with redirect URL or in-flow state.
2. Finalize a checkout after the customer completes payment.
   - Input: session ID + payment confirmation token.
   - Output: an Order with status.
3. Cancel an in-flight checkout.
   - Input: session ID.
   - Output: ack.
```

**Phase 3 candidates:**

```markdown
## Candidate A — function-shaped
- export async function initiateCheckout(input): Promise<CheckoutSession>;
- export async function finalizeCheckout(input): Promise<Order>;
- export async function cancelCheckout(sessionId): Promise<void>;
Pros: minimal surface; tree-shakeable.
Cons: state (auth, options) is passed in every call.

## Candidate B — class-shaped
- export class CheckoutClient {
-   constructor(opts: CheckoutClientOpts);
-   initiate(input): Promise<CheckoutSession>;
-   finalize(input): Promise<Order>;
-   cancel(sessionId): Promise<void>;
- }
Pros: shared state (auth, retries) ergonomic.
Cons: not tree-shakeable; ESM stylebook prefers functions.

## Candidate C — hybrid
- export class CheckoutClient { ... } (default)
- export async function initiateCheckout(opts, input) { ... } (functional alt)
Pros: serves both styles.
Cons: two surfaces to maintain; each is the contract.
```

**Phase 4 picked:** Candidate B.

```markdown
## design.md
Picked: Candidate B (class-shaped).

Rationale: the SDK has shared concerns (auth, base URL, retry policy)
that are awkward to thread through every call. The class wraps these.
Tree-shakeability is less important here because the SDK is small
(~60KB) and a typical consumer will use 2-3 methods anyway.

Hyrum's Law caveats:
- Guaranteed: the class methods in CheckoutClient + their request/response
  types.
- Observable but unsupported: internal helper exports (not under
  `export` in index.ts but reachable via deep imports — we explicitly
  reject deep imports as supported).
- Observable but unsupported: the exact request retry timings.

Validation strategy:
- Input types validated by TypeScript at the call site (compile-time).
- Runtime validation only at the network boundary (request bodies
  validated against the API's OpenAPI before sending; responses
  validated on receipt).

Versioning: package follows semver. Breaking changes go in major
versions; deprecations preceded by 1 minor with a deprecation warning.
```

**Phase 5 artifact:** `src/index.ts` and `src/client.ts` with the type defs + `package.json` `"exports"` field declaring only `./index` (no deep imports supported).

**Phase 7 report:** Lists candidates, pick, the artifact path, and a residual risk: "documenting the no-deep-imports rule in the README is the next task; spawn `docs-write`."

---

## Example 4 — CLI flag set

**Prompt:** `/adk-code:code-api "design the CLI flag set for the new 'migrate' command in the cli tool"`

**Phase 0:** Slug `api-cli-migrate`. Repo `~/code/acme/cli`. Type: CLI. Status: NEW command.

**Phase 1:** Existing CLI uses `commander`. Other commands (`import`, `export`, `init`) are 2-level: `acme <command> [args] [flags]`.

**Phase 2 use cases:**

```markdown
## Use cases
1. Migrate from one storage backend to another with full validation.
   - Input: source URL, target URL.
   - Output: count migrated; errors logged.
2. Dry-run a migration (no writes).
   - Input: same as 1; `--dry-run` flag.
   - Output: planned changes; no writes.
3. Resume a partially-completed migration.
   - Input: source / target + a checkpoint file.
   - Output: continues from where it left off.
```

**Phase 3 candidates:**

```markdown
## Candidate A — single command, multiple flags
acme migrate <source> <target> [--dry-run] [--resume-from <file>]
Pros: minimal command tree; one help page.
Cons: dry-run and resume are mutually exclusive but flag conjunctions
might allow both (must validate at runtime).

## Candidate B — subcommands
acme migrate run <source> <target> [--resume-from <file>]
acme migrate dry-run <source> <target>
Pros: clearer separation; subcommand-specific help.
Cons: more typing.

## Candidate C — single command, mode flag
acme migrate <source> <target> --mode (run | dry-run | resume)
Pros: single command + explicit mode.
Cons: less flexible than A; less explicit than B.
```

**Phase 4 picked:** Candidate A.

```markdown
## design.md
Picked: Candidate A (single command, multiple flags).

Rationale: matches the existing CLI's idiom (single command + flags
across `import`, `export`, `init`). Subcommand patterns would diverge
the CLI style. Runtime validation rejects `--dry-run --resume-from` as
incompatible (commander supports custom validation).

Hyrum's Law caveats:
- Guaranteed: the flag names + their semantics in the help text.
- Observable but unsupported: the exact log format on stdout (only
  --json output is contract).

Validation strategy:
- Argument validation at the boundary (commander's built-in checks).
- Custom check for incompatible flag combinations (--dry-run + --resume-from).

Versioning: the CLI follows semver. Removing a flag = major bump; adding
a flag = minor bump (backwards-compatible).
```

**Phase 5 artifact:** A `usage.txt` or commander spec spec embedded in `src/commands/migrate.ts` (the implementation goes via a follow-up `code-write` task).

**Phase 7 report:** Notes that the implementation is a separate `code-write` task; the CLI design just defines the flag set + help text.
