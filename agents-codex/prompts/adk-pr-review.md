# /adk-pr-review (Codex prompt)

Follow {{ADK_REPO}}/skills/adk-pr-review/SKILL.md.

Pre-load: AGENTS.md, constitution.md, paths.md, advisor.md, question-first.md, shared/personas/code-reviewer.md, shared/personas/security-reviewer.md.

This skill is GLOBAL — it runs from anywhere and isolates to `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/`. It does not touch the cwd repo.

Apply the input that follows this prompt.
