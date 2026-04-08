---
title: "docs-md"
description: Markdown feature detection and formatting guidelines for different targets
skill_name: docs-md
category: guideline
workflow_tier: helper
user_invocable: false
---

# docs-md

Detects the markdown rendering target and loads formatting guidelines that match what the target supports.

## Purpose

Ensures markdown output uses only features supported by the rendering target (pagesmith, GitHub, or plain markdown). Prevents broken rendering.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--target` | `pagesmith`, `github`, `plain` | auto-detect | Markdown rendering target |

## Target Detection

- Detects pagesmith from config files (`pagesmith.config.*`)
- Detects GitHub from `.github/` directory, GitHub URLs
- Falls back to plain markdown

## Feature Matrices

Each target has a supported feature set covering:
- GFM tables, alerts, footnotes
- Math rendering (KaTeX/MathJax)
- Mermaid diagrams inline
- Admonitions/callouts
- HTML embed support

## Invoked By

`docs-write`, `docs-review`, `docs-crud`, `docs-repo`, `spec`.
