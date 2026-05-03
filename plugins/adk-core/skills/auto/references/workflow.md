# `auto` — workflow detail

## Phase 0 — prompt expansion

1. **Restate** the prompt in your own words. One sentence.
2. **Classify** into one or more verbs: `write`, `review`, `docs`, `investigate`, `publish`. Output a comma-separated list.
3. **Resolve entities** by reading `~/.config/adk/info.md` + `repos.md` (and others as needed). Use the prompt-expander subagent for this.
4. **Slug** the task via `bin/adk-task-slug "<prompt>"`. Kebab-case, max 6 words. Date-prefix only when disambiguation is needed.
5. **Create** `.temp/task-<slug>/` if not present. Write `prompt.txt` containing the verbatim user prompt + ISO timestamp.
6. **Detect links**. Regex match for: `*.atlassian.net`, `docs.google.com`, `*.slack.com/archives/`, `mail.google.com`, `github.com/.../{pull,issues}/`. If any match, queue `/adk-core:context-gather`.
7. **Approval gate** (unless `--auto`): show classification, slug, links queued, ask "proceed?".

## Phase 1 — preflight

1. Run `bin/adk-info --check`. Stop with the validation errors if any meta-info file fails to parse.
2. Run `bin/adk-mcp-health` for any MCPs the proposed skill chain needs. Stop with the missing-thing list if a required MCP is unreachable.
3. Run `git status` to capture branch + cleanliness. Informational unless the chain implies code mutation, in which case dirty tree → ask the user.
4. Validate that every entity from Phase 0 was either `verified` or has a documented `inferred` status.

## Phase 2 — context-gather (conditional)

1. If links were detected in Phase 0, spawn `agents/context-gatherer.md` (via the `Task` tool) loaded with `/adk-core:context-gather`. Pass:
  - The list of URLs.
  - `.temp/task-<slug>/` for output.
2. The subagent emits `context.md`. Show the summary; approval gate unless `--auto`.
3. If a link was access-denied, surface it and ask whether to continue without that source.

## Phase 3 — propose skill chain

1. Match the classification + entities against `references/dispatch-matrix.md`.
2. For each candidate, score by: (a) prompt-pattern match strength, (b) entity coverage (does the skill need an entity we have?), (c) destructiveness (prefer non-destructive first).
3. Build the chain. Sequence dependent skills; mark independent ones for parallel dispatch.
4. Write `.temp/task-<slug>/skill-plan.md` per the prompt-expander output shape.
5. Approval gate unless `--auto`.

## Phase 4 — dispatch

1. Spawn `agents/dispatcher.md` loaded with `auto`. Pass:
  - `skill-plan.md`.
  - `.temp/task-<slug>/`.
2. The dispatcher spawns parallel subagents per slice (max 4 at once).
3. Wait for all subagents to complete. Each returns its own report path.
4. The dispatcher aggregates into `.temp/task-<slug>/dispatch.md`.

## Phase 5 — validate + report

1. Each downstream skill validated itself in its own Phase 3 (per the universal phase contract). Confirm each per-skill validator file exists at `.temp/task-<slug>/validation/per-skill/<skill>.md`.
2. If any Blocker / Critical finding bubbled up → loop back to Phase 4 with the fix request.
3. Write `.temp/task-<slug>/report.md` per `references/output-format.md`.
4. Surface the report to the user with the offer-depth question ("Need more detail on any decision?").

## Loop control

- Looping forever on a flaky validator. After 3 failures of the same kind, stop and ask the user.
- Treating CI yellow (warnings, not failures) as red. Surface yellows in the report; do not auto-loop.
- Re-running an MCP query that already failed twice in this session — stop and surface the connection issue.