---
name: research-deep
description: Exhaustive software engineering research using the shared multi-agent research pipeline
user_invocable: true
arguments:
  - name: topic
    description: "Topic to research"
    required: true
  - name: output
    description: "Output format: markdown, outline, notes, google-doc, confluence (default: markdown)"
    required: false
  - name: save
    description: "Optional file path to save output"
    required: false
---

# Deep Research

Run `/devkit:research` with `depth=exhaustive`. Use at least 5 child-agent passes: landscape, primary sources, implementation examples, risk analysis, and consensus synthesis.
