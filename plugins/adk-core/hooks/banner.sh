#!/usr/bin/env bash
# adk-core SessionStart banner — print the active plugins, loaded meta-info, MCP health summary.
# Stays under 30 lines so it doesn't dominate the session opener.

set -euo pipefail

CONFIG_DIR="${ADK_CONFIG_DIR:-$HOME/.config/adk}"

cat <<EOF
[adk] marketplace loaded — 5 plugins available (adk-core, adk-code, adk-review, adk-docs, adk-investigate).

Default entry points:
  /adk-core:auto        — prompt-routing dispatcher (use for any non-trivial request)
  /adk-core:setup       — bootstrap ~/.config/adk/*.md and check env vars (first-run)
  /adk-core:info        — show what adk knows about you / your repos
EOF

if [[ -d "$CONFIG_DIR" ]]; then
  topics=()
  for f in "$CONFIG_DIR"/*.md; do
    [[ -f "$f" ]] || continue
    topics+=("$(basename "$f" .md)")
  done
  if (( ${#topics[@]} > 0 )); then
    printf "Meta-info loaded: %s\n" "${topics[*]}"
  else
    echo "Meta-info: none yet — run /adk-core:setup to bootstrap."
  fi
else
  echo "Meta-info: ~/.config/adk/ not found — run /adk-core:setup to bootstrap."
fi

cat <<'EOF'
Mode contract: --auto (default), -i / --interactive, --fix (only on mutation skills).
Working artifacts: .temp/task-<slug>/ (gitignored).
EOF
