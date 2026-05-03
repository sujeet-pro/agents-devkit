# `prompt-expand` workflow

## Step 1 — capture

1. Quote the user's prompt verbatim into the output's `Prompt:` section.
2. Capture invocation flags (e.g. `--auto`, `--scope`).

## Step 2 — entity extraction

1. Run regex matchers for: repo paths (`org/repo`), service shorthand, PR URLs, time expressions, environment shorthand, experiment names, gate names, file paths.
2. For each match, attempt resolution against `~/.config/adk/*.md` per `auto/references/entity-resolver.md`.
3. Mark each as `verified` or `inferred`.

## Step 3 — link extraction

1. Regex for: `*.atlassian.net`, `docs.google.com`, `*.slack.com/archives/`, `mail.google.com`, `github.com/.../{pull,issues}/`.
2. Classify each by type.
3. Mark whether `context-gather` would be queued (default: yes if any link).

## Step 4 — verb classification

1. Match the prompt against the verb-trigger table (mirror of `auto/references/dispatch-matrix.md`).
2. Score each candidate; pick the top one as primary.
3. If multiple verbs score similarly, list them all in priority order.

## Step 5 — chain construction

1. For the primary verb, look up the matching skill.
2. For each secondary verb, decide whether it's a follow-up (chain) or a separate request (out of scope).
3. Each invocation includes: skill name, flags, key input.

## Step 6 — alternatives

1. For each step in the chain, identify ≥1 alternative skill.
2. Briefly note when the alternative would be preferred.

## Step 7 — missing inputs

1. List every entity the recommended chain needs but you couldn't resolve.
2. For each, suggest where the user could add it (`~/.config/adk/<topic>.md`).

## Step 8 — write output

Write `.temp/task-<slug>/skill-plan.md` per `references/output-format.md`. The slug comes from the prompt via `bin/adk-task-slug`.
