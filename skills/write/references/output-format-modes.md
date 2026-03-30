# Output Format Modes

All DevKit skills support three verbosity modes via `--verbosity short|standard|detailed`. This reference defines the templates, selection rules, and cross-platform constraints.

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

### Documents

For documents (not PR comments), mode applies to the entire document. Default: `standard`.

---

## PR Comment Templates

### Short Mode (Nitpick / Question)

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

<1-2 sentence description.> <Optional inline suggestion.>
```

**Example:**
```md
[Nitpick][Maintainability] Unused import `lodash/merge`

Remove the import — it's unused after the refactor in this PR.
```

### Standard Mode (Should Have / May Have)

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

**Issue**
<1-3 sentences: what is wrong, which code path, under what condition.>

**Impact**
<1-2 sentences on practical consequence.>

**Suggested fix**
<1-2 sentences + code snippet.>

```<lang>
<code>
```
```

**Example:**
```md
[Should Have][Performance] N+1 query in order list endpoint

**Issue**
The endpoint fetches orders then loads customer data in a loop — one extra query per order. Scales linearly with result size.

**Impact**
Latency grows with data volume. Not obvious in local testing but costly in production under concurrent load.

**Suggested fix**
Use eager loading or batch the related query.

```ts
const orders = await db.order.findMany({
  where: { tenantId },
  include: { customer: true },
});
```
```

### Detailed Mode (Blocker / Critical)

Use the full canonical template from `review-comment-template.md`:

```md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

**Summary**
- Confidence: <score>/100
- Agent: devkit (skill plugin tool)
- Principle violated: <principle>

**Issue**
<What is wrong, in which code path, and under what condition.>

**Where it fails**
- **Case 1:** <scenario>
  - Current behavior: <actual>
  - Expected behavior: <expected>
- **Case 2:** <scenario>
  - Current behavior: <actual>
  - Expected behavior: <expected>

**Why it matters**
<Impact in practical terms.>

**Suggested fix**
<Concrete recommendation.>

```<lang>
<code snippet>
```

**Suggested tests**
- <test>
- <test>
```

---

## Document Comment Templates

For comments on Confluence/Google Docs (not PR comments). Use priority tags only (no principle tags).

### Short

```md
[<PRIORITY>] <One sentence describing the issue and suggested fix.>
```

### Standard

```md
[<PRIORITY>] <Short title>

<2-3 sentences describing the issue with specific references to the document section.>

**Recommendation:** <1-2 sentences.>
```

### Detailed

```md
[<PRIORITY>] <Short title>

**Issue**
<Full paragraph with specific document references.>

**Impact**
<Why this matters for the reader/user.>

**Recommendation**
<Detailed suggestion with alternatives if applicable.>
```

---

## Review Report Structure

Review reports (markdown artifacts from local reviews) use a fixed wrapper with findings formatted per the selected mode.

```md
# Review Report: <target>

## Summary
<2-3 sentence overview of the review.>

## Statistics

| Metric | Value |
|---|---|
| Files reviewed | N |
| Findings | N |
| Blockers | N |
| Critical | N |

## Findings

<Findings formatted using the PR comment template for the selected mode.>

## Follow-Up Checklist

- [ ] <Action item 1>
- [ ] <Action item 2>
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
- Fenced code blocks with language hints (`` ```ts ``)
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
