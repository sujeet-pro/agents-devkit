---
description: Generate a professional markdown artifact (runbook / ADR / RCA / PR body / commit msg / changelog / diagram / readme / migration / api ref / experiment report). Does NOT publish — use /adk-sync.
argument-hint: <intent-or-source> --type <artifact-type> [--audience engineer|pm|exec|mixed] [--detailed] [--deep]
---

Invoke the adk-document skill at {{ADK_REPO}}/skills/adk-document/SKILL.md.

@{{ADK_REPO}}/AGENTS.md
@{{ADK_REPO}}/skills/adk-document/SKILL.md

Apply the input: $ARGUMENTS
