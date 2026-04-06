# Skill Routing Patterns

Pick the smallest useful pipeline that covers the confirmed intent.

## Common Routing Patterns

### Review a PR or branch

1. `/adk:coding`
2. `/adk:code-review-pr`

### Review a whole repo

1. `/adk:coding`
2. `/adk:code-review-repo`

### Fix PR comments / address review feedback

1. `/adk:coding`
2. `/adk:code-review-fix`

### Build or change product behavior

1. `/adk:coding`
2. `/adk:research` when patterns or external docs matter
3. `/adk:plan --mode brainstorm` when the ask is still fuzzy
4. `/adk:spec --mode write` when requirements must be formalized
5. `/adk:plan --mode write`
6. `/adk:dev-build --mode implement`
7. `/adk:code-review-pr`

### Fix a bug

1. `/adk:coding`
2. `/adk:plan --mode write` for Small+ bugs or unclear fixes
3. `/adk:dev-build --mode debug`
4. `/adk:dev-build --mode implement`
5. `/adk:code-review-pr`

### Write or revise documents

1. `/adk:research` when facts or comparisons are needed
2. `/adk:docs-guidelines`
3. `/adk:plan --mode write` for Medium+ writing tasks with multiple deliverables
4. `/adk:docs-write`
5. `/adk:docs-review`

### Generate repo documentation

1. `/adk:coding` to understand the codebase
2. `/adk:docs-repo`

### Review existing documentation

1. `/adk:docs-review`

### Update or manage documentation

1. `/adk:docs-guidelines`
2. `/adk:docs-crud`

### Audit or research

1. `/adk:coding` when the codebase matters
2. `/adk:research` or `/adk:audit`
3. `/adk:plan --mode write` if there are multiple workstreams or follow-up actions
4. `/adk:docs-write` when the output needs synthesis

### Design or UI work

1. `/adk:coding` when touching existing frontend code
2. `/adk:design` for new UI/UX design direction
3. `/adk:code-review-pr --focus ui` for auditing existing frontend

### Create diagrams

1. `/adk:diagram` for auto-detected engine
2. `/adk:diagram-mermaid` for Mermaid (sequence, flowchart, class, etc.)
3. `/adk:diagram-excalidraw` for Excalidraw hand-drawn style
4. `/adk:diagram-graphviz` for Graphviz DOT
5. `/adk:diagram-drawio` for Draw.io precise layouts

### Project setup or tooling

1. `/adk:setup` for CLI tools and MCP servers
2. `/adk:project --mode init` for new project scaffolding

### Track upstream dependencies

1. `/adk:deps-tracker`

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
