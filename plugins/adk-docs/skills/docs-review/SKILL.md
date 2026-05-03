---
name: docs-review
description: |
  Review an existing technical document — a markdown file in the repo, a fetched URL, a Confluence page via the workspace Atlassian connector, or a Google Doc via the workspace Google Drive connector — for accuracy against the actual code, freshness, structure, completeness, and readability. Produces severity-tiered findings (Blocker = wrong / actively misleading; Critical = stale and load-bearing — e.g. runbook references a deleted env var; Should-Have = missing context; May-Have = polish; Nitpick). Verifies every "the code does X" claim by opening the code. With --fix, applies only non-controversial corrections (renamed path, removed feature, changed flag, wrong default) in place; NEVER rewrites the doc's voice. Use when the deliverable is feedback on an existing doc. Do NOT use for authoring a new doc (/adk-docs:docs-write), drafting a PR description (/adk-docs:docs-pr-description), or reviewing code changes (/adk-review:review-code-changes, /adk-review:review-pr).
metadata:
  category: docs
  kind: task
  layer: 5
  modes: [auto, interactive, fix]
  needs_meta_info: [info, repos, docs]
argument-hint: "<doc-path-or-url> [--auto] [-i] [--fix]"
---

# docs-review — audit an existing doc against the source

Source-of-truth auditor. Finds where the doc and the code diverge,
tiers findings by severity, and (with `--fix`) corrects what's non-
controversially wrong without rewriting voice.

## When to use

- "review this runbook"
- "audit the on-call doc"
- "is this Confluence page still right?"
- "check the README for staleness"
- "review the migration guide before I send it out"

## When NOT to use

| Not this → | Use this |
| --- | --- |
| authoring a new doc | `/adk-docs:docs-write` |
| drafting a PR description | `/adk-docs:docs-pr-description` |
| reviewing a PR's code | `/adk-review:review-pr` |
| reviewing local code changes | `/adk-review:review-code-changes` |
| publishing (post-review) to Confluence | `/adk-docs:docs-publish-confluence` |
| publishing (post-review) to GDrive | `/adk-docs:docs-publish-gdrive` |

## Common prompts

- "review this doc"
- "audit the runbook"
- "is the README still right?"
- "review the Confluence page at <url>"
- "review the GDoc at <url>"
- "check for accuracy"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<doc-path-or-url>` | yes | — |
| `-i` / `--interactive` | no | off |
| `--fix` | no | off; with it, applies non-controversial corrections in place |

## Workflow

```
Phase 0 — prompt expansion
  - Resolve target kind: local md path | fetched URL | Confluence page |
    Google Doc (based on URL shape).
  - Pick slug; create .temp/task-<slug>/.

Phase 1 — preflight
  - For Confluence target: check claude.ai Atlassian workspace connector is connected.
  - For GDoc target: check claude.ai Google Drive workspace connector is connected.
  - Resolve the repo the doc describes via ~/.config/adk/repos.md.

Phase 2 — accuracy check
  - Follow references/accuracy-check-protocol.md: for every "the code
    does X" claim in the doc, open the cited file (or locate by name),
    and verify.
  - Classify each claim: OK | wrong | stale-but-correct | unverifiable.

Phase 3 — structure + freshness + readability audit
  - Headings depth, duplication, broken links, audience mismatch.
  - Last-modified vs last-code-touched (git log on cited files).
  - Audience calibration check (runbook reads like prose?).

Phase 4 — triage findings
  - Severity tier per finding (Blocker / Critical / Should-Have /
    May-Have / Nitpick).
  - Write .temp/task-<slug>/review.md per references/output-format.md.

Phase 5 — optional --fix
  - For findings labeled non-controversial (see modes.md), apply the
    correction in place (local md) or via the connector (Confluence /
    GDoc).
  - Surface controversial findings to the user for decision.
```

See `references/workflow.md` for the full stage detail.

## Persona

> "Audit against the source." A doc that contradicts the code is worse
> than no doc — it actively misleads. Stale docs become Blockers when
> they describe security flows, on-call procedures, or payment flows.
> You triage by severity and fix only what's non-controversially wrong;
> the author's voice is untouchable.

See `references/persona.md`.

## Constitution

**Must do:**

1. Verify every "the code does X" claim by opening the code (per
   `references/accuracy-check-protocol.md`).
2. Distinguish stale (old, still correct), wrong (contradicts code),
   and incomplete (missing a section a reader needs) — three different
   severities.
3. Cite evidence per finding: `doc:<location> vs code:<file>:<lines>`.
4. Tier every finding; no "this might be an issue" undecided findings.
5. For Confluence / GDoc targets, note the last editor and last-
   modified — raise the bar for `--fix` on recently-human-edited pages.

**Must not do:**

1. Rewrite the doc's voice in `--fix`. Only correct factual errors,
   renamed paths, changed flags, removed features, and typos.
2. Post findings to a shared Confluence / GDoc without explicit
   approval, even under `--auto --fix`.
3. Treat a stale timestamp alone as a Blocker — staleness of timestamp
   ≠ staleness of content.
4. Apply a change labeled "controversial" (voice, structure, added
   sections) under `--fix`.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- "The docs are missing some content" — be specific: section, what's missing, what a reader would look for.
- Style critiques on a runbook; it's not prose.
- Treating old timestamps as Blockers without checking content.
- Bulk-rewriting under `--fix` to "clean up the voice".

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/review.md` | The full review with tiered findings and evidence |
| `.temp/task-<slug>/fixes-applied.md` | (under `--fix`) list of applied corrections with diff |
| `.temp/task-<slug>/fixes-deferred.md` | (under `--fix`) controversial findings surfaced to user |
| `.temp/task-<slug>/report.md` | Final consolidated report |

See `references/output-format.md`.

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Source-of-truth-auditor persona |
| `references/workflow.md` | Phase 0–5 stage detail |
| `references/modes.md` | `--auto / -i / --fix`; non-controversial vs controversial rules |
| `references/interaction-contract.md` | Canonical interaction contract (byte-identical) |
| `references/anti-patterns.md` | What to avoid |
| `references/examples.md` | Worked reviews (README, runbook, Confluence page) |
| `references/output-format.md` | `review.md` shape + severity rubric |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase gates |
| `references/how-it-works.md` | Mermaid flow |
| `references/clarifying-questions.md` | Questions under `-i`; defaults under `--auto` |
| `references/accuracy-check-protocol.md` | Per-claim verification procedure |

## Additional links

- The workspace Atlassian connector's Confluence read endpoint (used when the target is a `*.atlassian.net/wiki/*` URL).
- The workspace Google Drive connector's GDoc read endpoint (used when the target is a `docs.google.com/*` URL).
- Upstream framework docs when the doc describes an external API.
