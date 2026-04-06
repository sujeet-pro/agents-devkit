# Jira Routing

## Story Details Workflow

When investigating an issue or understanding context:

1. **Get issue** → `scripts/issues.sh get --key PROJ-123`
   - Reference: `issue-operations.md` → get
2. **Read comments** → `scripts/comments.sh list --key PROJ-123`
   - Reference: `comment-operations.md` → list
3. **Get linked issues** → parse `issuelinks` from issue response, then get each linked issue
   - Reference: `issue-operations.md` → get (follow links)
4. **Check history** → use `--expand changelog` on issue get
   - Reference: `issue-operations.md` → get with expand

## Project Management Workflow

When managing project work:

1. **List projects** → `scripts/projects.sh list`
   - Reference: `project-operations.md` → list
2. **Get board** → `scripts/boards.sh list --project PROJ` then `scripts/boards.sh get --board-id ID`
   - Reference: `board-operations.md` → list, get
3. **Manage sprints** → `scripts/boards.sh sprints --board-id ID`
   - Reference: `board-operations.md` → sprints, move-to-sprint
4. **Transition issues** → `scripts/issues.sh transitions --key PROJ-123` then `scripts/issues.sh transition --key PROJ-123 --transition-id ID`
   - Reference: `issue-operations.md` → transitions, transition

## Search Workflow

When finding issues:

| Use Case | JQL Pattern | Script |
|----------|-------------|--------|
| My open issues | `assignee = currentUser() AND statusCategory != Done` | `scripts/search.sh` |
| Sprint work | `sprint in openSprints() AND project = PROJ` | `scripts/search.sh` |
| Recent bugs | `issuetype = Bug AND created >= -7d AND project = PROJ` | `scripts/search.sh` |
| Blocked items | `status = Blocked OR status = "On Hold"` | `scripts/search.sh` |
| Text search | `text ~ "search term" AND project = PROJ` | `scripts/search.sh` |
| Unassigned | `assignee is EMPTY AND project = PROJ AND statusCategory != Done` | `scripts/search.sh` |
| High priority | `priority in (Highest, High) AND statusCategory != Done` | `scripts/search.sh` |
| Updated recently | `updated >= -1d AND project = PROJ` | `scripts/search.sh` |

Reference: `search-operations.md`

## Issue Lifecycle

Standard progression for an issue:

1. **Create** → `scripts/issues.sh create --project PROJ --type Task --summary "..."` 
   - Reference: `issue-operations.md` → create
2. **Assign** → `scripts/issues.sh assign --key PROJ-123 --account-id ACC_ID`
   - Reference: `issue-operations.md` → assign
3. **Transition to In Progress** → get transition ID, then transition
   - Reference: `issue-operations.md` → transitions, transition
4. **Comment on progress** → `scripts/comments.sh add --key PROJ-123 --body "Update: ..."`
   - Reference: `comment-operations.md` → add
5. **Log work** → `scripts/issues.sh add-worklog --key PROJ-123 --time-spent "2h"`
   - Reference: `issue-operations.md` → add-worklog
6. **Resolve** → transition to Done/Resolved with resolution
   - Reference: `issue-operations.md` → transition with --resolution
7. **Link related issues** → `scripts/issues.sh link --from PROJ-123 --to PROJ-456 --type "Blocks"`
   - Reference: `issue-operations.md` → link

## Operation → Script Quick Reference

| Operation | Script | Action |
|-----------|--------|--------|
| Get issue details | `issues.sh` | `get` |
| Create issue | `issues.sh` | `create` |
| Update issue fields | `issues.sh` | `update` |
| Delete issue | `issues.sh` | `delete` |
| List transitions | `issues.sh` | `transitions` |
| Transition issue | `issues.sh` | `transition` |
| Assign issue | `issues.sh` | `assign` |
| Link issues | `issues.sh` | `link` |
| Get watchers | `issues.sh` | `watchers` |
| Add watcher | `issues.sh` | `add-watcher` |
| Get worklogs | `issues.sh` | `worklog` |
| Add worklog | `issues.sh` | `add-worklog` |
| List comments | `comments.sh` | `list` |
| Get comment | `comments.sh` | `get` |
| Add comment | `comments.sh` | `add` |
| Update comment | `comments.sh` | `update` |
| Delete comment | `comments.sh` | `delete` |
| Search (JQL) | `search.sh` | positional JQL arg |
| List projects | `projects.sh` | `list` |
| Get project | `projects.sh` | `get` |
| Project versions | `projects.sh` | `versions` |
| Create version | `projects.sh` | `create-version` |
| Project components | `projects.sh` | `components` |
| Create component | `projects.sh` | `create-component` |
| Project statuses | `projects.sh` | `statuses` |
| List boards | `boards.sh` | `list` |
| Get board | `boards.sh` | `get` |
| Board config | `boards.sh` | `config` |
| List sprints | `boards.sh` | `sprints` |
| Sprint issues | `boards.sh` | `sprint-issues` |
| Move to sprint | `boards.sh` | `move-to-sprint` |
| Get backlog | `boards.sh` | `backlog` |
| Move to backlog | `boards.sh` | `move-to-backlog` |
| Rank issues | `boards.sh` | `rank` |
