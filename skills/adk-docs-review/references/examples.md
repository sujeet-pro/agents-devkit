# Examples: adk-docs-review

These show the shape of inputs and outputs this skill expects. Adapt the wording to the user's actual task.

## Trigger phrases
- "Run `adk-docs-review` on <target>"
- A user request that matches the skill's "When to use" section in `SKILL.md`.

## Sample invocation
```
adk-docs-review "<one-sentence task description>" [--auto]
```

## Sample report shape
- Lead with the answer / finding / recommendation.
- Show the validation evidence inline (commands run, files touched, tests passed).
- End with remaining risks and an offer to expand.
