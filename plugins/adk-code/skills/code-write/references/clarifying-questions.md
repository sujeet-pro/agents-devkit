# `code-write` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently and are listed in the final report's Decisions table.

## Phase 0 — prompt expand

1. **Repo: I see the change applies to `<resolved-repo>` from `repos.md`. Correct?**
   - _How to pick:_ Resolved by `cwd → .git → repos.md path` match. If the prompt names a different repo by short alias, surface the conflict.
   - _Default under `--auto`:_ proceed with the cwd-resolved repo. Surface the resolution in the Decisions table.

2. **Likely files: `<list>`. Anything missing?**
   - _How to pick:_ Grep + Glob over the prompt's nouns/verbs.
   - _Default under `--auto`:_ proceed with the discovered list; flag any later-added files as "out of plan, re-confirmed".

3. **Slug `<proposed>` looks right?**
   - _How to pick:_ Derived from prompt nouns/verbs (3-6 words, kebab-case).
   - _Default under `--auto`:_ proceed with the derived slug.

## Phase 1 — preflight

4. **Working tree dirty: `<file list>`. Stash, abort, or include in the change?**
   - _How to pick:_ Default `stash` if dirty changes are unrelated. Default `include` only if the user explicitly named those files.
   - _Default under `--auto`:_ if `git diff --stat` shows changes outside the planned set → stash + restore at the end. If inside the planned set → STOP and ask, even under `--auto`.

5. **On `<branch>`. Create a feature branch, or stay here?**
   - _How to pick:_ If `<branch>` is `main`/`master`/`develop`/anything in `~/.config/adk/github.md.forbid_force_push_branches` → strongly default to creating a feature branch.
   - _Default under `--auto`:_ create `feat/<slug>` from the protected branch and switch to it.

6. **Baseline is red on the following: `<list>`. Continue anyway?**
   - _How to pick:_ Default NO. Editing on a red baseline obscures whether the new edit caused new failures.
   - _Default under `--auto`:_ STOP and ask. This is the one place `--auto` does not default-proceed.

## Phase 3 — plan

7. **Plan looks like this: `<plan>`. Approve, edit, or change?**
   - _How to pick:_ Default `(approve)` if no obvious gap. Allow edits like "drop step 2" or "add a test for the empty case".
   - _Default under `--auto`:_ proceed with the plan as written.

8. **Out-of-plan: I noticed `<thing>` while reading. Want to include it, or list it as a follow-up?**
   - _How to pick:_ Default `follow-up` (separate task). Only include if the user explicitly says "yes, fold it in".
   - _Default under `--auto`:_ list as follow-up in the report; never silently fold in.

## Phase 4 — implement

9. **Implementer wants to touch `<file>` (not in plan.md). Allow?**
   - _How to pick:_ Default NO. Re-confirm before letting the agent proceed. If yes, update `plan.md` to reflect the new scope.
   - _Default under `--auto`:_ STOP and ask. Even under `--auto`, scope creep is gated.

## Phase 5 — validate

10. **Snapshot tests changed. Update or treat as failure?**
    - _How to pick:_ Default `treat as failure` and ask the operator under `-i`. Under `--auto`, default `update + flag in report` ONLY if the snapshot file is the only thing red.
    - _Default under `--auto`:_ update + record in the Decisions table. The operator reviews the snapshot diff at PR time.

11. **Test failed: `<failing test>`. Iterate, accept, or escalate?**
    - _How to pick:_ Default `iterate` up to 3 times.
    - _Default under `--auto`:_ iterate up to 3 times, then escalate.

## Phase 6 — report

12. **Report ready. Need anything else added?**
    - _How to pick:_ Default `(no)`.
    - _Default under `--auto`:_ skip the question; offer-depth at the end.

## Anti-rules for asking

- Never ask 3 questions stacked in one turn.
- Never ask about something `repos.md` already answers (resolved entity ≠ ambiguous entity).
- Never ask under `--auto` (except #6 baseline-red and #9 scope-creep — those gate even under `--auto`).
- If the user already answered the same question earlier in this session, don't re-ask.
- Surface the default before asking, so the user can say "default is fine" without re-reading.
