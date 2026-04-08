---
title: "output-format"
description: Verbosity modes, PR comment templates, priority labels, and cross-platform markdown
skill_name: output-format
category: guideline
workflow_tier: helper
user_invocable: false
---

# output-format

Standards for output shape: verbosity modes, deliverable templates, severity labels, and cross-platform markdown compatibility.

## Purpose

Defines how skills format their output depending on verbosity, destination (markdown, PR comment, Confluence), and severity.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

## Verbosity Modes

| Mode | Behavior |
|------|----------|
| `short` | Key findings and sources only; one-liner summaries |
| `standard` | Structured output with sections; default for most tasks |
| `detailed` | Full analysis with code snippets, confidence ratings, risks |

## Priority Labels

| Label | Meaning |
|-------|---------|
| Blocker | Must fix before merge/release |
| Critical | Should fix; high-impact issue |
| Should Have | Important improvement |
| May Have | Nice-to-have optimization |
| Nitpick | Style or preference |
| Question | Clarification needed |

## Invoked By

Loaded by the workflow helper set "when producing output". Used by review, docs, and audit skills for formatting deliverables.
