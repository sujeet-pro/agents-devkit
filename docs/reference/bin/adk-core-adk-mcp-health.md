---
title: 'adk-core:adk-mcp-health'
description: 'Helper binary adk-mcp-health from adk-core.'
plugin: 'adk-core'
binary: 'adk-mcp-health'
source: 'plugins/adk-core/bin/adk-mcp-health'
group: 'core-bin'
order: 402
---
# adk-core:adk-mcp-health

## Source

`plugins/adk-core/bin/adk-mcp-health`

## Contents

```text
#!/usr/bin/env bash
# adk-mcp-health — report which MCPs are reachable and which env vars are missing.
#
# Usage:
#   adk-mcp-health             # full report (workspace + shipped + env vars)
#   adk-mcp-health --workspace # workspace connectors only
#   adk-mcp-health --shipped   # adk-shipped MCPs only
#   adk-mcp-health --env       # env-var presence only
#   adk-mcp-health --desktop   # print Claude Desktop connector guidance
#   adk-mcp-health --json      # machine-readable JSON output
#
# Reads:
#   - `claude mcp list` (source of truth for connector status)
#   - process env (for ${VAR} placeholders referenced by .mcp.json files)
#
# Never prints env-var VALUES — only their presence/absence.

set -uo pipefail

MODE=full
JSON=0
DESKTOP=0
for arg in "$@"; do
  case "$arg" in
    --workspace) MODE=workspace ;;
    --shipped)   MODE=shipped ;;
    --env)       MODE=env ;;
    --desktop)   DESKTOP=1 ;;
    --json)      JSON=1 ;;
  esac
done

WORKSPACE_CONNECTORS=(
  "Atlassian"
  "Google Drive"
  "Gmail"
  "Google Calendar"
  "Slack"
  "Mixpanel"
  "Snowflake"
)

SHIPPED_MCPS=(
  "github"
  "datadog"
  "statsig"
)

ENV_VARS=(
  "GITHUB_PAT"
  "GITHUB_TOOLSETS"
  "GITHUB_READ_ONLY"
  "DD_API_KEY"
  "DD_APP_KEY"
  "DD_SITE"
  "STATSIG_CONSOLE_API_KEY"
)

mcp_list_output=""
if command -v claude >/dev/null 2>&1; then
  mcp_list_output="$(claude mcp list 2>/dev/null || true)"
fi

mcp_status() {
  local name="$1"
  if [[ -z "$mcp_list_output" ]]; then echo "unknown"; return; fi
  if echo "$mcp_list_output" | grep -iq "$name.*Connected"; then echo "connected"; return; fi
  if echo "$mcp_list_output" | grep -iq "$name"; then echo "configured"; return; fi
  echo "not-configured"
}

env_status() {
  local var="$1"
  if [[ -n "${!var-}" ]]; then echo "present"; else echo "MISSING"; fi
}

if (( JSON )); then
  printf '{\n'
  if [[ "$MODE" == "full" || "$MODE" == "workspace" ]]; then
    printf '  "workspace_connectors": {\n'
    for i in "${!WORKSPACE_CONNECTORS[@]}"; do
      n="${WORKSPACE_CONNECTORS[$i]}"
      printf '    "%s": "%s"' "$n" "$(mcp_status "$n")"
      [[ $i -lt $((${#WORKSPACE_CONNECTORS[@]} - 1)) ]] && printf ','
      printf '\n'
    done
    printf '  },\n'
  fi
  if [[ "$MODE" == "full" || "$MODE" == "shipped" ]]; then
    printf '  "shipped_mcps": {\n'
    for i in "${!SHIPPED_MCPS[@]}"; do
      n="${SHIPPED_MCPS[$i]}"
      printf '    "%s": "%s"' "$n" "$(mcp_status "$n")"
      [[ $i -lt $((${#SHIPPED_MCPS[@]} - 1)) ]] && printf ','
      printf '\n'
    done
    printf '  },\n'
  fi
  if [[ "$MODE" == "full" || "$MODE" == "env" ]]; then
    printf '  "env_vars": {\n'
    for i in "${!ENV_VARS[@]}"; do
      v="${ENV_VARS[$i]}"
      printf '    "%s": "%s"' "$v" "$(env_status "$v")"
      [[ $i -lt $((${#ENV_VARS[@]} - 1)) ]] && printf ','
      printf '\n'
    done
    printf '  }\n'
  fi
  printf '}\n'
  exit 0
fi

printf '[adk-mcp-health] platform=%s\n' "$(uname -s | tr '[:upper:]' '[:lower:]')"
if (( DESKTOP )); then
  echo "Claude Desktop note: plugin-local .mcp.json files are not loaded by Desktop."
  echo "Configure required custom MCPs/connectors in Desktop or your workspace before running dependent skills."
fi

if [[ "$MODE" == "full" || "$MODE" == "workspace" ]]; then
  echo "- workspace connectors:"
  for n in "${WORKSPACE_CONNECTORS[@]}"; do
    s="$(mcp_status "$n")"
    case "$s" in
      connected)       printf '  - %-22s ✓ Connected\n' "$n" ;;
      configured)      printf '  - %-22s ⚠ Configured (not connected)\n' "$n" ;;
      not-configured)  printf '  - %-22s ✗ Not configured\n' "$n" ;;
      *)               printf '  - %-22s ? (claude CLI not available)\n' "$n" ;;
    esac
  done
fi

if [[ "$MODE" == "full" || "$MODE" == "shipped" ]]; then
  echo "- shipped MCPs:"
  for n in "${SHIPPED_MCPS[@]}"; do
    s="$(mcp_status "$n")"
    case "$s" in
      connected)       printf '  - %-22s ✓ Connected\n' "$n" ;;
      configured)      printf '  - %-22s ⚠ Configured (not connected; check env vars)\n' "$n" ;;
      not-configured)
        if (( DESKTOP )); then
          printf '  - %-22s ✗ Configure as a Desktop custom connector (plugin .mcp.json ignored)\n' "$n"
        else
          printf '  - %-22s ✗ Not configured (.mcp.json not loaded?)\n' "$n"
        fi
        ;;
      *)               printf '  - %-22s ? (claude CLI not available)\n' "$n" ;;
    esac
  done
fi

if [[ "$MODE" == "full" || "$MODE" == "env" ]]; then
  echo
  echo "env vars referenced by adk plugins:"
  for v in "${ENV_VARS[@]}"; do
    s="$(env_status "$v")"
    if [[ "$s" == "present" ]]; then
      printf '  - %-26s present\n' "$v"
    else
      case "$v" in
        GITHUB_PAT)             hint='(mint at https://github.com/settings/personal-access-tokens/new)' ;;
        DD_API_KEY|DD_APP_KEY)  hint='(see https://app.datadoghq.com/organization-settings/)' ;;
        DD_SITE)                hint='(default datadoghq.com)' ;;
        STATSIG_CONSOLE_API_KEY) hint='(mint at https://console.statsig.com/api_keys)' ;;
        *)                      hint='' ;;
      esac
      printf '  - %-26s MISSING %s\n' "$v" "$hint"
    fi
  done
fi
```
