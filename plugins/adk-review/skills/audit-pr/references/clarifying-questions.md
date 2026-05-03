# `audit-pr` — clarifying questions

Asked in order, one at a time, **only when the answer changes the plan**. Under `--auto`, defaults apply silently.

## Phase 0 questions

1. **PR reference: `<resolved owner/repo#num>`. Correct?**
   - _How to pick:_ derived from input or current branch's open PR.
   - _Skip when:_ unambiguous URL.

2. **Run all 10 checks, or a subset?**
   - _How to pick:_ default `all 10`. Override with `--checks <list>`.
   - _Skip when:_ user passed `--checks` explicitly OR `--auto`.

## Phase 1 questions

3. **Tool `<name>` not installed. Skip the affected check (mark N/A) or stop?**
   - _How to pick:_ default `skip + mark N/A` (with install command in the report).
   - _Skip when:_ `--auto` (default applies silently).

## Phase 4 questions (under `-i`)

4. **Check `<name>`: <verdict>. Action?**
   - _How to pick:_ default depends on verdict:
     - PASS → no action; just acknowledge.
     - WARN → suggest `--fix` if safely-fixable; else suggest follow-up skill.
     - FAIL → suggest `--fix` if safely-fixable; else surface mitigation steps.
     - N/A → surface install command; no other action.
   - _Skip when:_ `--auto`.

5. **Some Warns/Fails are not auto-fixable; suggest follow-up skills?**
   - _How to pick:_ default `yes` — list the suggested skills inline (e.g. `tests-added FAIL → /adk-code:code-test`; `doc-updated WARN → /adk-docs:docs-changelog`; `secrets-in-diff FAIL → user action: rotate + remove`).
   - _Skip when:_ `--auto`.

## Phase 5 questions

6. **(--fix only) Apply auto-fixes to <n> checks? <list>**
   - _How to pick:_ default `apply all safely-fixable`.
   - _Skip when:_ `--auto --fix`.

7. **(--fix only) PUSH-GATE: push <n> commits to branch <head-branch>?**
   - _How to pick:_ NO DEFAULT. Always asks at first push of session.
   - _Skip when:_ NEVER (mandatory even under `--auto --fix`).

8. **(--post-comment only) Post audit summary as a PR comment to #<num>?**
   - _How to pick:_ NO DEFAULT. Always asks (default `N` even under `--auto`).
   - _Skip when:_ NEVER.

## Anti-rules for asking

- **Never ask about something the meta-info answers.** If `repos.md` has the path, don't re-ask.
- **Never stack 3 questions in one turn.** Iterate.
- **Never ask under `--auto`** UNLESS the question is about a SHARED-STATE action (push, post-comment) — those always ask.
- **PUSH-GATE always asks.** Even under `--auto --fix`.
- **Comment-post gate always asks.** Even under `--auto --post-comment`.
- **No question about whether to post-confirm.** Always runs.
- **No question about whether to merge.** The skill never merges.
- **No question about severity.** This skill is Pass/Warn/Fail, period.

## Why this skill asks fewer questions than `review-pr`

- Fixed checklist (no per-finding decisions).
- Pass/Warn/Fail (no severity tiering decisions).
- No reconciliation (no per-existing-comment decisions).
- No drafting (no per-comment template decisions).
- Default mode is informational (no posting, no fixing).

Under `--auto` (no `--fix`, no `--post-comment`), this skill asks ZERO questions and runs end-to-end.

Under `--auto --fix`, it asks ONE question (the push-gate) — and only if there are commits to push.
