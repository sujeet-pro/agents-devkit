# `config-update` — per-topic source discovery

This file is the source-of-truth for "given topic X, what queries do I run, what fields do I update, and how do I cross-reference against code?" The skill reads it as a lookup table.

Topics are listed in the order the workflow walks them.

---

## `repos.md`

**Source:** depends on each configured repo's actual git host.
- `github.com` remotes → `gh` CLI.
- `bitbucket.org` remotes → bitbucket MCP (`mcp__plugin_adk-review_bitbucket__listRepositories`), available when the adk-review plugin is loaded.
- Other hosts (GHE, GitLab, self-hosted) → flag as unsupported; skip refresh.

**Reachable when:** the relevant source is reachable for *every* unique host across the configured repos. If the user's repos span multiple hosts, refresh succeeds per-host and skips the rest.
**Default `--since`:** none (every repo under the default workspace is in scope).

### Discovery queries

First, resolve the host for each configured repo by inspecting its local clone:

```bash
for repo_path in $(adk-info repos --paths); do
  git -C "$repo_path" remote get-url origin
done
# yields one of:
#   git@github.com:<org>/<repo>.git           → github
#   https://github.com/<org>/<repo>.git       → github
#   git@bitbucket.org:<workspace>/<repo>.git  → bitbucket
```

Then dispatch:

```bash
# github.com
ORG=$(adk-info github default_org)
gh repo list "$ORG" --limit 200 --json name,url,defaultBranchRef,pushedAt,isArchived \
  | jq '[.[] | select(.isArchived == false)]'

# bitbucket.org (requires adk-review plugin)
mcp__plugin_adk-review_bitbucket__listRepositories(workspace: "$WORKSPACE")
  → take name, mainbranch.name, updated_on, is_private
  → filter to the active set (not archived / deleted)
```

If a configured repo's host has no available source (e.g. Bitbucket repo but adk-review plugin not loaded), mark the topic SKIPPED with the reason and do NOT delete the entry.

### Fields refreshed

| Field | Action |
| --- | --- |
| `repos[*].name` | additions only — never auto-remove a repo the user listed |
| `repos[*].path` | inferred as `~/code/<org>/<repo>` if a local clone exists at that path; otherwise added with `path: ~/code/<org>/<repo> # not cloned` and flagged in the diff |
| `repos[*].base_branch` | derived from `defaultBranchRef.name` if the user hasn't set it |
| `repos[*].primary_language` | derived from `gh api repos/<org>/<repo>/languages` (top language); never overwrites a user-set value |
| `repos[*].datadog_service` | left blank if the field was never set; users wire this manually |

### Code cross-reference

None. A repo is a repo.

### Anti-rules

- Do NOT add archived repos.
- Do NOT auto-clone. Flag the missing local path; the user runs `gh repo clone` themselves.
- Do NOT remove a repo that's missing from `gh repo list` — it might be an inter-org repo the user has access to via another mechanism.

---

## `github.md`

**Source:** `gh` CLI (CODEOWNERS files + branch protection rules).
**Reachable when:** `gh auth status` OK.
**Default `--since`:** none.

### Discovery queries

```bash
# For each repo in repos.md:
gh api "repos/$ORG/$REPO/contents/.github/CODEOWNERS" --jq '.content' | base64 -d
gh api "repos/$ORG/$REPO/branches/$BASE_BRANCH/protection" \
  --jq '.required_status_checks.contexts'
```

### Fields refreshed

| Field | Action |
| --- | --- |
| `default_pr_reviewers` | suggest the union of CODEOWNERS handles across repos; propose only if the user's current list is empty or marked as a placeholder (`@alice`, `@bob`) |
| `status_check_required` | suggest the *intersection* across repos (a check that ALL repos require) |
| `merge_method` | left alone — user preference |
| `forbid_force_push_branches` | left alone — user policy |
| `pr_template_path`, `codeowners_path` | confirm the paths exist; flag if they don't |

### Code cross-reference

