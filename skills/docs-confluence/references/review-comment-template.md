# Code Review Comment Template

Every non-trivial review comment **must** follow this canonical format. The goal is that the PR author can immediately answer all of these just by reading the comment:

- What is wrong?
- When does it fail?
- What could go wrong if not fixed?
- What standard or best practice does it violate?
- What is the likely fix?

---

## Platform Compatibility

The comment format uses only markdown that renders cleanly on **both GitHub and Bitbucket**:

- Metadata subtext uses `*italic*` (not `<sub>` — Bitbucket strips HTML)
- No `<details>`, `<summary>`, or other HTML tags
- No emoji shortcodes — use unicode or omit
- Tables only when >2 columns
- All other formatting (bold, code blocks, lists, h4 headings) is safe on both platforms

---

## Severity Labels

Use exactly one severity label per comment:

**Issue severities (3 tiers):**

- `Must Fix` — must be fixed before merge: correctness, security, data loss, or reliability risk
- `Suggestion` — improves quality materially: maintainability, performance, consistency, or moderate risk
- `Note` — minor improvement, style, or future-proofing: safe to defer

**Non-issue types (not severity):**

- `Praise` — recognizes well-crafted code: reinforces good patterns
- `Question` — confidence is lower: asking for author context without overstating the issue

### Severity Icons

- `Must Fix` — :rotating_light:
- `Suggestion` — :large_orange_diamond:
- `Note` — :speech_balloon:
- `Praise` — :star2:
- `Question` — :grey_question:

---

## Dual Tags: Concern + Depth

Every comment carries **two classification tags** that describe what dimension was reviewed and how deep the analysis went.

### Concern Domain (what area)

- `Correctness` — logic bugs, edge cases, null handling, race conditions, data integrity
- `Design` — abstraction quality, coupling, dependency direction, API surface, data flow
- `Reliability` — error handling, retries, timeouts, observability, logging, graceful degradation
- `Performance` — algorithmic complexity, memory, N+1 queries, bundle size, caching
- `DevEx` — naming, readability, test quality, doc accuracy, migration notes, reviewer ergonomics

### Review Depth (how deep)

- `Surface` — syntax, linting gaps, obvious bugs, copy-paste errors, leftover debug code
- `Logic` — control flow, edge cases, error handling, boundary conditions, null paths
- `Integration` — API contracts, cross-module impact, dependency changes, migration safety
- `Architecture` — design decisions, abstraction quality, coupling, scalability implications
- `Hardening` — security, performance under load, observability, failure recovery, test gaps

---

## Review Dimensions (Sub-Agent Attribution)

Each comment is attributed to the review dimension (sub-agent) that identified it. When multiple dimensions flag the same issue, list all that apply.

| Dimension | Covers |
|-----------|--------|
| `syntax` | Linting, formatting, naming, import organization, dead code |
| `correctness` | Bugs, edge cases, null handling, boundary conditions, race conditions |
| `security` | OWASP Top 10, auth/authz, input validation, secret exposure, injection |
| `performance` | N+1 queries, memory leaks, bundle size, unnecessary computation, caching |
| `design` | Coupling, dependency direction, data flow, API surface, change isolation |
| `reliability` | Error handling, retries, timeouts, observability, logging, degradation |
| `testing` | Coverage gaps, test quality, missing edge case tests, flaky patterns |
| `documentation` | Doc drift, missing migration notes, API doc accuracy, changelog |
| `ui-ux` | Semantic HTML, ARIA, keyboard nav, responsive, visual consistency (frontend only) |
| `spec-compliance` | Does code implement what was asked? (when context docs are provided) |

---

## Guideline References

The **Guideline** field connects the finding to the specific standard being violated. This helps developers understand *why* this is considered an issue beyond the reviewer's opinion.

Use one of:

- **DevKit coding guideline**: `coding-guidelines/security: input validation`
- **DevKit doc guideline**: `doc-guidelines/api-reference: parameter descriptions`
- **Language/framework idiom**: `TypeScript: strict null checks`
- **Industry standard**: `OWASP A03: Injection`
- **Project convention**: `project convention: error handling pattern in src/errors/`
- **Official documentation**: `React docs: Rules of Hooks`

When no specific guideline applies, use a concise description of the violated principle: `defensive programming`, `fail-fast validation`, `single source of truth`.

