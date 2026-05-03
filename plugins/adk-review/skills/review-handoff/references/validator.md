# `review-handoff` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/review-handoff.md`.

## Phase 0 — pre-execution

- [ ] Task slug resolved (either from `<task-slug>` arg or most-recently-touched).
- [ ] `.temp/task-<slug>/` exists.
- [ ] If `<task-slug>` was guessed: surface to user (the slug appears in the status banner).
- [ ] Mode parsed (`auto` | `interactive`); incompatible combos refused.
- [ ] `--post-to <target>` parsed if set.

## Phase 1 — preflight

- [ ] `bin/adk-info repos --check` returns 0.
- [ ] For `--post-to slack`: workspace Slack connector reachable; `slack.md.<channel>` set.
- [ ] For `--post-to jira`: Atlassian connector reachable; ticket key extractable.
- [ ] For `--post-to pr`: `gh auth status` succeeds; current branch has an open PR.
- [ ] No code-mutation tools are required; assert.

## Phase 2 — gather

- [ ] All files under `.temp/task-<slug>/` enumerated and read.
- [ ] Git state captured: branch, dirty?, last 10 commits, uncommitted diff (full + stat), stash list.
- [ ] Git remote URLs captured (anonymized — no tokens).
- [ ] Environment captured: `$EDITOR`, `$SHELL`, `pwd`, tool versions. NAMES only for env vars referenced in `.mcp.json`.
- [ ] Operator's name read from `~/.config/adk/info.md` (used in handoff signature).

## Phase 3 — synthesize

- [ ] All 10 sections populated (or explicitly omitted with reason via `--no-<section>` flag).
- [ ] **Section 1 (Task summary)** is one paragraph; restated in operator voice.
- [ ] **Section 2 (Decisions)** is a table; rationale is one line per row.
- [ ] **Section 3 (Work completed)** has commit SHA / artifact path for every claim.
- [ ] **Section 4 (Remaining work)** is numbered; cites file:line where applicable.
- [ ] **Section 5 (Blockers)** is a table; common case is `(none)`. Each blocker has owner + ETA + workaround.
- [ ] **Section 6 (Key files touched)** is a table.
- [ ] **Section 7 (Files NOT touched deliberately)** is a table — REQUIRED unless `--no-files-not-touched` set; surface to user as the most-skipped section.
- [ ] **Section 8 (Git state)** has branch, dirty?, last 10 commits, diff stat. Diff truncated to 200 lines max.
- [ ] **Section 9 (Environment)** has anonymized values; env-var NAMES only (no values).
- [ ] **Section 10 (Next step)** has a one-sentence description AND the exact command (in a fenced bash block).
- [ ] No env-var values quoted verbatim anywhere in the doc.
- [ ] No secrets quoted (e.g. tokens, keys). If present in the prior artifacts (e.g. a security-pass `secret_in_diff` finding), name the type + file/line; never the bytes.
- [ ] Length ≤ 300 lines (warn if exceeded).
- [ ] Prior `handoff.md` (if any) moved to `.archive/<iso-ts>/`.
- [ ] `handoff.md` written.

## Phase 4 — propose

- [ ] Under `-i`: walked all 10 sections; user-edits captured.
- [ ] Under `--auto`: full doc presented; no per-section gating.

## Phase 5 — post (only if `--post-to <target>`)

- [ ] Confirmation gate ASKED (always, even under `--auto`).
- [ ] If user declined: NO post happened (assert).
- [ ] If user approved:
  - [ ] For `slack`: posted to resolved channel; URL captured.
  - [ ] For `jira`: posted as comment on resolved ticket; URL captured.
  - [ ] For `pr`: posted via `gh pr comment`; receipt captured.
- [ ] **POST-CONFIRMATION** for `pr` only:
  - [ ] t=5s re-fetch ran.
  - [ ] If gaps: t=10s, t=20s.
  - [ ] **NO RE-POSTS** on misses.
- [ ] `handoff-postback.md` written.

## Phase 6 — pre-handoff

- [ ] `report.md` exists (pointer to handoff.md).
- [ ] `handoff.md` exists at the cited path.
- [ ] If `--post-to` ran: `handoff-postback.md` exists.
- [ ] No remote write happened without an approval gate.
- [ ] No code mutation in the session log (assert: zero `git commit` / `git push` / `Edit` / `Write` to non-`.temp/` paths).
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/per-skill/review-handoff.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user.
- If a section's REQUIRED content can't be derived (e.g. no commits in the task), surface "section <N> empty; consider passing additional context" and continue with that section omitted (but explicitly marked as omitted, not silently skipped).
- If `--post-to pr` post-confirmation final-misses, surface; do NOT re-post.

## Invariants

- This skill never mutates code. Period.
- This skill never auto-posts publicly. `--post-to <target>` AND user confirmation in the SAME turn are required.
- This skill never modifies `~/.config/adk/*.md`.
- This skill never modifies any artifact written by another skill.
