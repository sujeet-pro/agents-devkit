---
title: "communication"
description: Communication style rules for all DevKit output
skill_name: communication
category: guideline
workflow_tier: helper
user_invocable: false
---

# communication

Style rules for all DevKit output. Ensures consistent, concise, actionable communication across all skills.

## Purpose

Defines the communication contract: lead with conclusions, use concrete specifics, avoid preamble, and match verbosity to context.

## Rules

- **Lead with the conclusion** — state the answer, then reasoning
- **Bullet points** over prose for lists and options
- **No preamble** — skip "Great question!", "I'd be happy to help"
- **No trailing summaries** — don't restate what was just done
- **Concrete specifics** — file paths, line numbers, command snippets over abstractions
- **Short version first** — offer to elaborate after showing compact results
- **Verbosity follows context** — `--verbosity detailed` unlocks full output

## Parameters

No direct parameters. Inherits `--verbosity` from the invoking skill.

## Invoked By

Loaded automatically as part of the workflow helper set ("Always" tier). Affects all full-tier task skills.
