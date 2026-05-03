---
title: 'adk-core:adk-task-slug'
description: 'Helper binary adk-task-slug from adk-core.'
plugin: 'adk-core'
binary: 'adk-task-slug'
source: 'plugins/adk-core/bin/adk-task-slug'
group: 'core-bin'
order: 403
---
# adk-core:adk-task-slug

## Source

`plugins/adk-core/bin/adk-task-slug`

## Contents

```text
#!/usr/bin/env bash
# adk-task-slug — generate a kebab-case slug from a free-form prompt and create
# .temp/task-<slug>/ in the current working directory.
#
# Usage:
#   adk-task-slug "<prompt>"             # echo slug; create .temp/task-<slug>/
#   adk-task-slug "<prompt>" --print     # echo slug only; do NOT create folder
#   adk-task-slug "<prompt>" --date      # date-prefix the slug for disambiguation
#
# Conventions (matches plan/00-overview.md and plan/10-adk-core.md §10):
# - kebab-case, lowercase, max 6 words, derived from the first 3-5 nouns/verbs.
# - Strips: punctuation, common stop-words, URLs.
# - Falls back to a date-stamp slug if the prompt is empty.

set -euo pipefail

PROMPT="${1:-}"
PRINT_ONLY=0
DATE_PREFIX=0
shift || true
for arg in "$@"; do
  case "$arg" in
    --print) PRINT_ONLY=1 ;;
    --date) DATE_PREFIX=1 ;;
  esac
done

if [[ -z "$PROMPT" ]]; then
  PROMPT="task-$(date +%Y%m%d-%H%M%S)"
fi

# Strip URLs.
clean=$(printf '%s\n' "$PROMPT" | sed -E 's#https?://[^[:space:]]+##g')

# Lowercase.
clean=$(printf '%s\n' "$clean" | tr '[:upper:]' '[:lower:]')

# Replace non-alphanumeric with spaces.
clean=$(printf '%s\n' "$clean" | sed -E 's/[^a-z0-9]+/ /g')

# Filter common stop-words; keep up to 6 distinct words.
read -r -a words <<<"$clean"
stopwords=" the a an and or for of in on at to from with by is are was were be been being do does did this that these those it its as into about across against between through that's i we you they fix make build write create please can could would should "
slug_words=()
for w in "${words[@]:-}"; do
  [[ -z "$w" ]] && continue
  if [[ "$stopwords" == *" $w "* ]]; then continue; fi
  already=0
  if (( ${#slug_words[@]} > 0 )); then
    for existing in "${slug_words[@]}"; do
      if [[ "$existing" == "$w" ]]; then already=1; break; fi
    done
  fi
  (( already )) && continue
  slug_words+=("$w")
  (( ${#slug_words[@]} >= 6 )) && break
done

if (( ${#slug_words[@]} == 0 )); then
  slug="task-$(date +%Y%m%d-%H%M%S)"
else
  slug=$(IFS=-; echo "${slug_words[*]}")
fi

if (( DATE_PREFIX )); then
  slug="$(date +%Y-%m-%d)-${slug}"
fi

echo "$slug"

if (( ! PRINT_ONLY )); then
  mkdir -p ".temp/task-${slug}"
fi
```
