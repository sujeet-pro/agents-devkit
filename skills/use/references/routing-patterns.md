# Skill Routing Patterns

Pick the smallest useful pipeline that covers the confirmed intent.

## Common Routing Patterns

### Review a PR or branch

1. `/adk-coding`
2. `/adk-review-pr`

### Build or change product behavior

1. `/adk-coding`
2. `/adk-research` when patterns or external docs matter
3. `/adk-plan --mode brainstorm` when the ask is still fuzzy
4. `/adk-spec --mode write` when requirements must be formalized
5. `/adk-plan --mode write`
6. `/adk-develop --mode implement`
7. `/adk-review-pr`

### Fix a bug

1. `/adk-coding`
2. `/adk-plan --mode write` for Small+ bugs or unclear fixes
3. `/adk-develop --mode debug`
4. `/adk-develop --mode implement`
5. `/adk-review-pr`

### Write or revise documents

1. `/adk-research` when facts or comparisons are needed
2. `/adk-doc-writing`
3. `/adk-plan --mode write` for Medium+ writing tasks with multiple deliverables
4. `/adk-write`
5. `/adk-review-doc`

### Audit or research

1. `/adk-coding` when the codebase matters
2. `/adk-research` or `/adk-audit`
3. `/adk-plan --mode write` if there are multiple workstreams or follow-up actions
4. `/adk-write` when the output needs synthesis

### Design or UI work

1. `/adk-coding` when touching existing frontend code
2. `/adk-design` for new UI/UX design direction
3. `/adk-review-pr --focus ui` for auditing existing frontend

### Project setup or tooling

1. `/adk-setup` for CLI tools and MCP servers
2. `/adk-project --mode init` for new project scaffolding

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
