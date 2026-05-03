# `investigate-deploy` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 0 questions

1. **Repo: `<resolved>`. Right one?**
   - _When asked:_ multiple candidates from `repos.md` match the shorthand; OR no `<repo>` arg AND not in a git repo.
   - _Default under `--auto`:_ pick the verified-aliased candidate; if none, pick the CWD-derived repo; otherwise stop and ask.

2. **Workflow: `<resolved>`. OK?**
   - _When asked:_ `repos.md.repos[<repo>].deploy_workflow` is unset AND the operator hasn't explicitly passed `--workflow`.
   - _Default under `--auto`:_ literal `deploy`; if zero runs returned, surface "no runs found for workflow `deploy`; suggest `gh workflow list --repo <repo>` to discover".

3. **Window: `<resolved>`. OK?**
   - _When asked:_ no `--window` flag and no NL window in the prompt.
   - _Default under `--auto`:_ `last 2h`.

## Phase 2 questions

4. **About to run: `gh run list --repo <r> --workflow=<w> --limit <N>`. Run?**
   - _When asked:_ only under `-i`. Under `--auto`, run silently (command still printed).

## Phase 3 questions

5. **DD cross-reference: I see `datadog` MCP available. Pull deploy events for cross-check?**
   - _When asked:_ `--auto` does not ask; default = pull. `-i` asks.
   - _Default under `--auto`:_ pull.

6. **Found `<N>` near-symptom candidates. Suggest follow-up to `/adk-investigate:investigate-incident`?**
   - _Default under `--auto`:_ yes; include the suggested invocation in the `Follow-up` section.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something the meta-info already answers.
- Never ask under `--auto` — defaults apply, surface them in the final report.
- If the user already answered earlier, don't re-ask.
- Don't ask "are you sure?" before a read-only `gh` call.
