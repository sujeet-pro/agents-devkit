---
title: 'output-format'
description: 'Output format standards: verbosity modes (short/standard/detailed), PR comment templates, document templates, priority labels, and cross-platform markdown rules'
skill_name: output-format
category: guideline
workflow_tier: helper
user_invocable: false
---

# output-format

`output-format` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`output-format` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

This helper does not expose a broad user-facing parameter surface beyond the narrow controls in `SKILL.md`. In practice, task skills load it indirectly and supply the context it needs.

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


## Additional Reference

### Output Targets

DevKit skills should support these output targets whenever the source material allows it.

### Documents

- **Markdown**: default source of truth.
- **Google Docs**: publish or update through Google Drive MCP.
- **Confluence**: publish or update through the Confluence MCP.
- **PDF**: export from markdown or HTML with local free tooling when available.

### Diagrams

- **Mermaid**: `.mermaid`, `.mmd`
- **Excalidraw**: `.excalidraw`
- **draw.io**: `.drawio`, `.drawio.xml`

For each generated diagram, keep both:

- the editable source file
- at least one rendered artifact, preferably SVG

Use PNG or JPEG only when the destination does not handle SVG well.

### Review Deliverables

Every review should be able to produce:

- a markdown report
- source comments when supported
- an executive summary section for handoff or reposting

---

### Verbosity Modes

| Mode | Target | Characteristics |
|---|---|---|
| `short` | Quick feedback, Slack-like | 1-3 lines. Title + suggestion. No boilerplate. Senior dev tone. |
| `standard` | PR comments, review docs | Full structured format. All sections present, no unnecessary verbosity. Default. |
| `detailed` | Documentation, audits, onboarding | Every section expanded. Rationale included. Teaching tone with examples. |

**Target audience:** SD2/SD3 (mid-level engineers). Assume language and framework knowledge. Do not explain basic concepts.

---

### Mode Selection

### Explicit selection

The user can specify `--verbosity short|standard|detailed`. Default is `standard`.

### Auto-selection for PR comments (severity-based)

When `--verbosity auto` or unspecified for PR review, select mode per finding:

| Severity | Auto Mode |
|---|---|
| Blocker | detailed |
| Critical | detailed |
| Should Have | standard |
| May Have | standard |
| Nitpick | short |
| Question | short |

### Severity override floors

Even when the user explicitly requests a mode, severity can override downward:

| Severity | Minimum Mode |
|---|---|
| Blocker | standard |
| Critical | standard |
| Should Have | short |
| May Have | short |
| Nitpick | short |
| Question | short |

A Blocker finding will never render as `short`, even if `--verbosity short` is passed.

---

### PR Comment Templates

### Short Mode (Nitpick / Question)

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

<1-2 sentence description with file:line reference.> <Optional inline suggestion.>
```

### Standard Mode (Should Have / May Have)

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

**Summary**
- Location: `<file>:<line>`
- Confidence: <score>/100
- Guideline: <which standard or best practice is violated>

**Issue**
<1-3 sentences: what is wrong, which code path, under what condition.>

**Why it matters**
<1-2 sentences on practical consequence.>

**Suggested fix**
<1-2 sentences + code snippet.>
```

### Detailed Mode (Blocker / Critical)

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

**Summary**
- Location: `<file>:<line-range>`
- Confidence: <score>/100
- Guideline: <which standard or best practice is violated>

**Issue**
<What is wrong, in which code path, and under what condition.>

**Where it fails**
- **Case 1:** <scenario>
  - Current behavior: <actual>
  - Expected behavior: <expected>

**Why it matters**
<Impact in practical terms.>

**Suggested fix**
<Concrete recommendation.>

**Suggested tests**
- <test>
- <test>
```

---

### Document Verbosity

For technical documents (ADRs, RFCs, system designs, etc.):

| Aspect | Short | Standard | Detailed |
|---|---|---|---|
| Structure | Key sections only | Full structure per guidelines | Full structure + appendix |
| Executive summary | This IS the output | 3-5 sentences | Full paragraph |
| Sections | Bullet points | Structured paragraphs | Expanded with rationale |
| Examples | Omit | 1-2 per section | 3+ with edge cases |
| Alternatives | Top pick only | All, briefly | All, with comparison table |
| Appendix | No | No | Yes |

---

### Cross-Platform Markdown Rules

### Safe for PR comments (GitHub + Bitbucket intersection)

Use freely:
- Bold (`**text**`), italic (`*text*`), inline code (`` `code` ``)
- Fenced code blocks with language hints
- Unordered and ordered lists
- Blockquotes (`>`)
- Links (`[text](url)`)
- GFM tables (`| col | col |`)
- Blank-line paragraph breaks

### Avoid in PR comments

These are not reliably supported on both platforms:
- `<details>` / `<summary>` (Bitbucket strips HTML)
- Nested blockquotes
- Task lists (`- [ ]`)
- Footnotes
- Emoji shortcodes (`:emoji:`)
- HTML tags in general

### Local markdown (review reports, documents)

All GFM features are safe since these are not posted as platform comments.

---

### Priority Labels

Use exactly one:

| Priority | When to use |
|---|---|
| `Blocker` | Must be fixed before merge — correctness, security, or data loss risk |
| `Critical` | Should be fixed before merge — significant reliability or performance concern |
| `Should Have` | Improves quality materially — maintainability, consistency, or moderate risk |
| `May Have` | Nice to have — minor improvement, style, or future-proofing |
| `Nitpick` | Cosmetic or stylistic preference — safe to ignore |
| `Question` | Confidence is lower — asking for author context |

### Principle Labels

Use one or more:

`Correctness` · `Reliability` · `Security` · `Performance` · `Maintainability` · `Consistency` · `Testability` · `Observability` · `Accessibility` · `Documentation`

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
