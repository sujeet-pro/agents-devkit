# `code-api` — contract versioning

The One-Version Rule and how to evolve a contract without breaking consumers (or, when you must, with a deprecation window).

## The One-Version Rule

At any point in time, there is ONE canonical version of the contract. Older versions may be supported (during a deprecation window), but only one is "the current contract".

This means:

- A consumer reading the docs / OpenAPI / .proto sees the current version.
- Older versions are documented as "deprecated since version X; will be removed in version Y".
- Server-side, requests to old versions go through a compatibility shim that maps them to the current version.

## Versioning per contract type

### REST APIs

Three options; pick one and stick with it across the org:

| Option | URL pattern | Pros | Cons |
| --- | --- | --- | --- |
| URL prefix | `/v1/orders`, `/v2/orders` | obvious; easy to grep; cache-friendly | URL pollution; harder to default |
| Header | `Accept: application/vnd.acme.v2+json` | clean URLs; per-request granularity | hard to test in browser; requires header discipline |
| Query parameter | `/orders?version=2` | flexible; default-able | non-RESTy; cache invalidation per param |

**Recommended (for org-internal APIs)**: URL prefix. Easiest to grep, easiest for tooling.

**Recommended (for public APIs)**: header (with a documented default). More flexibility for the long term.

### RPC (Protobuf)

Versioning by file:

```
proto/inventory_v1.proto
proto/inventory_v2.proto
```

Or by package within a file:

```proto
package acme.inventory.v1;
package acme.inventory.v2;
```

Field numbers (the wire format) are FOREVER. Once `field_x = 5` ships, that field number is forever associated with that field's type. Removing or repurposing it = breaking change.

**Additive changes** that DON'T require a new version:

- Adding a new field with a new number (with a default value).
- Adding a new RPC method.
- Adding a new enum value (BUT old clients may not handle it).

**Breaking changes** that REQUIRE a new version:

- Removing a field.
- Renaming a field (the wire compatibility is by number, but client code may break).
- Changing a field's type.
- Changing a field's number.
- Changing an enum value's number.

### SDK / module

Use semver (semantic versioning):

- **Patch** (1.0.0 → 1.0.1): bug fix; no API change.
- **Minor** (1.0.0 → 1.1.0): additive; new exports, new methods, new optional fields.
- **Major** (1.0.0 → 2.0.0): breaking changes.

**`exports` field** in `package.json` (Node ecosystem) is the contract. Subpath imports (`import 'pkg/internal'`) that aren't in `exports` are NOT contract — even if they "happen to work".

### CLI

Use semver. Same rules:

- New flag, new subcommand → minor bump.
- Renaming / removing a flag → major bump (requires deprecation).
- Changing a flag's semantics → major bump (requires deprecation).

The `--help` output is the contract; if it changes, that's a contract change.

### GraphQL

GraphQL is "version-less" by convention but supports deprecation:

```graphql
type Order {
  id: ID!
  oldField: String @deprecated(reason: "Use newField; will be removed 2026-08-01")
  newField: String
}
```

The schema is the contract; deprecation is the path; removal is the breaking change.

## Deprecation policies

### REST

Per RFC 8594:

```
HTTP/1.1 200 OK
Deprecation: true
Sunset: Wed, 01 Aug 2026 00:00:00 GMT
Link: <https://docs.acme.com/api/migration-v1-v2>; rel="deprecation"
```

Optionally also a `Warning` header.

### SDK (Node)

```ts
function oldFunction() {
  if (typeof process !== 'undefined' && process.emitWarning) {
    process.emitWarning(
      'oldFunction is deprecated; use newFunction instead. Will be removed in v2.0.',
      'DeprecationWarning'
    );
  }
  // … delegate to new implementation …
}
```

### CLI

```
$ acme migrate run …
WARNING: 'migrate run' is deprecated; use 'migrate' (without 'run').
         Will be removed in 2.0. See: https://docs.acme.com/cli/migration
…
```

Output to stderr (so it doesn't pollute stdout pipelines).

## Deprecation window

The default window in this skill is **at least 1 major version + 90 days**. Operator can override.

For SDK / library: a deprecation in 1.x.x means the deprecated API is removed at the earliest in 2.0.0, AND that 2.0.0 is at least 90 days after the deprecation announcement.

For REST APIs: similar; `Sunset` header date is at least 90 days from when the `Deprecation: true` header started shipping.

For CLI: announce in release notes + emit warning for at least 1 minor before removal in next major.

## Communication

Every breaking change has:

- **Release notes** entry — the canonical "what changed" doc.
- **Migration doc** — step-by-step for consumers.
- **Slack announcement** in the org channel.
- **(if applicable) partner email** — for SDKs / public APIs with known external consumers.

The skill produces these as a list of artifacts in `deprecation-plan.md`; the operator does the actual posting.

## Hyrum's Law in versioning

Even an "additive" change can be observed:

- Adding a field to a JSON response — some caller may be `Object.keys(response).length === 5`. New field = `length 6` = breakage.
- Adding a flag to a CLI — some caller may be parsing `--help` output positionally.
- Adding an enum value — old clients may have an exhaustive switch; new value = unhandled case.

Mitigations:

- **For JSON**: document that the response shape may grow; clients should ignore unknown fields.
- **For CLI**: document that `--help` output is human-readable, not stable; use `--json-help` for machine-readable.
- **For enums**: have a "fallback" / "unknown" value documented; clients should default to it.

Encode these in the contract artifact (doc-comments in OpenAPI / .proto / .d.ts) AND in `design.md` Hyrum's Law caveats.
