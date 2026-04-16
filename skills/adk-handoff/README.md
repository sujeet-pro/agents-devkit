# adk-handoff

Create structured session handoff documents for long-running tasks.

## Quick Start

Install via npx skills, then invoke:

```
/adk-handoff --action create --task "Implementing OAuth2 flow for the API gateway"
```

```
/adk-handoff --action resume --output .handoff/handoff-2026-04-14-1030.md
```

```
/adk-handoff --action status
```

```
/adk-handoff --action create --auto
```

## What This Skill Does

Captures the complete state of in-progress work so any session or person can resume without information loss. It records what was done, what decisions were made and why, what remains, what is blocking progress, and the exact git state. The output is both machine-readable and human-readable.

## Command Reference

| Invocation | Description |
| --- | --- |
| `/adk-handoff` | Create a handoff document (default action) |
| `/adk-handoff --action create` | Create a new handoff document |
| `/adk-handoff --action resume` | Resume work from an existing handoff document |
| `/adk-handoff --action status` | Show summaries of existing handoff documents |
| `/adk-handoff --task "<description>"` | Specify the task being handed off |
| `/adk-handoff --output <path>` | Set the output path for the handoff document |
| `/adk-handoff --auto` | Skip confirmations, use defaults |
| `/adk-handoff --help` | Show the skill description and stop |

## Dependencies

| Dependency | Required? | Install Command |
| --- | --- | --- |
| git | Yes | `brew install git` |
| python3 | Yes | `brew install python@3` |

## Skill Layout

```
adk-handoff/
  SKILL.md              # Skill definition and instructions
  README.md             # This file
  scripts/
    preflight.py        # Pre-flight dependency checker
    handoff.py          # Git state capture helper
  references/
    workflow.md          # Handoff workflow details
    persona.md           # Agent persona guidance
    handoff-template.md  # Handoff document template
    _shared/
      ai-guidelines-overview.md
      constitution.md
      output-format.md
      research-protocol.md
```

## Workflow

1. **Capture git state** -- run `handoff.py` to automatically capture branch, uncommitted changes, and recent commits
2. **Gather task context** -- collect task description from conversation or `--task` parameter
3. **Identify changed files** -- list all modified, created, and deleted files
4. **Document decisions** -- record decisions made during the session with rationale
5. **List remaining work** -- order remaining items by priority
6. **Capture blockers** -- note anything preventing progress or needing clarification
7. **Write document** -- output the handoff document to the specified location
8. **Report summary** -- show what was captured and suggest next action

## Interaction Protocol

- **Confirmations**: The skill shows the handoff document summary and confirms completeness before writing. Use `--auto` to skip.
- **Findings format**: The handoff document is presented in sections (task, state, decisions, remaining, blockers, files, git, environment). Each section is self-contained.
- **User response syntax**: Reply with "write", "add: ...", "remove: ...", or "adjust priority of ..." after reviewing the summary.

## Output Format

1. **Summary** -- handoff document path and one-line task description
2. **Scope** -- files modified, created, or deleted during the session
3. **Findings** -- decisions made, remaining work items, blockers
4. **Validation** -- git state matches reality, all modified files are listed, remaining items are actionable
5. **Remaining risk** -- information that may be missing from the handoff
6. **Next steps** -- recommended first action for the person resuming

## Examples

### Create a handoff document
```
> /adk-handoff --action create --task "Implementing OAuth2 flow for the API gateway"

Handoff document written to: .handoff/handoff-2026-04-14-1430.md

Summary:
  Task: Implementing OAuth2 flow for the API gateway
  Progress: ~60% complete
  Files: 8 modified, 3 created
  Decisions: 4 recorded (PKCE over implicit, jose library, etc.)
  Remaining: 5 items (token refresh, error handling, integration tests, docs, cleanup)
  Blockers: 1 (need staging environment credentials for integration test)
  Branch: feature/oauth2-flow
  Uncommitted: 2 files

Next action: resolve staging credentials blocker, then implement token refresh
```

### Resume from a handoff
```
> /adk-handoff --action resume --output .handoff/handoff-2026-04-14-1430.md

Loaded handoff: Implementing OAuth2 flow for the API gateway
Branch: feature/oauth2-flow (matches current branch)
Git state: clean (no unexpected changes)

Current state:
  Done: OAuth2 client, PKCE flow, authorization endpoint
  In progress: token refresh middleware
  Not started: error handling, integration tests, docs

Remaining work (by priority):
  1. Implement token refresh middleware
  2. Add error handling for expired/revoked tokens
  3. Write integration tests
  4. Update API docs
  5. Clean up debug logging

Suggested next action: continue token refresh middleware implementation
```

### Check handoff status
```
> /adk-handoff --action status

Found 2 handoff documents:

  .handoff/handoff-2026-04-14-1430.md
    Task: Implementing OAuth2 flow
    Progress: ~60%  |  Created: 2 hours ago

  .handoff/handoff-2026-04-12-0900.md
    Task: Database connection pooling
    Progress: ~90%  |  Created: 2 days ago
```

## What Success Looks Like

- [ ] Git state is captured accurately and matches reality
- [ ] All modified files are listed in the handoff document
- [ ] Decisions include rationale so settled questions are not revisited
- [ ] Remaining work items are actionable and prioritized
- [ ] Blockers are specific enough to act on
- [ ] The document stands alone without the original conversation
- [ ] Anyone can resume the work using only the handoff document
