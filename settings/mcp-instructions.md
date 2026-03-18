# Capability Routing Guide

This document describes how to route tasks to the correct skill, agent, or MCP server. It is the single reference for all routing decisions in the devkit.

## Skill Routing

Use the appropriate skill based on the user's task:

### Code Review & Quality
| Task | Skill | What it does |
|------|-------|-------------|
| Review a PR | `/pr-review <pr>` | Spawns 5 parallel agents (guidelines, bugs, security, performance, architecture). Posts inline comments. |
| Self-review before push | `/self-review` | Iterative lint → fix → test loop until clean. Auto-fix with convergence detection. |
| Generate PR description | `/pr-describe <pr>` | Analyzes diff and commits, generates structured description. GitHub and Bitbucket. |
| Auto-detect review type | `/review` | Detects PR vs document and routes to `/pr-review` or `/doc-review`. |
| Review changed code | `/simplify` | Reviews changed code for reuse, quality, and efficiency. |

### Document Writing
| Task | Skill | What it does |
|------|-------|-------------|
| Deep technical article | `/article <topic>` | Exhaustive research, principal engineer voice, 3000–6000 words. Multi-agent research phase. |
| Blog post | `/blog <topic>` | Narrative structure, opinion-driven, 800–1500 words. Research-backed. |
| Project documentation | `/project-docs` | Scans codebase for architecture, commands, APIs. Generates docs with working examples. |
| General document | `/doc-write <topic>` | Any document type with research, diagrams, and code examples. Multiple output formats. |
| Review a document | `/doc-review <url>` | Spawns 5 parallel agents (structure, accuracy, clarity, code, consistency). |

### Diagrams
| Task | Skill | What it does |
|------|-------|-------------|
| Any diagram | `/diagram <desc>` | Auto-selects Mermaid (structured) or Excalidraw (freeform) based on diagram type. |
| Mermaid diagram | `/mermaid <desc>` | 20+ diagram types (flowchart, sequence, class, ER, C4, etc.). Rendered SVG. |
| Excalidraw diagram | `/excalidraw <desc>` | Hand-drawn aesthetic. Best for architecture overviews, system diagrams. |

### Research & Communication
| Task | Skill | What it does |
|------|-------|-------------|
| Web research | `/research <topic>` | 1–5 parallel research agents. Depth: light/standard (default)/deep/exhaustive. Full citations. |
| Quick search | `/search <topic>` | Single agent, Sonnet for speed. Alias for `/research --depth=light`. Opus in multi-mode. |
| Deep research | `/deep-research <topic>` | 5 parallel agents. Alias for `/research --depth=exhaustive`. |
| Slack message | `/slack-compose` | Tone-aware composition (professional, casual, technical, announcement). Draft-first. |
| Publish to Confluence | `/confluence-publish` | Converts markdown to Confluence storage format with diagrams and attachments. |

### Frontend & Design
| Task | Skill | What it does |
|------|-------|-------------|
| UI design | `/frontend-design <desc>` | Generates 5 distinct design variations. Interactive selection. Production-ready code. |

### Utility
| Task | Skill | What it does |
|------|-------|-------------|
| Test MCP connections | `/validate-mcp` | Tests all configured MCP servers. Helps with OAuth flows. |
| Create new skill | `/create-skill <name>` | Creates devkit-compatible skills with quality loops and agent delegation. |
| Multi-model mode | `/multi <task>` or `--multi` flag | Runs task through multiple AI CLIs in parallel. Opus consensus. |

## Agent Routing

Skills delegate to specialized agents via the Agent tool (Agentic Teams). Do not call agents directly — let skills orchestrate them.

| Agent | Spawned By | Purpose |
|-------|-----------|---------|
| `code-reviewer` | `/pr-review`, `/self-review` | Multi-perspective code analysis (bugs, security, performance, architecture) |
| `doc-reviewer` | `/doc-review`, `/doc-write` | Multi-dimensional document analysis (structure, accuracy, clarity, code, consistency) |
| `research-agent` | `/research`, `/article`, `/blog`, `/doc-write` | Deep web research with source evaluation and citation |
| `diagram-agent` | `/diagram` | Selects Mermaid or Excalidraw and delegates to specialist |
| `mermaid-agent` | `diagram-agent` | Mermaid diagram generation (all v11 types) |
| `excalidraw-agent` | `diagram-agent` | Excalidraw JSON generation with validation |
| `code-snippet-agent` | `/doc-review`, `/article`, `/blog` | Expressive-code block writing and review |
| `frontend-designer` | `/frontend-design` | Distinctive UI design with accessibility and responsive requirements |
| `consensus-agent` | `/multi` | Synthesizes outputs from multiple AI models into unified consensus |

## Quality Standards

All skills enforce these quality dimensions at Principal Engineer level:

