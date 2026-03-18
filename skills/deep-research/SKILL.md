---
name: deep-research
description: "Exhaustive multi-agent research with 5 parallel agents — alias for /research --depth=exhaustive"
user_invocable: true
arguments:
  - name: topic
    description: "Topic to research"
    required: true
  - name: output
    description: "Output format: markdown, outline, notes (default: markdown)"
    required: false
  - name: save
    description: "File path to save research output (optional)"
    required: false
---

# Deep Research

Alias for `/research --depth=exhaustive`. Spawns 5 parallel research agents for comprehensive coverage.

## Delegation

Invoke the `/research` skill with `depth=exhaustive` and forward all other arguments:

```
/research "$ARGUMENTS.topic" --depth=exhaustive --output="$ARGUMENTS.output" --save="$ARGUMENTS.save"
```

Pass through any `--multi` flag if present. In multi-model mode, always use Opus.

This is a convenience alias — all logic lives in the `/research` skill.
