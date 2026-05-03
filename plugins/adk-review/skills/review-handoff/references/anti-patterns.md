# `review-handoff` — anti-patterns

## Content

- **Vague summary.** "Worked on the auth feature today" is useless. The standard: "Added `RequireRole('admin')` middleware to 4 admin endpoints (commits `<a-d>`); 3 of 4 endpoints have unit tests; 1 (`/admin/users/delete`) is missing the test."
- **No commits / files / artifacts cited.** Every "completed" claim links to a commit / file / artifact. If the artifact doesn't exist, the claim doesn't either.
- **Skipping the "Files NOT touched" section.** The single most-skipped, most-valuable section. Without it, the next person redoes work that was considered + rejected.
- **Hiding what didn't work.** "Tried X with Y; failed because Z; abandoned" is gold. Hiding it forces the next person to re-discover the dead-end.
- **Marking everything `Remaining work` and nothing `Blocker`.** Blockers are blocking — they have an owner + ETA + workaround. Mixing them dilutes urgency.
- **No concrete next-step command.** "Open the PR" is incomplete. The standard: `gh pr create --title "<derived from prompt.txt>" --body-file .temp/task-<slug>/pr-body.md` (and if `pr-body.md` doesn't exist yet, list the prerequisite skill: `/adk-docs:docs-pr-description`).
- **Out-of-date git state.** The skill captures git at Phase 2; if the user keeps editing during the synthesis phase, the captured state may be stale. Re-capture if there's been any edit.

## Privacy / security

- **Quoting env-var values verbatim.** `GITHUB_PAT=ghp_xxxxxxxxxxxxxxxxxxxx` in the handoff. NEVER. Anonymize: name only.
- **Quoting customer names from logs.** Even in internal docs. Anonymize.
- **Quoting secrets in any form.** Including "found a secret in this commit" — name the secret type / file / line; never the bytes.
- **Including the full uncommitted diff verbatim** when it contains sensitive code (e.g. customer-specific config). Truncate; reference the file:line range.

## Posting

- **Posting to Slack without `--post-to slack` AND user confirmation.** The skill is read-only by default. Public-post is a SHARED-STATE action; always asks.
- **Posting to a wrong channel.** Default to the team channel; for incident handoff, default to incident-channel; never default to a public channel that's not in the meta-info.
- **Posting verbatim handoff (10 sections, ~80 lines) to Slack.** Slack messages above ~30 lines get auto-collapsed. Surface a Slack-friendly truncated version + link to the full handoff.md (the user should publish the full doc to a separate URL — Confluence, Gist, etc.).
- **Posting to a closed PR.** Verify the PR is open before posting.
- **Re-posting on a propagation miss to PR.** Same rule as `review-pr`: never. The cost is duplicate comments.

## Process

- **Including the most-recent task by mtime when it's NOT what the user means.** If `.temp/task-<a-old>/` was touched 5 minutes ago by an unrelated edit, the skill might pick the wrong slug. Surface the chosen slug at Phase 0; user can override.
- **Skipping the read of `.temp/task-<slug>/` files OTHER than the obvious ones.** The skill should read everything in the task directory, not just `report.md`.
- **Synthesizing without reading.** Inferring "what was done" from the prompt without reading the actual artifacts. The artifacts are the source of truth.
- **Re-running on the same task in the same session and silently overwriting `handoff.md`.** Move the prior `handoff.md` to `.archive/<iso-ts>/` first.
- **Capturing git state at the wrong time.** Capture in Phase 2 (early); if there's an edit between Phase 2 and Phase 4, re-capture. Stale git state in the handoff is misleading.

## Reporting

- **Burying the next-step command at the bottom.** Reader-tired-mode: lead with the next step.
- **Listing 47 commits in "Git state".** Default `--commits 10`. More than 10 is overwhelming.
- **Listing all dirty files in "Git state".** If the dirty list is >20 files, summarize ("20+ files dirty under `src/pricing/`; full list in `git status --porcelain`").
- **Re-quoting the prompt verbatim in "Task summary".** Restate in your own words; the prompt is in `prompt.txt` for the curious.
- **Saying "this is in good shape" without evidence.** Cite the validation evidence path.