None directly; the source IS the repo metadata.

### Anti-rules

- Do NOT auto-rewrite `default_pr_reviewers` if the user has set named handles different from the template defaults — the user picked them deliberately.
- Do NOT add a status check that only one repo requires; the field is meant for cross-repo defaults.

---

## `datadog.md`

**Source:** Datadog MCP (`mcp__plugin_adk-investigate_datadog__*`).
**Reachable when:** smoke-ping `search_datadog_dashboards` returns 200.
**Default `--since`:** dashboards/monitors filter to "modified in last 90 days"; services filter to "had traffic in last 7 days".

### Discovery queries

```text
# Dashboards
search_datadog_dashboards(query: "", limit: 100)
  → take title, id, modified_at, author
  → filter to favorites + dashboards used in saved Notebooks
  → ignore archived

# Monitors (informational only — written to common_queries[*] of type monitor)
search_datadog_monitors(query: "status:alert OR status:warn", limit: 50)
  → take name, id, query

# Services (for service_aliases validation)
search_datadog_services(env: $DEFAULT_ENV, since: 7d)
  → take service tag, request_count
```

### Fields refreshed

| Field | Action |
| --- | --- |
| `common_dashboards` | additions for dashboards that are top-N by `view_count` in the last 30d AND tagged with the user's team / service. Propose removals for entries no longer present in the source. |
| `common_queries` | additions for queries you can derive from the top monitors; propose removals for queries that reference a metric that no longer has data. |
| `service_aliases.<short>` | propose update if the canonical tag has been renamed (no traffic on old tag, traffic on a near-named new one); propose removal if the aliased tag has zero traffic in 30d. NEVER auto-rename — flag and ask. |
| `slo_thresholds`, `default_env`, `default_window`, `auth.*`, `site` | left alone — user policy. |

### Code cross-reference

For `service_aliases.<short> → <canonical>`, optionally confirm by `search_datadog_services` that the canonical service has recent traffic. Zero traffic → propose removal with the reason "no traffic in last 30 days".

### Anti-rules

- Do NOT add every dashboard in the org. Filter aggressively — a `common_dashboards` entry should be something the on-call actually opens, not noise.
- Do NOT auto-rename `service_aliases` even when confidence is high. Renames can break downstream queries that hardcode the alias name.

---

## `mixpanel.md`

**Source:** workspace Mixpanel connector (`mcp__claude_ai_Mixpanel__*`).
**Reachable when:** `Get-Events` for the configured `project_id` returns a list.
**Default `--since`:** "events fired in the last 30 days".

### Discovery queries

```text
Get-Events(project_id: $PROJECT_ID)
  → take name, total_count_30d
  → sort by total_count_30d desc
  → take top 25
```

### Fields refreshed

| Field | Action |
| --- | --- |
| `common_events` | additions for top-N events by 30d count that are also referenced in code (see cross-reference); propose removals for events with zero hits in 30d AND zero code references. |
| `common_funnels`, `common_cohorts` | left alone — user-defined. |
| `project_id`, `project_token_env`, `default_window`, `identity_property` | left alone — user policy. |

### Code cross-reference

Grep every configured repo path for the literal event name. Add only if found in code. The reasoning: Mixpanel will retain old / experimental event names long after the code removed the call site; only events the code still emits belong in `common_events`.

```bash
for event in "${candidate_events[@]}"; do
  for path in "${repo_paths[@]}"; do
    if rg --fixed-strings --hidden --no-ignore-vcs -- "$event" "$path" >/dev/null; then
      code_refs["$event"]+="$path "
    fi
  done
done
```

### Anti-rules

- Do NOT add an event that's high-volume in the source but not referenced in any configured repo — likely a different team's event.
- Do NOT remove an event the user added that has zero recent volume — they may be tracking an upcoming feature.

---

## `statsig.md`

**Source:** Statsig MCP (`mcp__plugin_adk-investigate_statsig__*`).
**Reachable when:** `Get_List_of_Experiments` returns 200.
**Default `--since`:** experiments — "started in last 90 days OR currently active"; gates — "modified in last 90 days OR currently rolling out".

