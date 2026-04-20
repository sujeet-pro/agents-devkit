---
title: 'adk-docs-review'
description: 'Review an existing technical document for accuracy, freshness, structure, completeness, and readability - producing severity-tiered findings against the actual code or configs the doc claims to describe. Use when the deliverable is a critique with actionable fixes for a doc that already exists. Do not use to write a new doc (use adk-docs-write) or to review code (use adk-review-pr / adk-review-local).'
skill_name: adk-docs-review
category: task
---

# adk-docs-review

Review an existing technical document for accuracy, freshness, structure, completeness, and readability - producing severity-tiered findings against the actual code or configs the doc claims to describe. Use when the deliverable is a critique with actionable fixes for a doc that already exists. Do not use to write a new doc (use adk-docs-write) or to review code (use adk-review-pr / adk-review-local).

## Skill body

# ADK Docs / Review

Standalone task skill under the `adk-docs` category router. Produces a findings-first review of an existing document with each finding anchored to the doc and to the source-of-truth it claims to describe.

## When to use

- A doc is suspected of drifting from the code.
- A doc must be checked before publishing or before a release.
- A doc is being adopted by a new team and they want a quality bar.
- A handoff requires confirming the doc is still accurate.

## When NOT to use

- The doc does not exist yet -> `adk-docs-write`
- Reviewing code, not docs -> `adk-review-pr` / `adk-review-local`
- Auditing a whole repo -> `adk-audit-repo` (which can call this skill per-doc)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<doc path or URL>` | yes | Local file or fetched markdown |
| `<focus>` | optional | `accuracy` / `freshness` / `structure` / `readability` / `all` (default) |
| `<source-of-truth>` | optional | Path or URL the doc must agree with (default: inferred from doc) |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate doc, focus, source-of-truth. Approval gate unless `--auto`.
2. **Read doc + source** - read the doc end-to-end; read the linked code, configs, scripts, env files. Repo evidence over guessing.
3. **Run dimension passes**:
   - **Accuracy**: every command, code block, schema, env var, link resolves and matches the source.
   - **Freshness**: any "as of X" claims, version references, screenshots, or version-specific instructions are still current.
   - **Structure**: presence and order of expected sections (per doc type), level hierarchy, table consistency.
   - **Readability**: lead, scannability, jargon vs. defined terms, length.
4. **Tier findings** - assign severity (Blocker / Critical / Should Have / May Have / Nitpick / Question).
5. **Validate** - reread each finding against the doc + source to confirm it is real and reproducible.
6. **Report** - findings-first markdown ordered by severity; recommend the next step (fix in place, hand off to `adk-docs-write` for major rewrite).

## Severity ladder

| Label | Doc meaning |
| --- | --- |
| `Blocker` | Wrong or dangerous - command does not work, env var name wrong, security advice incorrect |
| `Critical` | Misleading or seriously outdated - reader will likely waste time or hit a wall |
| `Should Have` | Notable gap - missing section the doc type expects, ambiguous wording |
| `May Have` | Minor improvement - phrasing, ordering |
| `Nitpick` | Style only - punctuation, list bullet style |
| `Question` | Reviewer uncertain whether this is right; needs author input |

## Finding template

```markdown
### [<Severity>] <One-line summary>
- **Doc location**: `<doc-path>:LINE-LINE` (or section heading)
- **Source-of-truth**: `<source-path>:LINE-LINE` (or URL with date)
- **Issue**: <2-3 sentence explanation>
- **Suggested change**: <concrete recommendation, replacement text if useful>
- **Why this severity**: <one sentence>
```

## Output format

```
## Doc Review: <doc-path>
- Source-of-truth: <source-path>
- Focus: <focus>

## Verdict
<ready-to-publish | needs-fixes | needs-rewrite>

## Findings

### Blockers
<finding blocks>

### Critical
<finding blocks>

### Should Have
<finding blocks>

### May Have
<finding blocks>

### Nitpicks
<finding blocks>

### Questions
<finding blocks>

## Out of Scope
- <items explicitly not reviewed and why>

## Recommended Next Step
- <e.g. "fix Blockers in place" or "hand off to `adk-docs-write` for restructure">

Need more detail on any finding?
```

## Per-doc-type focus tips

| Doc type | Watch for |
| --- | --- |
| README | Quick start commands actually work; install steps include version requirements |
| Runbook | Mitigation steps tested in the last quarter; commands are copy-paste ready |
| API reference | Signatures match the code; error codes complete |
| ADR | Status reflects reality (Accepted vs. Superseded); consequences honest |
| Onboarding | Day-1 list still possible from a clean machine; "who to ask" is current |
| Migration guide | Source/target versions still relevant; rollback path concrete |
| Tech radar | Dates and signals not stale; ring movement justified |

## Anti-patterns

- Calling out "improve clarity" without a concrete suggested change.
- Marking nitpicks as Critical because they are visible.
- Reviewing the doc against memory instead of the source code.
- Findings without doc location anchors.
- Verdict of "looks good" with zero validation runs against the source.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/review-comment-format.md` | Standard finding format with stable IDs and severities. |

<!-- adk:references:end -->

## References shipped with this skill

- `references/anti-patterns.md`
- `references/constitution.md`
- `references/examples.md`
- `references/output-format.md`
- `references/persona.md`
- `references/review-comment-format.md`
