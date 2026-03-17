---
name: slack-compose
description: Compose a Slack message from a prompt and send it to a channel or thread
user_invocable: true
arguments:
  - name: prompt
    description: "What the message should communicate"
    required: true
  - name: channel
    description: "Slack channel name or ID to send to"
    required: false
  - name: thread
    description: "Thread timestamp to reply to (optional)"
    required: false
  - name: tone
    description: "Message tone: professional, casual, technical, announcement (default: professional)"
    required: false
  - name: draft
    description: "If true, only show draft without sending (default: true)"
    required: false
---

# Slack Compose Skill

Compose well-crafted Slack messages based on a prompt, with optional context-awareness from existing conversations, draft review, and sending capability.

## Instructions

Follow each phase in order. Always default to draft-only mode unless the user explicitly asks to send.

---

## Phase 1: Gather Context

### 1.1 Channel Context (if channel is specified)

If a `channel` is provided, read recent messages to understand the conversation context:

- Use `mcp__claude_ai_Slack__slack_read_channel` to read the latest messages from the channel
- Note the general tone, topics being discussed, and any relevant ongoing threads
- Identify key participants and their communication styles

### 1.2 Thread Context (if thread is specified)

If a `thread` timestamp is provided, read the full thread:

- Use `mcp__claude_ai_Slack__slack_read_thread` to read all messages in the thread
- Understand what has been discussed so far
- Identify who has participated and what positions/questions have been raised
- Determine what kind of reply would be most helpful

### 1.3 Channel Discovery (if channel is not specified)

If no channel is provided:

- Ask the user which channel they want to send to
- Optionally use `mcp__claude_ai_Slack__slack_search_channels` to help find the right channel
- Once identified, read recent messages for context (as in 1.1)

### 1.4 Tone Detection

If `tone` is not specified, infer the appropriate tone from:
- The channel context (engineering channels tend to be technical, general channels more casual)
- The thread context (match the existing conversation tone)
- The nature of the prompt (bug reports → technical, team updates → professional, celebrations → casual)

Default to **professional** if no context is available.

---

## Phase 2: Compose Message

### 2.1 Message Drafting

Compose the message following these guidelines based on the tone:

**Professional:**
- Clear and direct
- Use bullet points for multiple items
- Proper grammar and punctuation
- Minimal emoji (at most 1-2 contextually appropriate ones)
- Structure: context → main point → action items

**Casual:**
- Conversational and friendly
- Emoji usage is fine
- Shorter sentences
- Can use informal language
- Match the energy of the channel

**Technical:**
- Precise and detailed
- Use code blocks (`` ` `` for inline, ` ``` ` for blocks) for technical terms, commands, file paths
- Include relevant technical details
- Link to documentation or PRs where relevant
- Structure: problem/context → details → next steps

**Announcement:**
- Bold the headline or key message
- Use clear sections with headers (bold text as pseudo-headers)
- Include all relevant details (who, what, when, where, why)
- End with clear action items or next steps
- Use `:mega:` or `:loudspeaker:` emoji at the start

### 2.2 Slack Formatting

Use proper Slack mrkdwn formatting:
- `*bold*` for emphasis
- `_italic_` for subtle emphasis
- `` `code` `` for inline code
- ```` ```code block``` ```` for multi-line code
- `> quote` for quoting others
- `• ` or `- ` for bullet points (Slack renders both)
- `:emoji_name:` for emoji
- `<@USER_ID>` for mentions (only if the user specifically asks to mention someone)
- `<#CHANNEL_ID>` for channel links

### 2.3 Message Quality Rules

- Keep messages **concise** — say more with less
- Front-load the most important information
- If the message is longer than ~5 lines, use structure (bullets, sections)
- Include code snippets if it's a technical message and they add clarity
- Do NOT use `@here` or `@channel` unless the user explicitly requests it
- Do NOT mention people unless the user explicitly requests it
- Ensure the message answers: What do I need to know? What do I need to do?

---

## Phase 3: Draft Review

### 3.1 Present the Draft

Show the composed message to the user formatted as it would appear in Slack:

```
---
**Draft Message** → #channel-name
---

[The composed message exactly as it would appear in Slack]

---
```

If it's a thread reply, show:
```
---
**Draft Reply** → #channel-name (thread)
---

[The composed message]

---
```

### 3.2 Ask for Feedback

After presenting the draft, ask:

> "Here's the draft. Would you like to:
> - **Send it** as-is
> - **Edit** — tell me what to change
> - **Adjust tone** — make it more casual/formal/technical
> - **Shorten** or **expand** it
> - **Cancel** — discard the draft"

### 3.3 Iterate

If the user requests changes:
- Apply the requested modifications
- Show the updated draft
- Ask for approval again
- Repeat until the user is satisfied or cancels

---

## Phase 4: Send

### 4.1 Pre-Send Checks

Before sending, verify:
- The `draft` argument is NOT `true` (or the user has explicitly said "send it")
- The user has reviewed and approved the message
- A valid channel is specified

If `draft` is `true` (the default) and the user hasn't explicitly asked to send:
- Do NOT send the message
- Simply confirm: "Draft saved. Let me know when you'd like to send it or if you want to make changes."

### 4.2 Send the Message

If approved for sending:

**To a channel (no thread):**
- Use `mcp__claude_ai_Slack__slack_send_message` with the channel and composed message

**To a thread:**
- Use `mcp__claude_ai_Slack__slack_send_message` with the channel, thread timestamp, and composed message

### 4.3 Confirm

After sending:
- Confirm the message was sent successfully
- Show which channel/thread it was sent to
- If available, provide a link to the message

### 4.4 Error Handling

If sending fails:
- Show the error message
- Suggest possible fixes (wrong channel name, permissions issue, etc.)
- Offer to retry or save the draft for manual sending
- Never silently fail — always inform the user

---

## Default Behavior Summary

| Setting | Default | Notes |
|---------|---------|-------|
| `draft` | `true` | Always draft-only unless explicitly told to send |
| `tone` | `professional` | Inferred from context when possible |
| `channel` | none | Will ask user if not provided |
| `thread` | none | Sends to channel top-level if not provided |

**Critical rule**: NEVER send a message without explicit user approval. The default behavior is draft-only. The user must say "send it", "send", "yes send", or similar explicit confirmation before any message is actually sent to Slack.
