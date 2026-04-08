# Context Thread Stage

Context threads provide persistent, named workspaces for ongoing work streams that survive across sessions. Each thread captures purpose, relevant files, decisions, blockers, and a chronological log so you can pick up exactly where you left off.

## Workflow

This stage uses the **Quick Action** workflow: confirm → execute → verify.

## Thread Storage

Save all threads to `.temp/threads/<name>.md` in the current working directory. If `.temp/threads/` does not exist, create it and ensure `.temp/` is listed in `.gitignore`.

Use this thread file format:

```markdown
---
thread: <name>
created: <ISO-8601>
updated: <ISO-8601>
status: active | archived
tags: [<tag1>, <tag2>]
---

# Thread: <name>

## Purpose
<what this ongoing work stream is about>

## Relevant Files
- <file paths>

## Log
### <ISO-8601>
<note, decision, or status update>

### <ISO-8601>
<note, decision, or status update>
```

## Actions

### 1. create

Create a new named thread. Requires `name`.

**Steps:**

1. Verify no thread with the same name already exists in `.temp/threads/`.
2. Analyze recent git history and open files to detect relevant file paths.
3. Present the interactive creation prompt for confirmation:

```text
## New Context Thread

Name: <proposed name>
Purpose: <description inferred from context or provided by user>
Relevant files: <detected from recent work>
Tags: <suggested tags>

Action: [C]reate | [E]dit | [C]ancel
```

4. On **Create**: write the thread file to `.temp/threads/<name>.md` with the current timestamp, `status: active`, and an initial log entry recording the thread creation.
5. On **Edit**: let the user modify name, purpose, files, or tags, then re-present the prompt.
6. On **Cancel**: abort without writing anything.

### 2. update

Append a note, decision, or status update to an existing thread. Requires `name` and `note`.

**Steps:**

1. Read the thread file from `.temp/threads/<name>.md`. If it does not exist, report an error and list available threads.
2. Verify the thread status is `active`. If it is `archived`, ask the user whether to reactivate it first.
3. Append a new log entry with the current ISO-8601 timestamp and the provided note.
4. Update the `updated` field in the frontmatter.
5. Write the file back and confirm the update.

### 3. load

Read a thread into the current context and summarize its state. Requires `name`.

**Steps:**

1. Read the thread file from `.temp/threads/<name>.md`. If it does not exist, report an error and list available threads.
2. Present a summary:

```text
## Thread: <name>
Status: <active | archived>
Created: <date>  |  Last updated: <date>
Tags: <tags>

### Purpose
<purpose>

### Relevant Files
<file list with existence check -- mark missing files>

### Recent Activity (last 5 entries)
- <timestamp>: <summary of note>
- <timestamp>: <summary of note>

### Stats
- Total log entries: <count>
- Days since creation: <count>
- Days since last update: <count>
```

3. After presenting the summary, ask:

```text
What would you like to do?
[U]pdate with a note | [A]rchive | [E]dit purpose/files | [C]ontinue working
```

4. On **Continue working**, load the thread context silently and proceed with whatever the user asks next.

### 4. list

Show all active threads with brief status. This is the default action when no action is specified.

**Steps:**

1. Scan `.temp/threads/` for all `.md` files.
2. If no threads exist, report that and suggest creating one.
3. Present a table:

```text
## Active Context Threads

| Thread | Status | Last Updated | Purpose |
|--------|--------|-------------|---------|
| <name> | active | <date> | <short purpose> |
| <name> | active | <date> | <short purpose> |

Archived: <count> thread(s) -- use `action=list` with `--all` flag to include archived.

Actions: [L]oad <name> | [C]reate new | [A]rchive <name>
```

### 5. archive

Close a thread when its work stream is complete. Requires `name`.

**Steps:**

1. Read the thread file from `.temp/threads/<name>.md`. If it does not exist, report an error.
2. If the thread is already archived, report that and exit.
3. Present a confirmation:

```text
## Archive Thread: <name>

Purpose: <purpose>
Log entries: <count>
Last updated: <date>

This will mark the thread as archived. It can still be loaded and reactivated later.

Action: [A]rchive | [C]ancel
```

4. On **Archive**: set `status: archived` in the frontmatter, add a final log entry noting the archive, and update the `updated` timestamp.
5. On **Cancel**: abort without changes.

## Required Child Agents

Run at least these child agents in parallel when creating or loading threads:

- **File scanner**: analyzes recent git history, open buffers, and working directory to detect relevant files for the thread.
- **Context summarizer**: reads the thread log and produces a concise summary of current state, open questions, and next steps.

## Thread Best Practices

- Use descriptive, kebab-case names: `auth-refactor`, `api-v2-migration`, `perf-optimization`.
- Update threads frequently -- short notes are better than no notes.
- Archive threads when work is complete rather than deleting them, so history is preserved.
- Load a thread at the start of each session to restore context.
- Tag threads to enable filtering: `backend`, `frontend`, `infrastructure`, `urgent`.
