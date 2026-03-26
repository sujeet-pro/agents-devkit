---
name: idea-capture
description: "Use when capturing forward-looking ideas, managing a backlog parking lot, or reviewing and promoting deferred items"
user_invocable: true
arguments:
  - name: action
    description: "Action: capture, review, promote, list (default: capture)"
    required: false
  - name: idea
    description: "Idea description (for action=capture)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), auto-approve"
    required: false
---

# Idea Capture

Use `skills/_references/agentic-teams.md` and `skills/_references/preflight-validations.md`.

Use this when you want to park an idea for later without derailing the current work, or when you need to review and triage accumulated ideas.

## Preflight

Before running, execute:

`zsh scripts/check-skill-deps.zsh idea-capture`

## Idea Storage

All ideas are stored as individual markdown files in `.temp/ideas/`. Each file is named `<slug>.md` where `<slug>` is a kebab-cased version of the idea title.

### Idea File Format

```markdown
---
idea_id: <id>
created: <ISO-8601>
status: captured | promoted | deferred | removed
priority: low | medium | high
tags: [<tag1>, <tag2>]
---
# Idea: <title>

## Description
<what and why>

## Trigger Condition
<when this idea becomes relevant — e.g., "when we hit 1000 users", "after v2 ships">

## Notes
<additional context>
```

## Actions

### 1. Capture (`action=capture`)

Save a new idea to the backlog parking lot.

**Workflow:**

1. **Parse the idea.** If `idea` argument is provided, extract the title and description from it. If not provided, ask the user for a brief description.
2. **Clarify details.** In interactive mode, prompt for any missing fields:
   - Title (short, descriptive name)
   - Description (what and why)
   - Trigger condition (when does this become relevant?)
   - Priority (`low`, `medium`, `high` — default: `medium`)
   - Tags (comma-separated labels for grouping)
3. **Generate the slug.** Kebab-case the title, e.g., "Add Dark Mode" becomes `add-dark-mode`.
4. **Generate the idea ID.** Use format `idea-<YYYYMMDD>-<slug>`.
5. **Write the file.** Save to `.temp/ideas/<slug>.md` using the idea file format above.
6. **Confirm.** Display a summary:

```text
Captured: <title>
Priority: <priority>
Tags: <tags>
Trigger: <condition>
File: .temp/ideas/<slug>.md
```

In `auto-approve` mode, use sensible defaults for any missing fields and skip confirmation prompts.

### 2. Review (`action=review`)

Present all captured ideas one-by-one for interactive triage.

**Required Child Agents:**

Run at least these child agents in parallel:

- **Inventory agent**: reads all files in `.temp/ideas/`, parses frontmatter, and produces a sorted inventory (by priority descending, then age descending).
- **Context agent**: reads the current project state (recent git history, existing plans in `.temp/`, specs, and active tasks) to assess relevance of each idea against current project direction.

**Workflow:**

1. **Load ideas.** Read all `.md` files from `.temp/ideas/` where `status` is `captured` or `deferred`.
2. **Sort.** Order by priority (high first), then by age (oldest first).
3. **Present each idea** using the interactive review format:

```text
## Idea [N/total] - [priority] - <title>

Description: <brief>
Trigger: <condition>
Age: <days since capture>

Action: [P]romote to spec/plan | [D]efer | [R]emove | [E]dit | [S]kip
```

4. **Handle actions:**
   - **[P]romote**: Update `status` to `promoted` and invoke the promote workflow (see action 3).
   - **[D]efer**: Update `status` to `deferred`. Optionally add a note about why.
   - **[R]emove**: Update `status` to `removed`. Ask for confirmation first.
   - **[E]dit**: Allow inline editing of description, trigger, priority, or tags. Rewrite the file.
   - **[S]kip**: Move to the next idea without changes.

5. **Summary.** After reviewing all ideas, display a triage summary:

```text
## Review Summary

Reviewed: <N> ideas
Promoted: <count>
Deferred: <count>
Removed: <count>
Skipped: <count>
Remaining in backlog: <count>
```

### 3. Promote (`action=promote`)

Convert an idea into a spec task or execution plan.

**Workflow:**

1. **Select the idea.** If invoked from review, use the current idea. Otherwise, list all `captured` or `deferred` ideas and ask the user to pick one.
2. **Choose target.** Ask the user:

```text
Promote "<title>" to:
[S]pec — create a detailed specification via /devkit:spec-write
[P]lan — create an execution plan via /devkit:plan-write
[T]ask — create a quick-task via /devkit:quick-task
```

3. **Hand off.** Pass the idea description, trigger condition, and notes as context to the chosen skill.
4. **Update status.** Set the idea `status` to `promoted` and add a note with the path to the created spec/plan/task.

### 4. List (`action=list`)

Display all ideas grouped by priority and tag.

**Workflow:**

1. **Load ideas.** Read all `.md` files from `.temp/ideas/`.
2. **Group and display.** Present ideas grouped first by priority, then by tag:

```text
## Ideas Backlog

### High Priority (N)
- [captured] <title> — <brief description> (tags: <tags>) [<age> days]
- [deferred] <title> — <brief description> (tags: <tags>) [<age> days]

### Medium Priority (N)
- [captured] <title> — <brief description> (tags: <tags>) [<age> days]

### Low Priority (N)
- [captured] <title> — <brief description> (tags: <tags>) [<age> days]

### Promoted (N)
- [promoted] <title> — promoted to <target> [<age> days]

### Removed (N)
- [removed] <title> [<age> days]

---
Total: <N> ideas | Captured: <n> | Deferred: <n> | Promoted: <n> | Removed: <n>
```

3. **Filter support.** If the user provides a tag or priority filter, show only matching ideas.

## Output

All idea files are saved to `.temp/ideas/`.

Intermediary artifacts (review summaries, promotion logs) are saved to `.temp/ideas/_logs/`.

## Adjacent Skills

- `/devkit:spec-write` for turning a promoted idea into a detailed specification
- `/devkit:plan-write` for turning a promoted idea into an execution plan
- `/devkit:plan-brainstorm` for exploring an idea before committing to a spec or plan
- `/devkit:project-init` for bootstrapping a new project from an idea
- `/devkit:quick-task` for converting simple ideas into immediate tasks
