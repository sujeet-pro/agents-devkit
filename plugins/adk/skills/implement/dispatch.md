# implement — input dispatch

Route by the shape of the input. Fetch the requirement, then plan.

| Input shape | Sub-flow | How to fetch |
|---|---|---|
| Jira URL or `KEY-123` | from-jira (most common) | Atlassian MCP — summary, description, acceptance criteria, linked design docs |
| GitHub issue URL or `#N` | from-issue | `gh issue view <url-or-#N> --json title,body,labels,comments` |
| Confluence URL (a TDD / spec page) | from-tdd | Atlassian MCP — read the page as markdown |
| Slack permalink | from-slack-thread | Slack MCP — read the thread (one hop) |
| Freeform prose ("build the X") | greenfield | take the text as the spec; ask the one question that unblocks it |
| Mixed (URL + prose) | hybrid | fan out the `context-gatherer` agent; the URL's sub-flow leads, prose is extra context |

Routing is by data, not vibes. If several inputs match, the strongest discriminator wins: Jira > GitHub issue > Confluence > Slack > freeform.

## GitHub vs the rest

- **GitHub** (issues, PRs, code, commits) is always the **`gh` CLI**. Never the GitHub MCP, never raw REST.
- **Jira / Confluence** is the Atlassian MCP. **Slack** is the Slack MCP. A raw web URL is `WebFetch`.

## When the classifier is wrong

If the picked sub-flow doesn't fit, say so in Phase 1 — "this reads like freeform, not a Jira ticket; confirm or correct?" — then proceed on the corrected route. Don't silently force a bad fit.
