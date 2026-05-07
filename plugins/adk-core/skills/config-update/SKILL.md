---
name: config-update
description: |
  Refresh ~/.config/adk/*.md against live sources to keep drift-prone fields current. Reads each existing meta-info file, queries the topic's source-of-truth (Datadog dashboards/monitors/services, Statsig active experiments + gates, Mixpanel top events, Snowflake schema, GitHub CODEOWNERS + branch protection, local repo paths), cross-references findings against code (greps repos for gate/experiment names, validates aliases against actual service tags), produces a diff per topic, and — under `--fix` — applies non-controversial updates after explicit confirmation. Use when active experiments have changed, a new dashboard / monitor was created, a new repo was onboarded, or a skill complains "service alias X no longer exists in Datadog". Do NOT use to bootstrap missing files (use `/adk-core:setup`). Do NOT use to mutate the source itself (no toggling Statsig gates, no creating Datadog dashboards). Do NOT auto-delete a user-customized field — propose, never remove without consent.
metadata:
  category: meta
  kind: task
  modes: [auto, interactive, fix]
  layer: 0
argument-hint: "[--target <topic|all>] [--mode auto|interactive] [--fix] [--auto] [--since <duration>]"
---

# config-update — refresh meta-info against live sources

Different from `setup`: `setup` creates `~/.config/adk/*.md` from templates the first time. `config-update` keeps the *dynamic* fields inside those files current — the things that drift between runs because they live in external systems (Statsig experiments roll on/off, dashboards get added, repos get onboarded, services get renamed).

Idempotent. Safe to re-run. Read-only against sources; the only writes are to `~/.config/adk/*.md` after explicit confirmation.

## When to use

- "active experiments have changed" — Statsig pulse keeps citing experiments your config doesn't know about.
- "new dashboard / monitor / service" — Datadog auto-discovery is out of date.
- "new repo onboarded" — `gh repo list <org>` shows a repo that's not in `repos.md`.
- A skill complains "service alias `<X>` does not resolve to a Datadog service tag".
- Quarterly housekeeping — fold stale entries out, fold new ones in.

## When NOT to use

- File missing entirely → use `/adk-core:setup --target <topic>` (bootstrap from template first).
- Editing skill code → just edit the file.
- Toggling a Statsig gate, creating a Datadog dashboard, granting Snowflake roles — out of scope (read-only against sources).
- Renaming `info.md` operator details — those are user preference, not source-derived.

## Common prompts

- "refresh adk config"
- "update statsig experiments in adk config"
- "sync datadog dashboards to adk config"
- "config-update --target statsig"
- "my adk config is stale"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `--target <topic\|all>` | optional | `all` (walks every refreshable topic) |
| `--mode auto\|interactive` | optional | `auto` (= one approval gate per topic; not per field) |
| `--fix` | optional | apply the proposed updates after a single confirmation; without `--fix`, only prints the diff |
| `--auto` | optional | skip per-topic confirmation gates; equivalent to `--mode fix` for non-mutation, but still asks once before the first write under `--fix` |
| `--since <duration>` | optional | only consider source items newer than this (e.g. `30d` for "experiments started in last 30 days"); default per topic in `references/source-discovery.md` |

`--fix` is required for any actual write to `~/.config/adk/*.md`. Without it, the skill is purely diagnostic.

## Workflow

```
Phase 0 — prompt expand + preflight
  - Determine target (all topics or single).
  - Verify ~/.config/adk/<topic>.md exists for each target. If missing,
    redirect to /adk-core:setup --target <topic>; do NOT bootstrap from template here.
  - Validate current file: bin/adk-info <topic> --check. If invalid,
    refuse to update — fix the YAML first.

Phase 1 — dependency preflight
  - Per topic, confirm the source MCP / CLI is reachable:
    - datadog → search_datadog_dashboards (smoke ping)
    - statsig → Get_List_of_Experiments (smoke ping)
    - mixpanel → Get-Events (smoke ping)
    - snowflake → information_schema lookup (smoke ping)
    - repos / github → `gh auth status` + `gh repo list <default_org>`
  - If a source isn't reachable, mark the topic SKIPPED in the report; never invent.

Phase 2 — per-topic discovery
  See references/source-discovery.md for the field-by-field rules.
  Per topic, produce three lists:
    - additions    (in source, not in config)
    - removals     (in config, not in source — propose only; do NOT auto-remove)
    - changes      (in both, but the source value differs)

Phase 3 — code cross-reference
  For source items where a code mapping is meaningful:
    - Statsig gate / experiment names → grep every configured repo path
      for the literal name; flag "in source but never referenced in code" as
      a low-confidence addition (probably stale; ask before adding).
    - Datadog service_aliases → confirm the aliased service tag still has
      recent traffic via search_datadog_services.
    - Mixpanel events → grep repos for `track('<event>')` or equivalent.
  This step prevents the config from accumulating dead names that the source
  still lists but the code no longer touches.

Phase 4 — diff per topic
  Render a unified diff against ~/.config/adk/<topic>.md.
  Group by additions / removals / changes.
  Annotate every line with provenance (e.g. "from: statsig.experiments.active",
  "code-confirmed: yes / no").

Phase 5 — apply (only under --fix)
  - Show the consolidated diff once.
  - Ask for confirmation (skipped under --auto --fix; still asks once under --fix alone).
  - Write the updated file (preserve YAML front-matter shape, free-form
    "Notes" body untouched).
  - Re-validate with bin/adk-info <topic> --check.
  - On validation failure, restore from the in-memory original and surface the error.

Phase 6 — final report
  Per topic: changed Y/N, additions count, removals proposed, changes applied,
  code-confirmation rate. Errors and skips are listed separately.
```

## Persona

> You are a careful librarian-of-record. The meta-info files are the user's contract with adk; you treat every line they wrote as a deliberate choice. You add, you suggest removals, you NEVER silently delete.

See `references/persona.md`.

## Constitution

**Must do:**

1. Be idempotent — running twice in a row produces the same result.
2. Refuse to bootstrap. If `~/.config/adk/<topic>.md` is missing, tell the user to run `/adk-core:setup --target <topic>` first.
3. Validate the current file before proposing changes (`bin/adk-info <topic> --check`).
4. Validate the proposed file after writing; restore on failure.
5. Show a unified diff before any write — not a vague summary.
6. Cross-reference source-derived names against code where applicable (gates, experiments, events). Flag "in source but no code reference" as low-confidence.
7. Preserve user-authored fields. The `# Notes` free-form body is never rewritten.
8. Preserve `${ENV_VAR}` placeholders exactly. Never resolve them into raw values during the rewrite.
9. Quote provenance for every proposed change (which source, which query, which code reference).

**Must not do:**

1. Auto-delete entries the user added manually. Removals are always *proposed*; the user accepts them or they stay.
2. Mutate the source — no toggling Statsig gates, no creating Datadog dashboards, no Snowflake DDL, no `gh repo create`.
3. Write a raw secret into `~/.config/adk/*.md`. Same regex check as `setup` enforces.
4. Bootstrap a missing file. That's `setup`'s job.
5. Touch files outside `~/.config/adk/`.
6. Apply changes without `--fix`. Without it, the skill is pure diagnostic.
7. Skip the code cross-reference for gate / experiment / event names — the whole point is to map source to code.
8. Run when the topic file failed `bin/adk-info <topic> --check` — fix the YAML first.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Refreshing `info.md` (operator profile) — those fields are intentional, not source-derived.
- Auto-removing the user's hand-written `service_aliases` because they're not in `search_datadog_services`. The user named them; suggest, don't remove.
- Adding every Statsig experiment ever, including completed and decided ones. Filter by status (`active` or `setup`) and by `--since`.
- Resolving `${ENV_VAR}` placeholders during the rewrite (turns the file into a secret store).
- Treating the source as gospel. Datadog has dashboards no human uses; Statsig has half-finished experiments; Mixpanel has misnamed events. Code cross-reference is the truth-check.
- Over-eager removals. Out-of-source != stale; the user may have added a synthetic alias intentionally.
- Running without confirming `bin/adk-info <topic> --check` first. Garbage-in, garbage-out.

## Output

A per-topic report. Without `--fix`, this is the entire output. With `--fix`, the report is followed by a "wrote ~/.config/adk/<topic>.md (validated)" line per applied topic.

```
[adk-core:config-update] target=all mode=auto fix=no since=30d

datadog.md
  source: datadog mcp                                                    reachable
  current entries: 2 dashboards, 2 queries, 3 service aliases
  code refs scanned in: acme/checkout-api, acme/storefront, acme/search-api
  proposed changes:
    + common_dashboards: "Cart Abandonment SLO" (id ghi-789)             provenance: search_datadog_dashboards
    + common_queries:    "p99 by service"                                provenance: top by hit-count last 30d
    ~ service_aliases.search → "search-api-v2" (was "search-api")        provenance: search-api retired 2026-04-12
    - service_aliases.legacy_orders                                      proposed removal: no traffic in last 30d
  code-confirmation rate: 5/5 (100%)
  apply? not under --fix; re-run with --fix to write.

statsig.md
  source: statsig mcp                                                    reachable
  current entries: 2 experiments, 2 gates
  code refs scanned in: acme/checkout-api, acme/storefront, acme/search-api
  proposed changes:
    + common_experiments: "checkout_express_lane"                        provenance: status=active, started 2026-04-22
                                                                          code-confirmed: yes (acme/storefront/src/checkout/Express.tsx:42)
    + common_experiments: "search_ranker_v4"                             provenance: status=active
                                                                          code-confirmed: NO — flag for review (low confidence)
    - common_experiments: "checkout_funnel_v3"                           proposed removal: status=concluded 2026-04-15
    + common_gates: "express_checkout_killswitch"                        code-confirmed: yes (acme/storefront/src/lib/flags.ts:18)
  code-confirmation rate: 2/3 (67%)
  apply? not under --fix; re-run with --fix to write.

repos.md
  source: gh repo list acme                                              reachable
  current entries: 3 repos
  proposed changes:
    + repos: acme/payments-svc (new repo, last commit 2026-04-30)        path inferred: ~/code/acme/payments-svc (NOT FOUND locally)
                                                                          flagged: clone first or skip
  apply? not under --fix; re-run with --fix to write.

mixpanel.md   skipped: source unreachable (workspace mixpanel connector not configured)
snowflake.md  no changes proposed (current entries match information_schema)
github.md     no changes proposed
slack.md      not refreshable by this skill (channels are user-chosen)
info.md       not refreshable by this skill (operator profile)
review.md     not refreshable by this skill (preference-driven)
docs.md       not refreshable by this skill (preference-driven)

doctor: 1 warning, 0 errors
  - mixpanel.md skipped — workspace mixpanel connector unreachable

next steps:
  1. Re-run with --fix to apply proposed changes after review.
  2. Investigate "search_ranker_v4" (in source but not referenced in code).
  3. Either clone acme/payments-svc into ~/code/acme/ or skip the addition.
```

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The librarian-of-record persona |
| `references/workflow.md` | Detailed phases (preflight → discovery → diff → apply) |
| `references/source-discovery.md` | Per-topic source mapping and code cross-reference rules |
| `references/clarifying-questions.md` | Per-topic confirmations |
| `references/output-format.md` | Report shape |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked examples (statsig refresh, repo onboarding, datadog drift) |
| `references/modes.md` | auto + interactive + fix |
| `references/interaction-contract.md` | Canonical interaction contract (mirrored) |
