# MCP Routing Guide

This document describes when to use each MCP (Model Context Protocol) server. Use the appropriate MCP tools based on the service or data source involved.

## Google Drive MCP (`google-drive`)

Use for all interactions with Google Workspace file-based services:

- **Google Docs**: reading, creating, editing, formatting documents
- **Google Sheets**: reading, creating, updating spreadsheets; formatting cells; adding data validation
- **Google Slides**: reading, creating, editing presentations; adding shapes, text boxes, images
- **Google Drive**: searching files, listing folders, uploading/downloading files, managing permissions
- **Google Calendar** (via Drive MCP): creating, reading, updating, deleting calendar events

Tool prefix: `mcp__google-drive__`

## Atlassian Confluence MCP (`atlassian-confluence`)

Use for all interactions with Confluence:

- **Pages**: creating, reading, updating, deleting, moving pages
- **Page content**: getting page diffs, history, views, children, images
- **Comments**: adding comments, replying to comments, getting comments
- **Labels**: adding and getting labels on pages
- **Attachments**: uploading, downloading, deleting attachments
- **Search**: searching pages and users within Confluence

Tool prefix: `mcp__atlassian-confluence__confluence_`

## Bitbucket MCP (`bitbucket`)

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

## Slack MCP (`claude_ai_Slack`)

Use for all interactions with Slack:

- **Messages**: sending messages, scheduling messages, reading channels and threads
- **Search**: searching channels, users, public messages, public and private messages
- **Canvases**: creating, reading, updating Slack canvases
- **User profiles**: reading user profile information
- **Drafts**: sending message drafts for review

Tool prefix: `mcp__claude_ai_Slack__slack_`

## Gmail MCP (`claude_ai_Gmail`)

Use for all email operations:

- **Reading**: reading individual messages, reading threads
- **Search**: searching messages with Gmail query syntax
- **Drafts**: creating drafts, listing drafts
- **Labels**: listing labels
- **Profile**: getting the authenticated user's profile

Tool prefix: `mcp__claude_ai_Gmail__gmail_`

## Google Calendar MCP (`claude_ai_Google_Calendar`)

Use for calendar-specific operations (as an alternative to the Google Drive calendar tools):

- **Events**: creating, reading, updating, deleting calendar events
- **Scheduling**: finding meeting times, finding free time
- **Calendars**: listing available calendars
- **RSVP**: responding to event invitations

Tool prefix: `mcp__claude_ai_Google_Calendar__gcal_`

## Multi MCP (`multi`)

Use for multi-model interactions and comparisons:

- **Chat**: have a conversation with a specific model (`mcp__multi__chat`)
- **Code Review**: get code reviewed by another model (`mcp__multi__codereview`)
- **Compare**: compare responses from multiple models (`mcp__multi__compare`)
- **Debate**: have models debate a topic (`mcp__multi__debate`)
- **Models**: list available models (`mcp__multi__models`)

Tool prefix: `mcp__multi__`

## Routing Rules

1. **Match by service**: Always route to the MCP that owns the service. Do not use the wrong MCP even if tool names seem similar.
2. **Calendar operations**: Both Google Drive MCP and Google Calendar MCP can handle calendar events. Prefer Google Calendar MCP (`gcal_`) for event-focused operations. Use Google Drive MCP for calendar operations mixed with other Drive work.
3. **Prefer specificity**: If a task only involves one service, use only that service's MCP. Do not load unnecessary tools.
4. **Chaining**: It is valid to use multiple MCPs in a single workflow (e.g., read a Confluence page, then post a summary to Slack).
