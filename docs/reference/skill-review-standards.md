---
title: "review-standards"
description: "Review pipeline, source routing, and comment template standards for all review-oriented skills"
skill_name: review-standards
category: guideline
workflow_tier: helper
user_invocable: false
---

# review-standards

Review pipeline, source routing, and canonical comment template standards used by all review-oriented DevKit skills. Defines the 6-step review pipeline, comment format that answers five questions, severity labels, platform-compatible templates, comment consolidation rules, and existing interaction handling.

## Purpose

- Standardize the review pipeline so all review skills follow the same intake-to-output flow
- Define canonical comment templates that render cleanly on both GitHub and Bitbucket
- Ensure every review comment answers: what is wrong, when does it fail, what could go wrong, what standard is violated, and what is the fix
- Establish comment consolidation and existing interaction rules for clean PR discussions

## Key Behaviors

### 6-Step Review Pipeline

| Step | Name | Purpose |
|------|------|---------|
| 1 | Intake | Run preflight, detect source type, detect output target, load guidelines |
| 2 | Source Ingestion | Pull primary material (diff, metadata, comments), build comment ledger, build context packet |
| 3 | Parallel Review | Launch review team covering correctness, architecture, security, performance, tests, docs, and domain-specific concerns |
| 4 | Consolidation | Deduplicate findings, attach locations, assign confidence scores, separate must-fix from suggestions, reconcile against comment ledger |
| 5 | Output | Produce markdown review artifact with summary, severity-grouped findings, open questions, and follow-up checklist |
| 6 | Postback | Post comments to source platform, resolve handled comments, reopen incorrectly resolved critical issues |

### Comment Ledger (Step 2)

When the source already has comments or threads, build a ledger categorizing:

- Still-open issues
- Handled but unresolved issues
- Resolved or outdated issues that need verification
- Critical issues that may need to be reopened

### Severity Labels

**Issue severities (3 tiers):**

| Label | When to Use |
|-------|-------------|
| `Must Fix` | Must fix before merge — correctness, security, data loss, or reliability risk |
| `Suggestion` | Improves quality materially — maintainability, performance, consistency, or moderate risk |
| `Note` | Minor improvement, style, or future-proofing — safe to defer |

**Non-issue types:**

| Label | When to Use |
|-------|-------------|
| `Praise` | Recognizes well-crafted code — reinforces good patterns |
| `Question` | Confidence is lower — asking for author context |

### Canonical Comment Format

Every non-trivial comment includes metadata subtext with confidence score, concern domain, review depth, dimension, and guideline reference. Templates scale by severity:

| Severity | Template Sections |
|----------|-------------------|
| **Must Fix** | Issue, Risk, Suggested fix (with code), Also affects |
| **Suggestion** | Issue, Impact, Suggested fix (with code) |
| **Note** | 1-2 sentence inline description |
| **Praise** | Brief explanation of what's well done (no confidence score) |
| **Question** | The question with context for why it matters |

### Platform Compatibility

- Metadata uses `*italic*` (not `<sub>` — Bitbucket strips HTML)
- No `<details>`, `<summary>`, or other HTML tags
- No emoji shortcodes — use unicode or omit
- Tables only when >2 columns

### Comment Consolidation

| Condition | Action |
|-----------|--------|
| Exact same line | Merge into one comment |
| Overlapping ranges | Merge covering full range |
| Same function/block | Consider merging with numbered sub-findings |

Merged comments take the highest severity among sub-findings.

### Existing Interaction Rules

When the source already has review comments:

- Read existing comments first
- Do not duplicate resolved or clearly addressed feedback
- Verify handled comments before resolving or skipping
- Resolve handled-but-open comments when the source supports it
- Reopen critical issues marked outdated but still present, with fresh evidence
- Align new comments with the source's tone and threading model

### Postback Rules

- Reuse or align with existing review threads
- Avoid posting duplicate comments
- Prefer line comments when line mapping is stable
- Fall back to grouped summary comment when exact line mapping is not possible

## What It Provides

- Complete review pipeline from intake to postback
- Comment ledger protocol for tracking existing discussion state
- Canonical comment templates for 5 severity/type levels
- Platform-safe markdown formatting rules
- Consolidation logic for deduplicating multi-agent findings
- Existing interaction handling to avoid duplicate or contradictory comments

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | always |
| `code-review-repo` | always |
| `code-review-fix` | always |
| `docs-review` | always |
| `audit` | always |
