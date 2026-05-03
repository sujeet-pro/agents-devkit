# `code-api` — anti-patterns

## Validation theatre

- **"We'll add validation everywhere, just in case."** That's how trust collapses. Inner functions stop trusting their callers; defensive code multiplies. The contract should validate at the BOUNDARY (the HTTP request handler, the SDK entry point, the CLI flag parser); inner code trusts the validated input.
- **Same validation in 4 layers.** "Defense in depth" used as the rationale; in practice, drift between the layers means some layers reject what others accept.
- **Validation that doesn't match the schema.** The OpenAPI says `email: format: email` but the handler accepts `email: any-string`. The OpenAPI is not the source of truth; bad.

## Hyrum's Law violations

- **Adding fields to a response and assuming nobody reads the absence.** Some external caller may be testing `if (!response.foo) { … }` — your new `foo` breaks them.
- **Changing the order of fields in a JSON response.** Some caller may be parsing positionally (rare but real). Hyrum's Law eats this.
- **Tightening field validation.** "We used to accept any string for `email`; now we accept only valid emails." That's a breaking change for callers who rely on the old behavior — even if "the old behavior was a bug".
- **Changing error messages.** Some caller may be `if (response.error.message === "Invalid email")`. Don't change error message text without versioning.

## Two near-duplicate endpoints

- **`/orders/list` and `/orders/index`** doing nearly the same thing because nobody wanted to touch the existing `/orders/list`. The contract is now bigger and more confusing without serving more use cases.
- **`getUser(id)` AND `fetchUser(id)`** because someone wrote `fetch` and the existing one was `get`. Pick one; deprecate the other.
- **Multiple "v2" endpoints** when v1 was nearly fine. Distinguish "evolution" (additive, backward-compatible) from "breaking change" (new version).

## Breaking changes without deprecation

- **Removing a field overnight.** Even if "no callers use it" — that's hard to prove. Add a `Deprecation` header / log a warning / announce; wait a window; remove.
- **Renaming a field.** Same: keep the old name as an alias for a deprecation window.
- **Changing the type of a field** (string → object, array → object, etc.). Big breaking change; treat it as a new endpoint, not an evolution.
- **Removing an enum value.** Callers may be testing the value; removal silently breaks them.

## Designing without use cases

- **"Let's design v2 of the orders API."** What use cases? Without use cases, you'll over- or under-design.
- **"This will be more flexible."** Flexibility is not a feature; it's a cost. Each axis of flexibility is more code, more docs, more tests.
- **"We'll add fields as we need them."** Fine for additive growth; not fine as a substitute for upfront design when there's a known set of consumers.

## Design-by-implementation

- **"The contract is whatever the code does."** Then the implementation drives consumers; Hyrum's Law eats every accidental behavior.
- **No OpenAPI / .proto / .d.ts file.** The "contract" lives in the reader's head; consumers diverge from each other.
- **The OpenAPI is auto-generated from code annotations** but never reviewed. Design is happening in the code, not in the spec.
- **Documentation is the contract.** Docs lie; they go stale; they don't gate consumers. The OpenAPI / .proto / .d.ts is the contract.

## Versioning anti-patterns

- **Mixing v1 and v2 in the same endpoint surface** without a clear separator (URL prefix, header, parameter). Consumers can't tell which they're hitting.
- **Versioning by header without a clear default.** `Accept: application/vnd.acme.v2+json` is fine if there's a documented default.
- **Implicit versioning ("we'll just add fields, nobody's depending on the absence").** That's the Hyrum's Law trap.
- **Floating "latest"** as a version. `?version=latest` causes silent breakage when "latest" rolls forward.

## Over-flexibility

- **A single endpoint that takes 47 optional query parameters** to handle every possible use case. The contract becomes hard to test; consumers become hard to validate.
- **`Generic<T>` where `T` could be anything.** Without constraints, the type is no help.
- **A single CLI command with 23 flags.** Subcommands exist for a reason.

## Under-flexibility

- **Hard-coding a 100-item return limit** where some callers need 1000. Adding pagination after the fact is a breaking change.
- **Returning fields by name only.** Some callers want id-shaped references; some want embedded objects. Plan the embedding strategy.
- **No `nextPageToken` / cursor.** Adding pagination after the fact is awkward.

## Internal-vs-public confusion

- **Treating an internal-only contract** (between two services in the same repo, behind a firewall) **as if it were public.** Over-engineering; over-specification; slow iteration.
- **Treating a public SDK** (used by external customers) **as if it were internal.** Breaking changes ship without warning; customers get angry.

## Reporting

- **Burying the rationale in implementation details.** The rationale is the most-read part of `design.md`.
- **Hiding "what we considered and rejected".** Reviewers want to know.
- **Saying "all use cases supported" without listing them.**
- **Not documenting Hyrum's Law caveats.** Future-you will be glad you did.
