# Hyrum's Law audit — observable-behavior checklist

> *"With a sufficient number of users of an API, it does not matter what you promise in the contract: all observable behaviors of your system will be depended on by somebody."* — Hyrum Wright

The point of this checklist is to **decide explicitly** which observable behaviors are part of the contract and which are not — and to **document the not-in-contract ones in plain text** so future-you (and consumers) cannot pretend otherwise.

## Run this list against any new or evolved interface

For each item, mark one of:

- **CONTRACT** — promised; consumers may depend on it; changes are versioned/deprecated.
- **NOT CONTRACT** — visible but explicitly subject to change; documented as such.
- **N/A** — does not apply to this surface.

| # | Observable behavior | Common consumer dependency | Default classification |
| --- | --- | --- | --- |
| 1 | Field order in JSON responses | Snapshot tests, regex parsers | NOT CONTRACT (most JSON parsers are unordered, but be explicit) |
| 2 | Default values of optional fields | Consumer code that doesn't read a field, assuming the default | CONTRACT — change requires migration |
| 3 | Exact error `message` strings | Consumer code branching on the message | NOT CONTRACT (consumers must branch on `code`) |
| 4 | Set of error `code` values | Switch statements / typed enums on the consumer | CONTRACT (new codes additive; removed codes breaking) |
| 5 | Status code mapping per error class | Generic retry / fallback logic on the consumer | CONTRACT |
| 6 | `Retry-After` header presence/value | Backoff schedulers | CONTRACT if you ever set it; NOT CONTRACT only if always absent |
| 7 | Pagination cursor format | Cursor parsing in the consumer | NOT CONTRACT (treat as opaque) — but document opacity |
| 8 | Response timing / latency | Timeouts, race-condition workarounds | NOT CONTRACT (no SLO promised here) — call out separately if SLOs exist |
| 9 | Order of items in a list response | "Latest first" assumptions | CONTRACT if you sort; NOT CONTRACT if explicitly unordered |
| 10 | Whether 404 vs 403 is returned for missing+forbidden resources | Existence-leak detection | CONTRACT (changing is a security-impacting breaking change) |
| 11 | Log line shape | Log-based monitoring downstream | NOT CONTRACT — but if you publish them, you de facto promised them |
| 12 | Request ID format | Trace correlation | NOT CONTRACT (treat as opaque string) |
| 13 | Maximum payload size | Clients that batch | CONTRACT — change requires migration |
| 14 | Acceptable `Content-Type` values on input | Consumers sending alternative formats | CONTRACT |
| 15 | Strictness of input parsing (e.g. extra fields ignored vs rejected) | Lazy consumers sending stale fields | Pick one and lock it; documented either way |
| 16 | Case sensitivity of identifiers | Consumers normalizing IDs differently | CONTRACT |
| 17 | Whitespace / unicode normalization in string fields | Consumers comparing strings exactly | CONTRACT — document the normalization rule (NFC, trim, etc.) |
| 18 | Idempotency of POST | Retry loops | CONTRACT (yes/no) — and if yes, the key, scope, and TTL |
| 19 | Cache-control headers | CDNs, browser caches | CONTRACT |
| 20 | OPTIONS / CORS preflight behavior | Browser callers | CONTRACT (specify allowed origins, methods, headers) |

## Output

Save the completed audit to `.temp/task-<slug>/notes/api-<slug>-hyrums-audit.md` with three columns:

```markdown
| # | Behavior | Classification | Note |
| --- | --- | --- | --- |
| 1 | Field order in JSON | NOT CONTRACT | Documented as "fields may be re-ordered" in the OpenAPI description |
| 2 | Default for `notify_on_create` | CONTRACT | Default `true`; flipping it is a breaking change |
| ... | ... | ... | ... |
```

The act of filling this out is the value — even when 80% are NOT CONTRACT, you've made the choice on purpose.
