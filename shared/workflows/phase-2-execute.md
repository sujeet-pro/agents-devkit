# workflow: Phase 2 — execute

> Run the chosen approach. The skill-specific work happens here. This template is the wrapper.

## Steps

1. **Load the approach-specific reference**: `skills/<skill-name>/references/<approach>.md`.
2. **Run the work in small commits / checkpoints** when possible. Each checkpoint:
   - has a name (`step-1-scaffolding`, `step-2-domain-model`, …).
   - writes its output to `<task-slug>/steps/<step-name>.md`.
   - runs a validation gate before moving on (typecheck, lint, narrow test).
3. **Don't batch invisible work**. Surface what's about to happen, do it, surface what happened.
4. **Programmatic over AI** where deterministic: a regex, a script, a CLI tool > an LLM call. The skill's `scripts/` folder is where these live.
5. **One MCP / API call per logical question**. Don't speculatively fan out.

## Checkpoint format

Each step report (under `<task-slug>/steps/`):

```markdown
# step-N — <name>
status: completed | failed | skipped
took: 12s
what changed:
  - <path>: <one-line change description>
validators run:
  - typecheck: ✓
  - lint: ✓
  - narrow tests (affected): ✓
notes:
  - <anything surprising>
```

## When to pause

- Validator failure mid-execution → STOP. Don't paper over.
- User-confirmable shared-state action upcoming (push, post, publish, mutate) → STOP, ask, resume.
- Cost spike (LLM-calls-per-minute exceeded a threshold; programmatic step is taking >5min) → STOP, report, ask.
- Discovery of a contradiction (the code says X, the doc said Y) → STOP, ask which to trust.

## When NOT to pause

- A non-blocking question that can be deferred to the report. Log it; don't interrupt flow for it.
- A nicer-but-not-required refactor opportunity. Note in report; don't act.

## Mode-specific overlays

- `--auto`: execution runs to completion without stopping for non-blocker questions. Shared-state actions still require explicit confirmation.
- `-i` / `--interactive`: pause between steps for user OK.
- `--dry-run`: produce all checkpoints + diffs, but don't write to repo, push, post, or publish.

## Output

- `<task-slug>/steps/*.md` — per-checkpoint logs.
- `<task-slug>/diffs/` — proposed patch files (under `--dry-run`) or applied diffs (otherwise).
- All work files in the repo, not under `<task-slug>/`.
