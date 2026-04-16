# ADK Handoff Workflow

## Create Flow
1. **Capture git state** -- run `python3 scripts/handoff.py` to get branch, status, recent commits, and diff summary automatically
2. **Identify scope** -- determine the task description from `--task` or infer from the conversation
3. **Catalog files** -- list all files created, modified, or deleted during the session using git status and diff
4. **Record decisions** -- document each decision made during the session with its rationale so the next reader does not revisit settled questions
5. **List remaining work** -- enumerate what still needs to be done, ordered by priority, each item specific and actionable
6. **Capture blockers** -- list anything preventing progress: missing information, unresolved questions, external dependencies, failing tests
7. **Write handoff document** -- assemble all sections using the handoff template and write to `--output` or `.handoff/handoff-YYYY-MM-DD-HHMM.md`
8. **Report summary** -- output a short summary: task name, progress, blocker count, file path

## Resume Flow
1. **Read handoff** -- load the handoff document from the specified path or find the most recent one in `.handoff/`
2. **Verify git state** -- confirm current branch matches the recorded branch, check for unexpected uncommitted changes
3. **Present state** -- show the user what is done, what is in progress, and what remains
4. **Suggest next action** -- based on priority ordering in the remaining work section, recommend the immediate next step
5. **Offer continuation** -- ask the user whether to proceed with the suggested action or re-prioritize

## Status Flow
1. **Scan for handoffs** -- find all `.md` files in `.handoff/` and any path the user specifies
2. **Summarize each** -- extract task name, creation date, progress state, and blocker count
3. **Show freshness** -- indicate how long ago each handoff was created (e.g., "2 hours ago", "3 days ago")
4. **Highlight stale** -- flag handoffs older than 7 days as potentially outdated

## Validation Rules
- git state section is present and populated from actual commands
- all files from `git status` appear in the key files section
- every remaining work item is a concrete action, not a vague goal
- every blocker includes enough context to act on
- the document is self-contained: a reader with no prior context can understand the state
