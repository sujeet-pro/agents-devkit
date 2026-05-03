# `info` — anti-patterns

- **Printing env-var values.** The `--resolve-env` flag substitutes `${VAR}` with the actual value, but this skill MUST refuse to print resolved secrets. The `<unset>` sentinel is fine; the literal value is not. (Use `echo $VAR` if you need to verify.)
- **Inventing a field.** If `datadog.md.site` is unset, return `null` or omit it. Don't fabricate `datadoghq.com` as a default; that's the skill's job, not `info`'s.
- **Modifying any file.** Read-only. Even normalizing whitespace is forbidden.
- **Caching across invocations.** Always read fresh. The user may have just edited the file in another tab.
- **Treating an optional unset field as an error.** Fields are optional unless explicitly required (per `bin/adk-info`'s `REQUIRED_FIELDS`).
- **Pretty-printing changes the JSON shape.** Stable JSON output (sorted keys, 2-space indent, no trailing comma) — downstream skills parse it.
- **Returning a different shape for the same query.** Determinism matters: `info datadog site` always returns a string; `info datadog service_aliases` always returns an object.
- **Failing silently on a parse error.** Surface the error with line:col so the user can fix it.