When multiple guidelines from different dimensions are violated, list each as a bullet point. When only one guideline applies, include it inline in the metadata subtext.

---

## Canonical Format

### Line 1: Title (comment header)

```
<icon> **[<SEVERITY>]** <Short, specific title that describes the actual problem>
```

This is the scannable header. It must be specific enough to understand the issue without reading further.

**Good titles:**
- `Potential null dereference when accessing user.profile.id`
- `N+1 query pattern in order list endpoint`
- `Missing authorization check for admin-only action`

**Bad titles:**
- `Bug in profile code`
- `Performance issue`
- `Needs refactor`

### Line 2: Metadata subtext

A single italic line with pipe separators. No bold labels, no bullet points — just clean, scannable metadata that stays visually subordinate to the title.

**Format (works on both GitHub and Bitbucket):**
```
*Confidence: <score>/100 | Concern: <concern(s)> | Depth: <depth> | Dimension: <dimension(s)> | Guideline: <guideline>*
```

**Field rules:**
- **Confidence**: 0-100 with `/100` suffix. Be honest: 60-70 means "I think this is an issue but could be wrong"; 90+ means "this is clearly wrong"
- **Concern**: one or more from the Concern Domain list, comma-separated
- **Depth**: one from the Review Depth list
- **Dimension**: which review sub-agent(s) identified it, comma-separated
- **Guideline**: the specific standard violated

**When multiple guidelines are violated** (from different dimensions), use a second italic line for the additional guidelines:

```md
:rotating_light: **[Must Fix]** Race condition in session refresh during token expiry

*Confidence: 92/100 | Concern: Correctness, Reliability | Depth: Logic | Dimension: correctness, reliability*
*Guideline: coding-guidelines/backend-general: concurrent-state-mutation | coding-guidelines/security: session-management*
```

### Section headings (h4)

After the title and metadata, use `####` headings for each section. Leave a blank line between the metadata and the first heading.

---

## Full Template (Must Fix)

````md
:rotating_light: **[Must Fix]** <Short, specific title>

*Confidence: <score>/100 | Concern: <concern(s)> | Depth: <depth> | Dimension: <dimension(s)> | Guideline: <guideline>*

#### Issue
<What is wrong, in which code path, and under what condition. 1-3 sentences.>

#### Risk
<What could go wrong if this is not fixed. Concrete consequences, not vague warnings. Include specific failure scenarios.>

#### Suggested fix
<Concrete recommendation. 1-2 sentences describing the approach.>

```<lang>
<code snippet>
```

#### Also affects
- `<other-file>:<line>` — <brief description of how it's affected>
- `<other-file>:<line>` — <brief description>
````

**Section rules:**
- **Issue**: 1-3 sentences. Call out the condition or trigger. Reference the specific code path
- **Risk** (for Must Fix): What happens if not fixed. Real consequences: data corruption, security breach, user-facing error, silent failure. Not "this could be a problem" — state the actual consequence
- **Impact** (for Suggestion/Note): Same section, but titled "Impact" instead of "Risk". Lighter consequences: maintainability burden, inconsistency, tech debt
- **Suggested fix**: 1-2 sentences + minimal code snippet. Don't over-prescribe — the author owns the implementation
- **Also affects**: Only when the issue ripples to other locations. Since these are inline comments, the primary location is the comment itself. Omit this section entirely when the issue is localized

---

## Adaptation by Severity

### Must Fix — full template

Use all sections. These comments justify the detail.

````md
:rotating_light: **[Must Fix]** Race condition in session refresh during token expiry

*Confidence: 92/100 | Concern: Correctness, Reliability | Depth: Logic | Dimension: correctness, reliability | Guideline: concurrent-state-mutation*

#### Issue
The `refreshSession()` call on line 45 reads and writes `this.token` without a lock. When two requests trigger refresh simultaneously, the second overwrites the first's token mid-flight, leaving one request with a stale session.

#### Risk
- Silent auth failures under concurrent load — hard to reproduce locally
- Users get logged out intermittently in production
- If the stale token hits a write endpoint, partial data corruption

#### Suggested fix
Wrap the refresh in a mutex or deduplicate concurrent calls:

