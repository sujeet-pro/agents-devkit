---
title: 'monitor-ci-status'
description: 'Watches CI status on the current PR.'
artifact_kind: monitor
---

# monitor-ci-status

Watches CI status on the current PR. cicd-monitor and cicd-fix subscribe to this stream.

## Trigger

`on-skill-invoke:cicd-monitor`

## Command

```bash
while true; do (gh pr checks --watch --fail-fast --interval 30 2>&1 | head -1) 2>/dev/null || true; sleep 60; done
```

## Source

`monitors/monitors.json` (entry: `ci-status`).
