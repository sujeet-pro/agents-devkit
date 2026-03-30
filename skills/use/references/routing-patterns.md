# Skill Routing Patterns

Pick the smallest useful pipeline that covers the confirmed intent.

## Common Routing Patterns

### Review a PR or branch

1. `/coding`
2. `/review`

### Build or change product behavior

1. `/coding`
2. `/research` when patterns or external docs matter
3. `/plan --mode brainstorm` when the ask is still fuzzy
4. `/spec --mode write` when requirements must be formalized
5. `/plan --mode write`
6. `/develop --mode implement`
7. `/review`

### Fix a bug

1. `/coding`
2. `/plan --mode write` for Small+ bugs or unclear fixes
3. `/develop --mode debug`
4. `/develop --mode implement`
5. `/review`

### Write or revise documents

1. `/research` when facts or comparisons are needed
2. `/doc-writing`
3. `/plan --mode write` for Medium+ writing tasks with multiple deliverables
4. `/write`
5. `/review-doc`

### Audit or research

1. `/coding` when the codebase matters
2. `/research` or `/audit`
3. `/plan --mode write` if there are multiple workstreams or follow-up actions
4. `/write` when the output needs synthesis

### Design or UI work

1. `/coding` when touching existing frontend code
2. `/design` for new UI/UX design direction
3. `/review --focus ui` for auditing existing frontend

### Project setup or tooling

1. `/setup` for CLI tools and MCP servers
2. `/project --mode init` for new project scaffolding

## Parameter Resolution

Before showing the plan to the user:

1. read the selected skill's `argument-hint`
2. read the skill's `Parameters` and `Behavior Variations`
3. infer what can be inferred from the prompt
4. mark everything else as default or needs confirmation

Show the user the resolved pipeline in one compact view. Let them:

- approve it
- remove a skill
- add a skill
- simplify the ask
- change an inferred parameter
