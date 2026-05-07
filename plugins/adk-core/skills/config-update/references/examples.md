# `config-update` — examples

## Example 1 — quarterly housekeeping (default mode, no `--fix`)

```text
/adk-core:config-update
```

**Phase 0:** all 10 meta-info files present and pass `--check`.

**Phase 1:** smoke-pings — datadog OK, statsig OK, mixpanel unreachable (workspace connector not configured), snowflake OK, gh OK.

**Phase 2 + 3:** per-topic discovery + code cross-reference.

**Phase 4 (diff):**

```
[adk-core:config-update] target=all mode=auto fix=no since=defaults

repos.md
  source: gh repo list acme                                              reachable
  current entries: 3 repos
  proposed changes:
    + repos: acme/payments-svc (new repo, last commit 2026-04-30)        path inferred: ~/code/acme/payments-svc (NOT FOUND locally)
                                                                          flagged: clone first or skip
  apply? not under --fix; re-run with --fix to write.

github.md     no changes proposed
datadog.md
  source: datadog mcp                                                    reachable
  current entries: 2 dashboards, 2 queries, 3 service aliases
  proposed changes:
    + common_dashboards: "Cart Abandonment SLO" (id ghi-789)             provenance: search_datadog_dashboards (top by view_count, last 30d)
  apply? not under --fix; re-run with --fix to write.

mixpanel.md   skipped: source unreachable (workspace mixpanel connector not configured)

statsig.md
  source: statsig mcp                                                    reachable
  current entries: 2 experiments, 2 gates
  code refs scanned in: acme/checkout-api, acme/storefront, acme/search-api
  proposed changes:
    + common_experiments: "checkout_express_lane"                        provenance: status=active, started 2026-04-22
                                                                          code-confirmed: yes (acme/storefront/src/checkout/Express.tsx)
    - common_experiments: "checkout_funnel_v3"                           proposed removal: status=concluded 2026-04-15
  code-confirmation rate: 1/1 (100%)
  apply? not under --fix; re-run with --fix to write.

snowflake.md  no changes proposed
slack.md      not refreshable by this skill (channels are user-chosen)
info.md       not refreshable by this skill (operator profile)
review.md     not refreshable by this skill (preference-driven)
docs.md       not refreshable by this skill (preference-driven)

doctor: 1 warning, 0 errors
  - mixpanel.md skipped — workspace mixpanel connector unreachable

next steps:
  1. Re-run with --fix to apply proposed changes after review.
  2. Either clone acme/payments-svc into ~/code/acme/ or skip the addition.
  3. Configure workspace mixpanel connector to refresh mixpanel.md.
```

User reviews, decides everything looks reasonable, re-runs with `--fix`.

---

## Example 2 — Statsig active experiments rolled over

```text
/adk-core:config-update --target statsig --fix
```

**Phase 0-3:** existing config has 4 experiments listed; only 1 is still active. Source has 5 active experiments; 3 are referenced in code.

**Phase 4 (diff):**

```
statsig.md
  source: statsig mcp                                                    reachable
  current entries: 4 experiments, 2 gates
  code refs scanned in: acme/checkout-api, acme/storefront, acme/search-api
  proposed changes:
    + common_experiments: "search_ranker_v4"                             provenance: status=active, started 2026-03-30
                                                                          code-confirmed: yes (acme/search-api/src/ranker/v4.kt)
    + common_experiments: "checkout_express_lane"                        provenance: status=active, started 2026-04-22
                                                                          code-confirmed: yes (acme/storefront/src/checkout/Express.tsx)
    + common_experiments: "pricing_psych_99"                             provenance: status=active, started 2026-04-28
                                                                          code-confirmed: NO — flag for review (low confidence)
    - common_experiments: "checkout_funnel_v3"                           proposed removal: status=concluded 2026-04-15
    - common_experiments: "pdp_image_carousel"                           proposed removal: status=concluded 2026-03-01
    - common_experiments: "header_redesign"                              proposed removal: status=concluded 2026-02-12
  code-confirmation rate: 2/3 (67%)
```

**Phase 5 (apply, `--fix` is set):**

The skill asks first about `pricing_psych_99` (low confidence): "in source but not referenced in any configured repo. Add anyway?" — user says NO.

Then asks about each removal in turn. User accepts the two old ones; says NO to `header_redesign` because they're tracking historical context.

Final write contains the two confirmed additions and two confirmed removals; `pricing_psych_99` and `header_redesign` are NOT written.

Post-write `--check` passes. Report ends with:

```
statsig.md  applied (validated). 2 added, 2 removed.

doctor: 0 warnings, 0 errors

next steps:
  1. Investigate "pricing_psych_99" — is it about to be wired up, or is the experiment off-roadmap?
```

---

## Example 3 — Datadog service rename

```text
/adk-core:config-update --target datadog
```

**Phase 1:** datadog mcp reachable.
**Phase 2:** `service_aliases.search → search-api` exists in config; `search_datadog_services` shows 0 traffic on `search-api` and high traffic on `search-api-v2`.

**Phase 4:**

```
datadog.md
  source: datadog mcp                                                    reachable
  proposed changes:
    ~ service_aliases.search → "search-api-v2" (was "search-api")        provenance: search-api 0 req/min for 14d; search-api-v2 1.2k req/min
  code-confirmation rate: n/a
  apply? not under --fix; re-run with --fix to write.

next steps:
  1. Re-run with --fix to apply.
  2. Verify: any saved Datadog dashboards / monitors that hardcode "search-api" will need updating after this rename.
```

User runs `/adk-core:config-update --target datadog --fix`, accepts the change. The skill rewrites the front-matter, preserves the `# Notes` body, and re-validates.

---

## Example 4 — refusing to bootstrap

```text
/adk-core:config-update --target docs
```

User has never created `~/.config/adk/docs.md`.

```
ERROR: ~/.config/adk/docs.md missing.
       This skill refreshes existing files; it does NOT bootstrap from templates.
       Run: /adk-core:setup --target docs
```

Skill exits with non-zero status. The user runs `setup --target docs`, fills the template, then comes back and runs `config-update` if needed (though `docs.md` is preference-driven and the skill will report it as "not refreshable" anyway).

---

## Example 5 — repeat run, nothing changed

```text
/adk-core:config-update --auto
```

```
[adk-core:config-update] target=all mode=auto fix=no since=defaults

repos.md      no changes proposed
github.md     no changes proposed
datadog.md    no changes proposed
mixpanel.md   no changes proposed
statsig.md    no changes proposed
snowflake.md  no changes proposed
slack.md      not refreshable by this skill (channels are user-chosen)
info.md       not refreshable by this skill (operator profile)
review.md     not refreshable by this skill (preference-driven)
docs.md       not refreshable by this skill (preference-driven)

doctor: 0 warnings, 0 errors
```

Idempotent — nothing changed, nothing asked, nothing written.
