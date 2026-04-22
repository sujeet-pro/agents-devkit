# `mode-contract` — example invocations

## Review-only
```
/adk:review-pr https://github.com/org/repo/pull/123 --mode review
```
Posts no comments. Writes findings to `.temp/task-<slug>/validation/d1.md`.

## Fix-mode (auto-apply own findings)
```
/adk:audit-repo --mode fix --auto
```
Audits the repo and applies all auto-fixable findings. Re-runs `--mode review` at the end to confirm zero residual findings.

## Auto loop (default)
```
/adk:build-feature "Add user-data export"
```
Brainstorm + plan + execute end-to-end. Same as `--mode auto`. Approval gates active.

## Auto loop, unattended
```
/adk:build-feature "Add user-data export" --auto
```
Skip approval gates. Pick documented (default) at each fork.
