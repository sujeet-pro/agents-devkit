---
name: review-standards
description: "adk - [helper] [guideline] Review pipeline, source routing, and comment template standards for all review-oriented skills."
user-invocable: false
allowed-tools: [Read]
workflow-tier: helper
---

# Review Standards

All review-oriented skills follow this pipeline and use these comment standards.

---

## Review Pipeline

### 1. Intake

- Run the skill preflight first so tool dependencies and source-native MCP configuration are verified from the actual input.
- Detect the source type: GitHub PR, Bitbucket PR, local repository, local markdown, Confluence page, Google Doc, or mixed input.
- Detect whether the requested output is markdown only, source comments, source updates, or both.
- Detect whether the active skill is `review-*` or `write-*`. `review-*` skills do not mutate the source; `write-*` skills do.
- Load repo and source-specific guidelines before analysis.

### 2. Source Ingestion

- Pull the primary material first:
  - PR metadata, diff, commits, and existing comments
  - document body, attachments, images, diagrams, and comments
  - relevant source files from the local checkout
- Build a comment ledger when the source already has comments or threads:
  - still-open issues
  - handled but unresolved issues
  - resolved or outdated issues that need verification
  - critical issues that may need to be reopened
- Build a compact context packet for the review team: summary, scope, guidelines, changed files, and existing discussion.

### 3. Parallel Review

Launch a review team (invoke `/adk:agentic-teams` if available).

Every review must cover:

- correctness and behavioral risk
- architecture and boundary fit
- security and performance
- tests, docs, and migration impact
- source-specific concerns such as frontend, backend, design system, or document quality

### 4. Consolidation

- Deduplicate overlapping findings.
- Attach file paths, line numbers, or quoted text when available.
- Assign a confidence score and a concrete next step.
- Separate must-fix issues from suggestions.
- Reconcile new findings against the comment ledger before preparing postback actions.

### 5. Output

Always produce a markdown review artifact with:

- summary
- findings grouped by severity
- open questions and assumptions
- follow-up checklist

Optional source-side output:

- PR comments on GitHub or Bitbucket
- Confluence comments or page updates
- Google Docs comments or document updates

### 6. Postback Rules

- Reuse or align with existing review interaction when the source already has a live review thread.
- Avoid posting duplicate comments that already exist.
- Resolve comments that are truly handled but still left open when the source supports it.
- Reopen or restate critical comments that were marked outdated or resolved incorrectly and are still valid.
- Prefer line comments when the source supports them and the line mapping is stable.
- Fall back to a grouped summary comment when exact line mapping is not possible.

---

## Comment Template

Every non-trivial review comment **must** follow this canonical format so the PR author can immediately answer:

- What is wrong?
- When does it fail?
- What could go wrong if not fixed?
- What standard or best practice does it violate?
- What is the likely fix?

### Platform Compatibility

The comment format uses only markdown that renders cleanly on **both GitHub and Bitbucket**:

- Metadata subtext uses `*italic*` (not `<sub>` — Bitbucket strips HTML)
- No `<details>`, `<summary>`, or other HTML tags
- No emoji shortcodes — use unicode or omit
- Tables only when >2 columns

### Severity Labels

**Issue severities (3 tiers):**

- `Must Fix` — must be fixed before merge: correctness, security, data loss, or reliability risk
- `Suggestion` — improves quality materially: maintainability, performance, consistency, or moderate risk
- `Note` — minor improvement, style, or future-proofing: safe to defer

**Non-issue types:**

- `Praise` — recognizes well-crafted code: reinforces good patterns
- `Question` — confidence is lower: asking for author context

### Canonical Format

#### Must Fix — full template

````md
:rotating_light: **[Must Fix]** <Short, specific title>

*Confidence: <score>/100 | Concern: <concern(s)> | Depth: <depth> | Dimension: <dimension(s)> | Guideline: <guideline>*

#### Issue
<What is wrong, in which code path, and under what condition. 1-3 sentences.>

#### Risk
<What could go wrong if this is not fixed. Concrete consequences.>

#### Suggested fix
<Concrete recommendation. 1-2 sentences.>

```<lang>
<code snippet>
```

#### Also affects
- `<other-file>:<line>` — <brief description>
````

#### Suggestion — drop "Risk", use "Impact"

````md
:large_orange_diamond: **[Suggestion]** <Short, specific title>

*Confidence: <score>/100 | Concern: <concern(s)> | Depth: <depth> | Dimension: <dimension(s)> | Guideline: <guideline>*

#### Issue
<Issue description>

#### Impact
<Maintainability/consistency consequence>

#### Suggested fix
```<lang>
<code>
```
````

#### Note — compact, no h4 headings

```md
:speech_balloon: **[Note]** <Title>

*Confidence: <score>/100 | Concern: <concern> | Depth: <depth> | Dimension: <dimension> | Guideline: <guideline>*

<1-2 sentence inline description. Not blocking.>
```

#### Praise — no confidence score

```md
:star2: **[Praise]** <Title>

*Concern: <concern> | Depth: <depth> | Dimension: <dimension>*

<Brief explanation of what's well done.>
```

#### Question

```md
:grey_question: **[Question]** <Title>

*Confidence: <score>/100 | Concern: <concern> | Depth: <depth> | Dimension: <dimension>*

<The question, with context for why it matters.>
```

### Comment Consolidation

When multiple findings target the same file and line:

1. **Exact same line**: merge into one comment
2. **Overlapping ranges**: merge covering full range
3. **Same function/block**: consider merging with numbered sub-findings

The merged comment takes the **highest severity** among the sub-findings.

### Existing Interaction Rule

When the source already has review comments or a discussion thread:

- read it first
- do not duplicate resolved or clearly addressed feedback
- verify handled comments before resolving or skipping them
- resolve handled-but-open comments when the source supports it
- if a critical issue was marked outdated but is still present, reopen with fresh evidence
- keep new comments aligned with the source's tone and threading model
