---
name: adk-review
description: Category router for code review work - reviewing a pull request, reviewing local uncommitted changes, addressing review feedback, or capturing a session handoff so the next reviewer or session can continue without information loss. Picks one of adk-review-pr, adk-review-local, adk-review-feedback, adk-review-handoff.
---

# ADK Review (Category Router)

Routes any "look at code that already exists, judge it, capture state" intent to the right review task. Activate one of the listed task skills below; do not review directly from this router.

## When to use this category

- A PR or merge request needs a structured review with severity-tiered findings.
- Local uncommitted (or branch) changes need a self-review before pushing or committing.
- Reviewer comments need to be triaged and addressed in code with traceable replies.
- A long-running task needs to be paused or handed off without losing context.

## When NOT to use this category

- Implementing new code -> `adk-build`
- Reviewing documentation only -> `adk-docs-review`
- Auditing an entire repo or website -> `adk-audit`
- Drafting commit/PR text from a clean review -> `adk-publish-commit`

## Shared workflow

Every task in this category honors the same six steps. The task skills tailor the content of each step.

1. **Confirm intent** - identify target (PR URL, branch, file set, comment thread, session); set scope and severity bar.
2. **Gather** - read the diff, related code, related tests, recent history, and prior comments. Use repo evidence over guessing.
3. **Assess** - produce findings ordered by severity (Blocker / Critical / Should Have / May Have / Nitpick / Question). Separate verified issues from open questions.
4. **Resolve** - either author replies / fixes (review-feedback) or capture the snapshot (handoff). PR/local review just reports.
5. **Validate** - if changes were made, run repo-native checks; if findings were posted, verify they are visible.
6. **Report** - findings-first summary; explicit "not validated" markers; recommended next step.

## Task selection

| Task skill | Use when | Do NOT use when |
| --- | --- | --- |
| `adk-review-pr` | A specific PR URL or remote MR is the target; produce findings for posting back | The change is local and not yet pushed - use review-local |
| `adk-review-local` | Uncommitted changes, staged changes, or current branch vs. base needs a self-review before push | The change is already on a remote PR - use review-pr |
| `adk-review-feedback` | Existing review comments must be triaged and addressed in code with traceable replies | The reviewer comments are not yet posted - just iterate locally |
| `adk-review-handoff` | A session must be paused, switched, or handed off; capture state, decisions, blockers, git status | Writing project documentation - use docs-write |

## Severity ladder

All review-style outputs use the same labels:

| Label | Meaning |
| --- | --- |
| `Blocker` | Must fix before merge / before continuing. Bug, security hole, broken contract. |
| `Critical` | Strongly recommended fix; would normally block release. |
| `Should Have` | Improvement that meaningfully raises quality; deferring needs justification. |
| `May Have` | Optional polish; no harm in skipping. |
| `Nitpick` | Style or taste; never block on this alone. |
| `Question` | Reviewer is unsure; needs clarification, not necessarily a fix. |

Lead with the highest severity. Never bury a Blocker under nitpicks.

## Activation

Once you have picked a task, load `adk-review-<task>` and follow it. Each task skill is fully standalone - everything it needs is in its own folder.

## Anti-patterns

- Reviewing inside this router. Always hand off to a task skill.
- Mixing severity levels in one bullet ("nit/blocker"). Pick one.
- Posting findings without verifying the diff context.
- Marking something "fixed" in feedback without running validation.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Where do the changes live: a remote PR, local working tree, or already-pushed branch?** — _How to pick:_ Remote PR → adk-review-pr. Local uncommitted → adk-review-local. Already-pushed but no PR yet → adk-review-local first, then publish.
2. **Are there existing reviewer comments to address?** — _How to pick:_ Yes → adk-review-feedback. No → adk-review-pr or adk-review-local.
3. **Is the goal a session handoff (capture state for the next agent/human)?** — _How to pick:_ Yes → adk-review-handoff.

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** Decision table covering all four review modes.

**Artifact:** `review-routing-decision` — Inline message.

**Artifact path:** (none)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Where do the changes live: a remote PR, local working tree, or already-pushed branch?** — _How to pick:_ Remote PR → adk-review-pr. Local uncommitted → adk-review-local. Already-pushed but no PR yet → adk-review-local first, then publish.
2. **Are there existing reviewer comments to address?** — _How to pick:_ Yes → adk-review-feedback. No → adk-review-pr or adk-review-local.
3. **Is the goal a session handoff (capture state for the next agent/human)?** — _How to pick:_ Yes → adk-review-handoff.

## Default vs detailed output

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** Decision table covering all four review modes.

**Artifact:** `review-routing-decision` — Inline message.

**Artifact path:** (none)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/persona.md` | The agent persona that drives this skill. |

<!-- adk:references:end -->
