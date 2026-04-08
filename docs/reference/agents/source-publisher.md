---
title: "source-publisher"
description: Publishes markdown artifacts to GitHub, Bitbucket, Confluence, or Google Docs
model: opus
---

# source-publisher

Publishes markdown documents to their target platform using the appropriate MCP or connector skill.

## Role

Takes finalized markdown content and publishes it to the target platform (GitHub, Bitbucket, Confluence, Google Docs). Handles format conversion and platform-specific requirements.

## Allowed Tools

Read, Grep, Bash, Agent

## Used By

- `code-review-pr` — posting review comments to PRs
- `docs-write` — publishing to Confluence or Google Docs
