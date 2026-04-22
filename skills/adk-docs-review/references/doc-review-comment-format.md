# Doc Review Comment Format

Canonical shape for every finding this skill produces, whether it is rendered in the local Markdown report (`--mode local`) or posted as inline / footer comment on Confluence (`--mode confluence`). The same template works for both.

In `--mode confluence`, keep posted Markdown Confluence-safe:

- no HTML-heavy formatting
- no nested admonitions or panels (Confluence renderer is fragile)
- short headers (`**Bold**` for section labels, NOT `###`)
- concise paragraphs
- bold labels for the comment title and every section heading
- fenced code blocks render fine; tables render fine

## Stable IDs

Each finding gets a stable ID `F1`, `F2`, `F3`, ... assigned in the order they appear in the report. The ID is for the user-facing accept/reject loop (`a-1,3`, `r-2`, `e-4`); it is NOT included in the posted comment text on Confluence.

## Reviewer-facing finding card (shown to the user before approval)

The card wraps the exact draft that would be posted plus reviewer-facing context.

````text
### F<id> [<Severity>][<Type>][<focus-area>] <Short, specific title>

Doc location: `<doc-path>:LINE-LINE` (or section heading + anchor)
Source-of-truth: `<source-path>:LINE-LINE` (or URL with retrieval date)
Action: <add inline comment | reply to existing thread | local-only note>
Mode-specific:
  - local: write to .temp/reports/...
  - confluence: post as inline comment anchored to the quoted text

Why post this comment:
- <reason 1, reviewer-facing>
- <reason 2>

Exact comment to post:
```md
<the exact Markdown that would be rendered — see template below>
```

Reviewer explanation:
<1-3 short sentences with the extra context that helps the user decide whether to accept the comment. NOT part of the posted draft.>
````

## Canonical posted-comment template

Use this same structure for `Issue`, `Suggestion`, `Nitpick`, `Question`, and `Praise`. Severity is implied by Type + position in the summary, NOT repeated as a separate label inside the comment.

```md
**[<Type>][<primary-focus-area>] <Short, specific title>**

**Confidence:** <0-100>/100 | **Dimension:** <dimension> | **Source-of-truth:** <source-anchor>

**Issue Explanation:**
<Concise explanation of what the doc says, what the source actually does, and why they disagree (or why the doc is unclear / outdated / structurally wrong). Use a few lines when more context is needed.>

**Suggested Fix:**
<Concrete recommended doc edit. Add a fenced code block with the proposed replacement Markdown when that helps. Reference the source anchor that justifies the change.>

**Impact:**
<Concrete consequence — reader will run a broken command, will configure the wrong env var, will assume a behavior that does not exist, etc.>
```

### Field guidance

- `Type`: `Blocker` | `Critical` | `Issue` | `Suggestion` | `Nitpick` | `Question` | `Praise`. (`Blocker` and `Critical` ARE Issues with elevated severity.)
- `primary-focus-area`: short slug — `accuracy`, `freshness`, `structure`, `completeness`, `readability`, `links`, `examples`, `commands`, `screenshots`.
- `Confidence`: 0-100 integer. Below 60: prefer `Question` type. Below 40: do not post — clarify locally first.
- `Dimension`: same vocabulary as `primary-focus-area`. Use this when the focus area in the title is broader than the specific dimension being checked.
- `Source-of-truth`: file path + line range, OR URL + retrieval date, OR an explicit "no source — convention only" note.

### Worked example

```md
**[Blocker][accuracy] Quick-start command no longer works against current CLI**

**Confidence:** 95/100 | **Dimension:** commands | **Source-of-truth:** `cli/index.mjs:42-58` (verified 2026-04-21)

**Issue Explanation:**
The Quick Start section says `npx adk-install --setup`, but the CLI dropped the `--setup` flag in v3.0; `cli/index.mjs:42-58` shows the current entry point uses `npm run setup` (or the bare `adk-install` command with no flag). Following the doc as-written errors with `unknown option: --setup`.

**Suggested Fix:**
Replace the Quick Start command with the current invocation. Suggested replacement:

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git
cd agents-devkit
npm install
npm run setup
```

**Impact:**
Every new user who follows the README hits an error on the first command. This is the dominant onboarding path and the failure is silent (looks like the CLI is broken, not the doc).
```

## Praise template

```md
**[Praise][<primary-focus-area>] <Short title>**

**Confidence:** <0-100>/100 | **Dimension:** <dimension> | **Source-of-truth:** <source-anchor>

**Issue Explanation:**
<Explain what is notably well done and why it stands out — usually a section that is unusually clear, a particularly useful example, or a non-obvious gotcha that is captured well.>

**Suggested Fix:**
No change required.

**Impact:**
<Explain the concrete positive impact worth reinforcing.>
```

## Summary section (top of the report; in Confluence mode = footer comment)

```md
## Doc review summary

**Verdict:** <ready-to-publish | needs-fixes | needs-rewrite>

**Blockers:** <count>
**Critical:** <count>
**Should Have:** <count>
**Nitpicks / Questions:** <count>

### Blockers
- <one-line title> — `<doc-anchor>` vs `<source-anchor>`
- ...

### Critical
- <one-line title> — `<doc-anchor>` vs `<source-anchor>`
- ...

### Out of scope
- <items explicitly not reviewed and why>

### Validation
- Doc fetched / read: YES (<n> sections)
- Source-of-truth read: YES (<n> files / configs)
- Existing comments reconciled: <kept / stale / restated counts>  (Confluence mode only)
- Inline comments posted: <count or N/A>
- Footer summary posted: <YES | N/A>
```

## Severity ladder

| Severity | Meaning | Goes inline | Goes in summary list |
| --- | --- | --- | --- |
| `Blocker` | Wrong or dangerous — command does not work, env var name wrong, security advice incorrect | Yes | Yes |
| `Critical` | Misleading or seriously outdated — reader will likely waste time or hit a wall | Yes | Yes |
| `Should Have` | Notable gap — missing section the doc type expects, ambiguous wording | Yes | Counted only |
| `May Have` | Minor improvement — phrasing, ordering | Yes | Counted only |
| `Nitpick` | Style only — punctuation, list bullet style | Yes | Counted only |
| `Question` | Reviewer uncertain whether this is right; needs author input | Yes | Counted only |

Lead with the highest. Never mix levels in one bullet.

## Consolidation rules

1. Group related findings affecting the same doc section under one F-ID.
2. Use the highest severity in the group.
3. List each sub-issue as a bullet under the consolidated `Issue Explanation`.
4. Keep the consolidated finding actionable.
