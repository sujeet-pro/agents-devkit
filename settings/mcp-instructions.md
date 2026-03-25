# Capability Routing Guide

This file is the routing reference for AKIT's software-development workflows.

Before any MCP-backed workflow, run `zsh scripts/check-skill-deps.zsh <skill> ...context...` with the real input and then perform one lightweight MCP read to confirm live connectivity.

## Skill Routing

### Reviews

| Task | Skill | Notes |
|------|-------|-------|
| Review a GitHub or Bitbucket PR | `/review-pr <pr>` | Reads existing comments first, reconciles thread state, and can post comments back |
| Review local work before push | `/review-local` | Reviews staged, unstaged, or branch-local changes without auto-fixing them |
| Route review target automatically | `/review <target>` | Chooses PR, document, or codebase review |
| Review a local doc, Confluence page, or Google Doc | `/review-doc <source>` | Markdown-first review artifact plus optional source comments |
| Review an entire repository | `/review-codebase` | Architecture, maintainability, docs, test, and modernization audit |
| Generate a PR description | `/pr-describe <pr>` | Diff-based summary with risk, tests, and docs impact |

### Documentation And Research

| Task | Skill | Notes |
|------|-------|-------|
| Write engineering docs | `/write-doc <topic>` | Markdown, Google Docs, Confluence, or PDF with direct revision support |
| Generate or refresh project docs | `/write-project-docs` | Reads the codebase and emits professional docs plus diagrams |
| Write a deep engineering article | `/write-article <topic>` | Exhaustive research plus diagrams and code examples |
| Write an engineering blog or update | `/write-blog <topic>` | Shorter narrative format with technical grounding |
| Research a topic | `/research <topic>` | Official docs, specs, source code, and migration notes |
| Quick research | `/research-quick <topic>` | Two-agent quick pass |
| Exhaustive research | `/research-deep <topic>` | Five-pass research and synthesis |

### Diagrams And Design

| Task | Skill | Notes |
|------|-------|-------|
| Create a diagram | `/diagram <desc>` | Chooses Mermaid, Excalidraw, or draw.io first; falls back to Graphviz only when needed |
| Maintain Graphviz diagrams | `/diagram-graphviz <target>` | Use for existing DOT assets or strict layout cases |
| Render diagram sources | `/diagramkit render ...` | Produces rendered outputs without losing source files |
| Convert diagram output for delivery | `/diagram-convert <input>` | Use only when PNG or JPEG is required |
| Create frontend or design-system directions | `/design-frontend <desc>` | Multiple parallel design passes |

### Utility

| Task | Skill | Notes |
|------|-------|-------|
| Validate MCP availability | `/manage-validate` | Checks GitHub, Bitbucket, Confluence, and Google Drive |
| Create or update an AKIT skill | `/manage-skill <name>` | Uses the shared AKIT contracts |
| Run multiple providers or models | `/agent-multi <task>` | Respects host constraints, especially Cursor |

## Agent Routing

| Agent | Purpose |
|-------|---------|
| `code-reviewer` | Diff-aware review across correctness, security, performance, tests, and code patterns |
| `repo-auditor` | Whole-codebase architecture and maintainability review |
| `doc-reviewer` | Technical document review, delivery-fit checks, and doc quality |
| `research-agent` | Primary-source and implementation research |
| `code-snippet-agent` | Code examples and code-block review |
| `source-publisher` | Post markdown findings back to GitHub, Bitbucket, Confluence, or Google Docs |
| `frontend-designer` | Frontend and design-system direction setting |
| `consensus-agent` | Merge multiple agent or provider outputs |

## MCP Routing

### GitHub MCP (`github`)

Use for:

- reading PRs, comments, commits, and repo metadata
- posting PR review comments or updating PR bodies

Tool prefix: `mcp__github__`

### Bitbucket MCP (`bitbucket`)

Use for:

- reading PRs, comments, commits, and repo metadata
- posting PR review comments and updating PRs

Tool prefix: `mcp__bitbucket__`

### Atlassian Confluence MCP (`atlassian-confluence`)

Use for:

- reading and updating pages
- adding comments
- uploading attachments such as diagrams and exported docs

Tool prefix: `mcp__atlassian-confluence__confluence_`

### Google Drive MCP (`google-drive`)

Use for:

- reading and updating Google Docs
- accessing Drive files used as source material
- publishing generated documents back to Google Docs

Tool prefix: `mcp__google-drive__`

## Chaining Rules

1. Prefer the source-native MCP over shelling out to service-specific CLIs.
2. Validate only the MCP implied by the real input URL or publish target before analysis.
3. Produce markdown first, then publish back to the origin if the workflow requires it.
4. Read existing source discussions before posting new comments.
5. Resolve handled-but-open comments and reopen critical outdated comments when the source supports it.
6. Use child-agent teams for non-trivial work whenever the current platform supports them.
