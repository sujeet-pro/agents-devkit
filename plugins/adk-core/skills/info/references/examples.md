# `info` — worked examples

## Example 1 — dump all (default)

```text
/adk-core:info
```

→ JSON object with one key per topic file in `~/.config/adk/`.

## Example 2 — dump one topic

```text
/adk-core:info datadog
```

→ The contents of `~/.config/adk/datadog.md`'s YAML front-matter as JSON.

## Example 3 — dump one key

```text
/adk-core:info datadog site
```

→ `"datadoghq.com"` (single string).

## Example 4 — dotted path

```text
/adk-core:info repos defaults.base_branch
```

→ `"main"`.

## Example 5 — validate

```text
/adk-core:info --check
```

If all OK:

```
{ "ok": true }
```

If errors:

```
ERROR: datadog.md: required field 'site' missing or empty
ERROR: github.md: looks like a raw secret at github.auth.token; use ${ENV_VAR} placeholder instead
```

(exit code 1)

## Example 6 — list missing-but-recommended fields

```text
/adk-core:info --missing
```

→

```json
[
  { "topic": "mixpanel", "status": "missing-file" },
  { "topic": "docs", "status": "missing-fields", "fields": ["default_confluence_space", "default_gdrive_folder_id"] }
]
```

## Example 7 — interactive summary

```text
/adk-core:info
```

(if invoked interactively) → markdown summary instead of raw JSON. See `references/output-format.md` for the shape.

## Example 8 — used by another skill

`/adk-investigate:investigate-datadog` does:

```bash
SITE=$(adk-info datadog site | tr -d '"')
DEFAULT_ENV=$(adk-info datadog default_env | tr -d '"')
SERVICE=$(adk-info datadog "service_aliases.$user_shorthand" 2>/dev/null | tr -d '"')
```

If any of these returns nothing, the skill stops and tells the user to run `/adk-core:setup --target datadog`.