### Discovery queries

```text
Get_List_of_Experiments()
  → filter status in {active, setup}
  → take id, name, primary_metric, secondary_metrics, started_at

Get_List_of_Gates()
  → filter status in {enabled, partially_rolled_out}
  → take id, name, default_value
```

### Fields refreshed

| Field | Action |
| --- | --- |
| `common_experiments[*]` | additions for active experiments NAMED in code (cross-ref required for high-confidence). Propose removals for experiments concluded > 30 days ago. Update `primary_metric` / `secondary_metrics` if the source value differs. |
| `common_gates[*]` | additions for currently-rolling-out gates referenced in code. Propose removals for gates removed in source. Owner field left alone unless empty. |
| `project`, `console_api_key_env`, `server_secret_env`, `default_environment`, `exposure_metric_conventions.guardrail_metrics` | left alone. |

### Code cross-reference

Mandatory for `common_experiments` and `common_gates`. Grep every configured repo path for the literal name.

- Found in code: `code-confirmed: yes` → high-confidence addition.
- Not found in code: `code-confirmed: NO` → flag in the diff with "in source but never referenced". The user might be about to wire it; don't auto-skip, just annotate.

### Anti-rules

- Do NOT add experiments with status `decided` / `concluded`. The whole point of a refresh is *active* experiments.
- Do NOT add gates that are 100% on or 100% off and have been so for > 90 days — they're effectively code; the user can clean them up via `Start_Gate_Code_Cleanup`.
- Do NOT update `primary_metric` if the user's value matches a known alias (e.g. user wrote `checkout_completed`; source says `checkout_completed_v2`). Flag the divergence; the user picks.

---

## `snowflake.md`

**Source:** workspace Snowflake connector (`mcp__claude_ai_Snowflake__sql_exec_tool`).
**Reachable when:** `SELECT 1` succeeds against the configured warehouse + role.
**Default `--since`:** views — "last queried in last 30 days".

### Discovery queries

```sql
-- Active views (queried recently)
SELECT TABLE_CATALOG, TABLE_SCHEMA, TABLE_NAME
FROM SNOWFLAKE.ACCOUNT_USAGE.OBJECT_DEPENDENCIES
WHERE LAST_ALTERED >= DATEADD(day, -30, CURRENT_TIMESTAMP())
  AND TABLE_TYPE = 'VIEW'
  AND TABLE_SCHEMA IN (<configured schemas>)
ORDER BY LAST_ALTERED DESC;
```

(Fall back to `INFORMATION_SCHEMA.VIEWS` when `ACCOUNT_USAGE` is not granted.)

### Fields refreshed

| Field | Action |
| --- | --- |
| `common_views` | propose additions for views that match the configured schema search path AND were altered in the last 30 days. Propose removals for views absent from `INFORMATION_SCHEMA`. |
| `pii_columns.block_substring`, `block_token_columns` | left alone — policy. |
| `account`, `default_warehouse`, `default_role`, `default_database`, `default_schema_search_path` | left alone — user policy. |

### Code cross-reference

None. A view is a view; if it's in the schema and recently altered, it's a candidate.

### Anti-rules

- Do NOT propose changes to PII guardrail rules. They are policy; the user changes them deliberately or via security review.
- Do NOT propose `default_role` changes — role choice is a security boundary.

---

## Topics NOT refreshable by this skill

These are listed in the report so the user knows they were considered, but the skill does NOT touch them:

- `info.md` — operator profile (name, email, default editor) is a deliberate user choice.
- `slack.md` — channel choice is a deliberate user policy.
- `review.md` — severity bar is preference-driven; only the user / team decides what's a Blocker vs a Critical.
- `docs.md` — Confluence space + GDrive folder are user policy.

If the user explicitly passes `--target info` (or another non-refreshable topic), the skill prints a one-line "not refreshable; nothing to do" and exits cleanly.
