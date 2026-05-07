# `config-update` workflow

Six phases. Phases 0-4 are read-only; phase 5 is the only writer; phase 6 is the report.

## Phase 0 — preflight

```bash
# 0.1 — confirm the file exists
for topic in $TARGETS; do
  if [[ ! -f "$HOME/.config/adk/$topic.md" ]]; then
    echo "ERROR: ~/.config/adk/$topic.md missing — run /adk-core:setup --target $topic"
    exit 1
  fi
done

# 0.2 — confirm the file parses
adk-info --check >/dev/null || {
  echo "ERROR: a meta-info file failed --check; fix the YAML before refreshing"
  exit 1
}

# 0.3 — load operator + repo context for downstream phases
ORG=$(adk-info github default_org)
REPOS_JSON=$(adk-info repos)
```

## Phase 1 — dependency preflight per topic

For each target topic, smoke-ping the source. Mark unreachable topics SKIPPED — never invent.

| Topic | Source | Smoke-ping |
| --- | --- | --- |
| `repos` | `gh` CLI | `gh auth status` + `gh repo list "$ORG" --limit 1` |
| `github` | `gh` CLI | same as above; plus `gh api repos/<org>/<repo>/branches/main/protection` for one repo |
| `datadog` | datadog MCP | `search_datadog_dashboards` with `query: "test"`, `limit: 1` |
| `statsig` | statsig MCP | `Get_List_of_Experiments` with the smallest page size |
| `mixpanel` | workspace Mixpanel connector | `Get-Events` with smallest window |
| `snowflake` | workspace Snowflake connector | `SELECT 1` against the default warehouse |
| `slack`, `info`, `review`, `docs` | n/a | not refreshable; report unchanged |

Record reachable / unreachable per topic. Continue only with reachable ones; the rest are reported as `skipped: source unreachable` in phase 6.

## Phase 2 — per-topic discovery

Walk topics in dependency order: `repos` → `github` → `datadog` → `mixpanel` → `statsig` → `snowflake`. The exact source-to-field mapping lives in `references/source-discovery.md`. Each topic produces three lists:

```
additions  = source - config       # in source, not in config
removals   = config - source       # in config, not in source (PROPOSED only; not executed)
changes    = config ∩ source, value-mismatched
```

Apply `--since <duration>` to the *source* side before diffing. Without `--since`, defaults are documented per topic in `source-discovery.md` (e.g. statsig defaults to "active in last 90 days"; datadog defaults to "any").

## Phase 3 — code cross-reference

Source items that name something the code references must be confirmed in code before they're treated as high-confidence additions:

| Topic | What to grep | Where |
| --- | --- | --- |
| `statsig.common_gates[*].name` | literal gate name | every `repos[*].path` from repos.md |
| `statsig.common_experiments[*].name` | literal experiment name | every `repos[*].path` |
| `mixpanel.common_events[*]` | literal event name | every `repos[*].path` (also as a substring of `track('<name>')` patterns) |
| `datadog.service_aliases[*]` | the canonical service tag | optional — confirm via `search_datadog_services` (recent traffic) |

Implementation: shell out to `rg --fixed-strings --hidden --no-ignore-vcs -- "<name>"` against each repo path. A match in any repo = `code-confirmed: yes`. Zero matches = `code-confirmed: NO`.

For low-confidence additions (in source, not in code), the diff annotates them so the user can decide. Don't auto-skip them — the user might be about to wire the experiment into code.

## Phase 4 — diff per topic

Render a unified diff against the file as it sits on disk. Group by:

- additions (with provenance + code-confirmation)
- proposed removals (with the reason: "absent from source", "concluded N days ago", "no traffic in last 30d")
- changes (current → proposed, with provenance)

If a topic has zero diffs, output a single line: `<topic>.md  no changes proposed`.

## Phase 5 — apply (only under `--fix`)

```
if [[ "$FIX" == "yes" ]]; then
  show consolidated diff
  if [[ "$AUTO" != "yes" ]]; then
    ask "apply these changes to ~/.config/adk/$topic.md?"
  fi
  # Backup the original in memory (NOT to disk — keeps blast radius bounded).
  ORIGINAL=$(cat "$HOME/.config/adk/$topic.md")

  write updated front-matter while preserving:
    - the `---` fences exactly
    - any user-authored fields not touched by additions/removals/changes
    - the `# Notes` body verbatim
    - any `${ENV_VAR}` placeholders verbatim

  # Re-validate.
  if ! adk-info "$topic" --check; then
    echo "$ORIGINAL" > "$HOME/.config/adk/$topic.md"
    echo "ERROR: post-write validation failed; restored original."
    exit 1
  fi
fi
```

Hard rules during write:
- The skill rewrites the YAML front-matter block ONLY.
- The body (`# Notes` and any prose after) is copied through byte-for-byte.
- If a field exists in the file but is unrelated to the diff, copy it through unchanged. Removals are the exception, and only when the user accepted them in phase 5's confirmation step.
- One file at a time. Never write `repos.md` and `datadog.md` in the same atomic step — each topic is its own validate-and-restore boundary.

## Phase 6 — final report

Aggregate per-topic results into the shape from `references/output-format.md`. Under `--auto`, also write `.temp/config-update-report.md` (gitignored).

The report must answer four questions for the user:
1. What changed?
2. What did I refuse to change automatically (and why)?
3. What sources were unreachable?
4. What's the next step (re-run with `--fix`, clone a missing repo, investigate a low-confidence flag)?
