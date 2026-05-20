# /adk-pr-reviews (Codex prompt)

Follow {{ADK_REPO}}/skills/adk-pr-reviews/SKILL.md.

Pre-load: AGENTS.md, constitution.md, paths.md, advisor.md, question-first.md, and skills/adk-pr-review/SKILL.md (this skill wraps it).

This skill is GLOBAL — it reads a JSON5 queue at `~/.agents-devkit/pr-reviews/queue.json5` (or the path passed). Two modes: `--scan` first refreshes the queue from slack channels per `~/.agents-devkit/config/pr-reviews-slack.json5`; default mode runs reviews against the existing queue. Per non-skipped row: spawns a headless `claude -p` review. Posting comments + slack reactions + slack reminders are all in scope by the user's invocation.

Apply the input that follows this prompt.
