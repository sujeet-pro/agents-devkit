---
name: research-quick
description: Quick multi-agent software research using the shared research pipeline with shorter scope and faster output
user_invocable: true
arguments:
  - name: topic
    description: "Topic to search"
    required: true
  - name: output
    description: "Output format: notes, outline, markdown (default: notes)"
    required: false
  - name: save
    description: "Optional file path to save output"
    required: false
---

# Search

Run `/devkit:research` with `depth=quick`. Even in quick mode, use at least 2 child agents in parallel: one for official docs and one for practical examples.
