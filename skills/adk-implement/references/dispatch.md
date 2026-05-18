# adk-implement — input dispatch

> Used in Phase 0. `scripts/classify-input.py` (this skill's local script) wraps `scripts/url_classifier.py` and emits the chosen sub-flow.

| Input shape | Sub-flow | Reference |
|---|---|---|
| Jira URL or `<KEY>-<NUM>` | from-jira | `from-jira.md` (specialized — most common) |
| GitHub issue URL or `#<num>` | from-issue | `from-issue.md` (specialized — 2nd most common) |
| Confluence URL (TDD page) | from-tdd | `from-tdd.md` |
| Confluence URL (other) | from-confluence | `from-confluence.md` |
| Slack permalink | from-slack-thread | `from-slack-thread.md` |
| Freeform description | greenfield | `greenfield.md` |
| Mixed (URL + description) | hybrid — fan-out fetch, then default to the URL's sub-flow with the description as additional context | n/a |

Routing is data-driven (not AI-driven). If multiple inputs match, the URL with the strongest discriminator wins (Jira > GH PR > GH issue > Confluence > Slack > freeform).

## When the classifier is wrong

If the user invokes `/adk-implement <ambiguous-input>` and the classifier picks a sub-flow that doesn't fit, the advisor phase asks: "I dispatched to `<sub-flow>` but it doesn't look like a clear match — confirm or pick another?" Then logs a `dispatch-override` fork to the decision log.
