# `docs-pr-description` — clarifying questions

Asked under `-i`; defaults apply under `--auto`.

## Phase 0 questions

1. **Repo: `<resolved>`. Branch: `<current>`. PR exists: `<#N or no>`.
   Proceed?**
   - _Default under `--auto`:_ proceed.

## Phase 1 questions

2. **Base branch: `<resolved>`. Override?**
   - _How to pick:_ Defaults to tracking → `origin/<repos.md base>`
     → `main`. Override if the branch targets a feature branch (e.g.
     merging to a release branch).
   - _Default under `--auto`:_ the resolved default.

3. **Repo has `.github/pull_request_template.md`. Adopt its
   structure?**
   - _Default under `--auto`:_ yes. Refuse only if the template is
     empty or broken.

## Phase 3 questions

4. **Classification of changes by area (proposed):**
   - _Default under `--auto`:_ accept the classification.
   - _When to ask:_ the area table is unwieldy (> 10 rows) and
     collapsing is non-trivial.

## Phase 4 questions

5. **Title style: `<conventional | sentence | repo-matched>`?**
   - _Default under `--auto`:_ detected convention from `git log -10
     --format=%s`; fall back to `sentence`.

## Phase 5 questions (under `--fix`)

6. **Update PR body via `gh pr edit <N> --body-file pr-body.md`?**
   - _Default under `--auto --fix`:_ **still asks once** — this is
     the one ask that survives `--auto`. Reviewers get a GitHub
     notification from the edit.

7. **Existing PR body was last edited by `<author>` on `<date>`. Back
   up and overwrite?**
   - _Default under `--auto --fix`:_ yes, with backup, after the
     single ask above.

## Anti-rules

- Never ask more than one question per turn.
- Never stack "confirm the title" and "confirm the body" into one
  question — iterate.
- Never ask about something the CLI arg already disambiguates.
- Never silently skip the remote-write confirmation, even under
  `--auto --fix`. That confirmation is a hard rule.