- **Performance**: Optimize hot paths, lazy loading, caching with invalidation, pagination, batch operations, bundle size tracking
- **Security**: Input validation, auth/authz, no secrets committed, OWASP top 10, dependency auditing, rate limiting
- **Accessibility**: WCAG 2.1 AA, semantic HTML, keyboard navigation, color contrast (4.5:1), ARIA, screen reader testing
- **Maintainability**: Clear naming, DRY (3+ threshold), test coverage, documentation for public APIs, atomic commits
- **DX**: Typed APIs, helpful error messages, examples, quick starts, structured logging
- **Cost**: Bundle size budgets, query efficiency, resource utilization, TCO analysis for tool choices

All documents target senior audience (staff/principal engineers, stakeholders, management). Technical accuracy is mandatory — all claims require citations to authoritative sources.

## MCP Server Routing

Use the appropriate MCP tools based on the service or data source involved.

### Google Drive MCP (`google-drive`)

Use for all interactions with Google Workspace file-based services:

- **Google Docs**: reading, creating, editing, formatting documents
- **Google Sheets**: reading, creating, updating spreadsheets; formatting cells; adding data validation
- **Google Slides**: reading, creating, editing presentations; adding shapes, text boxes, images
- **Google Drive**: searching files, listing folders, uploading/downloading files, managing permissions
- **Google Calendar** (via Drive MCP): creating, reading, updating, deleting calendar events

Tool prefix: `mcp__google-drive__`

### Atlassian Confluence MCP (`atlassian-confluence`)

Use for all interactions with Confluence:

- **Pages**: creating, reading, updating, deleting, moving pages
- **Page content**: getting page diffs, history, views, children, images
- **Comments**: adding comments, replying to comments, getting comments
- **Labels**: adding and getting labels on pages
- **Attachments**: uploading, downloading, deleting attachments
- **Search**: searching pages and users within Confluence

Tool prefix: `mcp__atlassian-confluence__confluence_`

### Bitbucket MCP (`bitbucket`)

Use for all interactions with Bitbucket:

- **Pull Requests**: creating, updating, approving, declining, merging PRs
- **PR Comments**: adding, updating, resolving, reopening comments
- **PR Reviews**: getting activity, diffs, commits, statuses
- **PR Tasks**: creating and updating tasks on PRs
- **Draft PRs**: creating, publishing, converting to draft
- **Repositories**: listing repos, getting repo info
- **Pipelines**: listing runs, getting steps, viewing logs, running/stopping pipelines
- **Branching Models**: getting and updating branching model settings

Tool prefix: `mcp__bitbucket__`

### Slack MCP (`claude_ai_Slack`)

Use for all interactions with Slack:

- **Messages**: sending messages, scheduling messages, reading channels and threads
- **Search**: searching channels, users, public messages, public and private messages
- **Canvases**: creating, reading, updating Slack canvases
- **User profiles**: reading user profile information
- **Drafts**: sending message drafts for review

Tool prefix: `mcp__claude_ai_Slack__slack_`

### Gmail MCP (`claude_ai_Gmail`)

Use for all email operations:

- **Reading**: reading individual messages, reading threads
- **Search**: searching messages with Gmail query syntax
- **Drafts**: creating drafts, listing drafts
- **Labels**: listing labels
- **Profile**: getting the authenticated user's profile

Tool prefix: `mcp__claude_ai_Gmail__gmail_`

### Google Calendar MCP (`claude_ai_Google_Calendar`)

Use for calendar-specific operations (as an alternative to the Google Drive calendar tools):

- **Events**: creating, reading, updating, deleting calendar events
- **Scheduling**: finding meeting times, finding free time
- **Calendars**: listing available calendars
- **RSVP**: responding to event invitations

Tool prefix: `mcp__claude_ai_Google_Calendar__gcal_`

## MCP + Skill Chaining Rules

1. **Match by service**: Always route to the MCP that owns the service. Do not use the wrong MCP even if tool names seem similar.
2. **Calendar operations**: Both Google Drive MCP and Google Calendar MCP can handle calendar events. Prefer Google Calendar MCP (`gcal_`) for event-focused operations. Use Google Drive MCP for calendar operations mixed with other Drive work.
3. **Prefer specificity**: If a task only involves one service, use only that service's MCP. Do not load unnecessary tools.
4. **Chaining**: It is valid to use multiple MCPs in a single workflow (e.g., read a Confluence page, then post a summary to Slack).
5. **Skill + MCP**: Skills automatically use the correct MCP based on context. For example, `/pr-review` with a Bitbucket URL uses the bitbucket MCP; `/doc-review` with a Confluence URL uses the atlassian-confluence MCP.
6. **Agent delegation**: Skills delegate to agents, not the other way around. Always invoke the skill command — it handles agent orchestration internally.
7. **Multi-model mode**: The `/multi` skill (or `--multi` flag on any skill) runs the same task through multiple AI CLIs (claude, codex, gemini-cli, cursor-cli) in parallel. Opus synthesizes the consensus result. This replaces the old Multi MCP server. Multi-model is CLI-based and requires no MCP server configuration.
