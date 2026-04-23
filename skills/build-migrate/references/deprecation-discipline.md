# Deprecation discipline — Hyrum's Law, advisory vs compulsory, churn rule

Optional reference loaded by `build-migrate` when the migration includes removing or replacing existing API surface. Encodes the "code is a liability" discipline.

## Code is a liability

Every line of code has carrying cost: it must be read, tested, secured, kept compatible, and eventually removed. Code that no one uses still costs maintenance. **Removing code is a net win — when done correctly.**

## Hyrum's Law and removal cost

> *"With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody."*

The cost of removing or changing code scales with the number of dependents — INTERNAL and EXTERNAL — and with what they observe. Before removing or changing anything user-visible:

- List internal call sites (grep / call-graph).
- List external consumers (other services, partner integrations, public docs, SDKs).
- For each, identify what observable behavior they likely depend on (status codes, response shape, error messages, timing, log lines).
- Use the **Hyrum's Law audit** from `@adk:build-api`'s `references/hyrums-law-audit.md` if any of those behaviors are part of an interface.

## Advisory vs compulsory deprecation

Two distinct modes — pick one explicitly.

| Mode | Audience | Mechanism | Removal trigger |
| --- | --- | --- | --- |
| **Advisory** | Internal callers OR users you can nudge | Logged warning / typed `@deprecated` / docs note | When the team decides; no forced timeline |
| **Compulsory** | Required by security / cost / external mandate | Removed-by date communicated; code path returns error after the date | The communicated date |

Advisory is the default for internal monorepo migrations. Compulsory is for external APIs with real cost (security CVE, vendor sunset, infra retirement).

## The churn rule

> The team that owns the API is responsible for migrating its users — not the other way around.

If you're the API owner and you change the API, you don't get to say "users will figure it out." You:

1. Provide the replacement first, working and proven.
2. Migrate as many internal callers as you can.
3. Communicate the change to external callers with a real timeline.
4. Provide a migration guide (`docs/migrations/<from>-to-<to>.md`) with code examples.
5. Run a usage telemetry to see when the deprecated path is fully unused.
6. Remove the old code only when telemetry says it's safe.

## Migration patterns

### Strangler fig

Stand up the new system next to the old one. Route requests to the new one progressively. Decommission the old one once traffic is fully shifted.

- Best for: large architectural replacements (monolith → service split).
- Risk: long parallel-running period; double the operational surface.

### Adapter pattern

Add a thin layer that translates between old and new interfaces. Old callers keep working unchanged; new code uses the new interface.

- Best for: API renames, signature changes, vocabulary shifts.
- Risk: adapter becomes permanent if removal isn't tracked.

### Feature flags / dark launches

Deploy the new path behind a flag, dark-launch traffic to it, compare results, then flip.

- Best for: behavior changes that need real-traffic validation.
- Risk: flag accumulates; cleanup is mandatory (see `@adk:publish-ship`'s flag lifecycle).

### Big-bang migration (avoid)

Replace everything in one PR. Fast in theory; brittle in practice. Reserve for genuinely small, low-blast-radius changes.

## Zombie code

Zombie code is code that:

- Has no production traffic (verified by telemetry).
- Has no tests (or tests that test the zombie itself, in a tautology).
- Has no documentation explaining why it's still there.

Response:

- Confirm zero usage with telemetry over a meaningful window (≥ 1 month for low-traffic systems; ≥ 1 week for high-traffic).
- Add a removal commit. The diff is the proof.
- Update CHANGELOG / release notes.

## Anti-patterns

- "It still works, why remove it?" — code that works has carrying cost (security, dep upgrades, mental load).
- "Someone might need it later" — they can resurrect it from git; deletions are reversible.
- "The migration is too expensive" — the carrying cost compounds; each year delayed is more expensive.
- "We'll deprecate after we finish the new system" — no, the new system needs the migration to go all the way.
- "Users will migrate on their own" — the data says they won't; you have to drive it.
- "We can maintain both systems indefinitely" — every divergence makes both more expensive.

## Verification

- Migration guide exists.
- Internal callers migrated, verified by grep + telemetry.
- External callers notified with real timelines (advisory) or removed-by date (compulsory).
- Old code path removed AND old tests AND old docs AND deprecation notice.
- CHANGELOG / release notes updated.
- Zero-usage telemetry shown.
