# Quick Action Workflow

Shape: **confirm → execute → verify**

For narrow tasks with clear intent and a single execution path. No research, approach selection, or planning phases — the task is well-understood and has one obvious way to proceed.

## When to Use

- Diagram generation (Mermaid, Excalidraw, draw.io, Graphviz)
- Chart rendering
- Commits and PR descriptions
- Session handoff / context threads
- Setup and configuration
- UAT test extraction
- Quick fixes (typos, config tweaks, single-file changes)
- Worktree creation

## Steps

### 1. Confirm

Restate the goal and confirm intent. Keep it brief — this is a narrow task.

- Restate the user's goal in one line
- List key assumptions (output location, format, scope)
- For `--auto` or parent-skill invocation: skip confirmation, proceed directly
- Complexity scaling: 1-line inline for trivial, 2-3 lines with assumptions for small/medium

### 2. Execute

Do the work directly. No wave decomposition or parallel agents needed.

- Execute the task in a single pass
- Follow the skill's specific execution instructions
- Save artifacts to the expected output location

### 3. Verify

Quick validation pass — confirm the output is correct and report.

- Check output exists and is well-formed (render, lint, syntax check)
- Report what was created/changed
- Offer next steps if applicable
- No iteration loop — if something is wrong, the user will ask for a fix

## `--auto` Behavior

All steps execute without confirmation pauses. Step 1 states intent but does not wait for approval.

## Artifacts

Save output to the skill-specific location. No `.temp/` phase artifacts unless the skill explicitly requires them.

## Complexity Scaling

| Step | Trivial/Small | Medium |
|------|---------------|--------|
| Confirm | 1-line inline | Brief with assumptions |
| Execute | Direct | Direct |
| Verify | Existence check | Check + brief summary |