```ts
private refreshPromise: Promise<Token> | null = null;

async refreshSession() {
  if (!this.refreshPromise) {
    this.refreshPromise = this._doRefresh().finally(() => {
      this.refreshPromise = null;
    });
  }
  return this.refreshPromise;
}
```

#### Also affects
- `api/client.ts:112` — same pattern, same race
- `ws/reconnect.ts:67` — calls `refreshSession` without awaiting
````

### Suggestion — drop "Risk", use "Impact", keep rest

````md
:large_orange_diamond: **[Suggestion]** Extract retry config to a shared constant

*Confidence: 78/100 | Concern: DevEx | Depth: Surface | Dimension: design | Guideline: single-source-of-truth*

#### Issue
Retry count (3) and backoff (1000ms) are hardcoded in four places. Changing one without the others causes inconsistent behavior.

#### Impact
Config drift across retry sites. A future change to retry policy requires finding and updating all four locations.

#### Suggested fix
```ts
// config/retry.ts
export const RETRY_CONFIG = { maxRetries: 3, backoffMs: 1000 };
```
````

### Note — title + subtext + 1-2 sentence inline, no h4 headings

```md
:speech_balloon: **[Note]** Consider `structuredClone` instead of `JSON.parse(JSON.stringify(...))`

*Confidence: 70/100 | Concern: Performance | Depth: Surface | Dimension: performance | Guideline: modern-apis*

`structuredClone` handles circular refs and is ~2x faster for large objects. Not blocking.
```

### Praise — title + subtext (no confidence) + brief explanation

```md
:star2: **[Praise]** Clean separation of transport from protocol logic

*Concern: Design | Depth: Architecture | Dimension: design*

The new `Transport` interface makes it trivial to swap WebSocket for SSE later without touching message handling. Well done.
```

### Question — title + subtext + the question

```md
:grey_question: **[Question]** Is the 30s timeout intentional for health checks?

*Confidence: 55/100 | Concern: Reliability | Depth: Integration | Dimension: reliability*

Most health check endpoints return in <100ms. A 30s timeout means a hung dependency won't trigger alerts for 30 seconds. Was this chosen to match a specific SLA, or is it a default that should be lower?
```

---

## Comment Consolidation (Same-Line Merging)

When multiple findings target the same file and line (or overlapping line ranges), **merge them into a single comment**. This avoids cluttering the PR with redundant threads.

### Merge Rules

1. **Exact same line**: two or more findings on the same `file:line` -> combine into one comment
2. **Overlapping ranges**: ranges that overlap (e.g., lines 42-45 and 43-48) -> merge covering full range
3. **Same function/block**: different lines within the same function, thematically related -> consider merging with numbered sub-findings

### Merged Comment Format

````md
:rotating_light: **[Must Fix]** <Merged title summarizing the area>

*Findings: <N> issues | Concern: <all concerns> | Depth: <deepest depth>*

---

**1. <First finding title>**

*Confidence: <score>/100 | Dimension: <dimension> | Guideline: <guideline>*

<Issue description>

**Suggested fix:**
```<lang>
<code>
```

---

**2. <Second finding title>**

*Confidence: <score>/100 | Dimension: <dimension> | Guideline: <guideline>*

<Issue description>

**Suggested fix:**
```<lang>
<code>
```
````

The merged comment takes the **highest severity** among the sub-findings.

### Reply Merging

When posting multiple replies to the same thread in one session:
1. Combine all replies into a single response
2. Use `---` between distinct points
3. Lead with acknowledgment, then any follow-up concern

---

## Writing Quality Rules

### Issue Section
- 1-3 sentences describing the exact problem in the current code path
- Call out the condition or trigger that makes the issue happen
- Be specific: name the function, variable, or data state

### Risk / Impact Section
- State actual consequences, not vague warnings
- "Users see a 500 error" not "this might break"
- Include the scenario that triggers the consequence
- For Must Fix: use "Risk" heading. For Suggestion/Note: use "Impact" heading

### Suggested Fix
- 1-2 sentences describing the approach and why it addresses the root cause
- Include a minimal code snippet in the appropriate language
- Don't over-prescribe — the author owns the implementation

### Also Affects
- Only include when the issue genuinely ripples to other files
- Each entry: `file:line` + brief description of how it's affected
- Omit entirely for localized issues (most comments)
