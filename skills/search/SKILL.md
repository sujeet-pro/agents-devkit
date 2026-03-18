---
name: search
description: "Quick lightweight research — alias for /research --depth=light. Uses Sonnet for speed (Opus in multi-model mode)."
user_invocable: true
model: sonnet
arguments:
  - name: topic
    description: "Topic to search"
    required: true
  - name: output
    description: "Output format: markdown, outline, notes (default: notes)"
    required: false
  - name: save
    description: "File path to save output (optional)"
    required: false
---

# Search (Quick Research)

Lightweight, fast research using a single agent. Alias for `/research --depth=light`.

**Model**: Sonnet for speed. If `--multi` flag is present, all models use Opus for consistency.

## Delegation

Invoke the `/research` skill with `depth=quick` and forward all other arguments.
Default output format is `notes` (not `markdown`) for brevity:

```
/research "$ARGUMENTS.topic" --depth=quick --output="${ARGUMENTS.output:-notes}" --save="$ARGUMENTS.save"
```

### Multi-model override

If the user invokes `/search topic --multi`, the multi-model skill takes over and ALL models (including the primary) run at Opus level. The Sonnet default only applies to single-model execution.

This is a convenience alias — all logic lives in the `/research` skill.
