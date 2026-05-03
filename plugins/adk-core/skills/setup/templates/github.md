---
# ~/.config/adk/github.md
# GitHub conventions. Used by adk-review:* and adk-docs:docs-pr-description.

default_org: acme
default_pr_reviewers:
  - "@alice"
  - "@bob"
pr_template_path: .github/pull_request_template.md
codeowners_path: .github/CODEOWNERS
status_check_required:
  - build
  - test
  - security-scan
labels:
  blocker: blocker
  needs_review: needs review
  wip: wip
merge_method: squash             # squash | merge | rebase
forbid_force_push_branches:
  - main
  - master
  - develop
  - release/*
auth:
  token_env: GITHUB_PAT
toolsets_env: GITHUB_TOOLSETS    # e.g. context,repos,issues,pull_requests,actions,users
read_only_env: GITHUB_READ_ONLY  # 1 by default; flip per-skill
---

# Notes

- The fine-grained PAT (in `$GITHUB_PAT`) needs: Contents:Read, Pull Requests:Read+Write, Issues:Read+Write, Actions:Read, Metadata:Read, read:org, read:project, notifications.
- For purely read-only investigation, drop the write scopes.
- `GITHUB_READ_ONLY=1` is the default; the github MCP is locked to read; review skills flip it to 0 only inside their post-comments stage.
