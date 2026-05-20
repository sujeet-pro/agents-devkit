---
description: Batch driver over /adk-pr-review — reads a CSV of PR URLs and runs N reviews concurrently. Skips merged + skips-stable.
argument-hint: "[<queue-path>] [--scan] [-p N | --parallelism N] [--dry-run] [--max-rows M] [--since <days>] [--slack-config <path>]"
---

Invoke the adk-pr-reviews skill at {{ADK_REPO}}/skills/adk-pr-reviews/SKILL.md.

@{{ADK_REPO}}/AGENTS.md
@{{ADK_REPO}}/skills/adk-pr-reviews/SKILL.md

Apply the input: $ARGUMENTS
