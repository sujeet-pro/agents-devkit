---
name: adk-output-format
description: "adk - [helper] [guideline] Output format standards: verbosity modes (short/standard/detailed), PR comment templates, document templates, priority labels, and cross-platform markdown rules."
user-invocable: false
allowed-tools: [Read]
workflow-tier: helper
---

# Output Format Standards

All DevKit skills support three verbosity modes via `--verbosity short|standard|detailed`. This skill defines the templates, selection rules, cross-platform constraints, and output targets.

---

## Output Targets

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

## Verbosity Modes

| Mode | Target | Characteristics |
|---|---|---|
| `short` | Quick feedback, Slack-like | 1-3 lines. Title + suggestion. No boilerplate. Senior dev tone. |
| `standard` | PR comments, review docs | Full structured format. All sections present, no unnecessary verbosity. Default. |
| `detailed` | Documentation, audits, onboarding | Every section expanded. Rationale included. Teaching tone with examples. |

**Target audience:** SD2/SD3 (mid-level engineers). Assume language and framework knowledge. Do not explain basic concepts.

---

## Mode Selection

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

## PR Comment Templates

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

## Document Verbosity

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

## Cross-Platform Markdown Rules

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

## Priority Labels

Use exactly one:

| Priority | When to use |
|---|---|
| `Blocker` | Must be fixed before merge — correctness, security, or data loss risk |
| `Critical` | Should be fixed before merge — significant reliability or performance concern |
| `Should Have` | Improves quality materially — maintainability, consistency, or moderate risk |
| `May Have` | Nice to have — minor improvement, style, or future-proofing |
| `Nitpick` | Cosmetic or stylistic preference — safe to ignore |
| `Question` | Confidence is lower — asking for author context |

## Principle Labels

Use one or more:

`Correctness` · `Reliability` · `Security` · `Performance` · `Maintainability` · `Consistency` · `Testability` · `Observability` · `Accessibility` · `Documentation`
