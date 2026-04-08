---
title: "output-format"
description: "Output format standards with verbosity modes, comment templates, and cross-platform markdown rules"
skill_name: output-format
category: guideline
workflow_tier: helper
user_invocable: false
---

# output-format

Output format standards for all DevKit skills. Defines three verbosity modes (`short`/`standard`/`detailed`), PR comment templates per severity, document verbosity rules, cross-platform markdown constraints, and priority/principle labels.

## Purpose

- Standardize output structure across all skills that produce deliverables
- Provide severity-adaptive verbosity so critical findings get detail and nitpicks stay compact
- Define PR comment templates that render cleanly on both GitHub and Bitbucket
- Establish priority and principle labels used consistently across all review output

## Key Behaviors

### Verbosity Modes

| Mode | Target | Characteristics |
|------|--------|-----------------|
| `short` | Quick feedback, Slack-like | 1-3 lines. Title + suggestion. No boilerplate. Senior dev tone. |
| `standard` | PR comments, review docs | Full structured format. All sections present, no unnecessary verbosity. Default. |
| `detailed` | Documentation, audits, onboarding | Every section expanded. Rationale included. Teaching tone with examples. |

Target audience: SD2/SD3 (mid-level engineers). Assume language and framework knowledge.

### Mode Selection

- **Explicit**: user specifies `--verbosity short|standard|detailed`. Default is `standard`.
- **Auto-selection for PR comments** (severity-based): Blocker/Critical → `detailed`; Should Have/May Have → `standard`; Nitpick/Question → `short`.
- **Severity override floors**: Blocker and Critical findings never render as `short`, even when `--verbosity short` is explicitly passed.

### PR Comment Templates

Three template tiers aligned to verbosity:

| Template | Used For | Sections |
|----------|----------|----------|
| **Short** | Nitpick, Question | Priority+principle tag, title, 1-2 sentence description |
| **Standard** | Should Have, May Have | Summary (location, confidence, guideline), Issue, Why it matters, Suggested fix |
| **Detailed** | Blocker, Critical | Summary, Issue, Where it fails (with cases), Why it matters, Suggested fix, Suggested tests |

### Document Verbosity

| Aspect | Short | Standard | Detailed |
|--------|-------|----------|----------|
| Structure | Key sections only | Full structure per guidelines | Full structure + appendix |
| Executive summary | This IS the output | 3-5 sentences | Full paragraph |
| Sections | Bullet points | Structured paragraphs | Expanded with rationale |
| Examples | Omit | 1-2 per section | 3+ with edge cases |
| Alternatives | Top pick only | All, briefly | All, with comparison table |
| Appendix | No | No | Yes |

### Cross-Platform Markdown Rules

**Safe for PR comments** (GitHub + Bitbucket intersection): bold, italic, inline code, fenced code blocks, lists, blockquotes, links, GFM tables, blank-line paragraph breaks.

**Avoid in PR comments**: `<details>`/`<summary>` (Bitbucket strips HTML), nested blockquotes, task lists, footnotes, emoji shortcodes, HTML tags.

**Local markdown** (review reports, documents): all GFM features are safe.

### Output Targets

| Target | Format |
|--------|--------|
| Documents | Markdown (default), Google Docs, Confluence, PDF |
| Diagrams | Mermaid, Excalidraw, draw.io (source + rendered) |
| Review deliverables | Markdown report, source comments, executive summary |

## What It Provides

### Priority Labels

| Priority | When to Use |
|----------|-------------|
| `Blocker` | Must fix before merge — correctness, security, or data loss risk |
| `Critical` | Should fix before merge — significant reliability or performance concern |
| `Should Have` | Improves quality materially — maintainability, consistency, or moderate risk |
| `May Have` | Nice to have — minor improvement, style, or future-proofing |
| `Nitpick` | Cosmetic or stylistic preference — safe to ignore |
| `Question` | Confidence is lower — asking for author context |

### Principle Labels

`Correctness` · `Reliability` · `Security` · `Performance` · `Maintainability` · `Consistency` · `Testability` · `Observability` · `Accessibility` · `Documentation`

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `code-review-pr` | when producing output |
| `code-review-repo` | when producing output |
| `code-review-fix` | when producing output |
| `audit` | when producing output |
| `docs-write` | when producing output |
| `docs-review` | when producing output |
| `docs-repo` | when producing output |
| `docs-crud` | when producing output |
| `docs-confluence` | when producing output |
| `design` | when producing output |
| `dev-build` | when producing output |
| `dev-refactor` | when producing output |
| `dev-migrate` | when producing output |
| `plan` | when producing output |
| `spec` | when producing output |
| `research` | when producing output |
| `handoff` | when producing output |
