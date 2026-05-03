# `docs-review` — anti-patterns

## Findings

- **"The docs are missing some content."** Not a finding. Which
  section? What's missing? What would a reader open the doc looking
  for?
- **Staleness ≠ wrongness.** An old timestamp alone is a Nitpick or
  a Should-Have at most. If the content still matches the code, the
  doc is fine.
- **Style critiques on a runbook.** A runbook is optimized for speed
  during an incident, not prose elegance. "The phrasing is a bit
  imperative" is anti-feedback for a runbook.
- **Prose critiques without citing a line.** Point at the paragraph;
  quote the sentence; name the issue.
- **"Undecided" severity.** Every finding is tiered. If you can't
  tier it, it's not a finding.
- **Severity inflation.** Don't label a Nitpick as a Should-Have to
  make the review look thorough.

## Evidence

- **Claiming a contradiction without opening the code.** Every
  "wrong" finding cites `file:lines`. If you haven't opened the code,
  you haven't verified.
- **Treating the doc's word as evidence.** The doc is the thing being
  audited. Use the code to adjudicate.

## `--fix` pitfalls

- **Rewriting voice.** The author wrote it that way for a reason.
  Only correct facts.
- **Bulk structural changes.** Moving sections, merging sections,
  splitting sections — all controversial. Surface as findings.
- **Applying >20 corrections silently.** Paginate with approval to
  keep review overhead meaningful.
- **Writing to a shared Confluence / GDoc without opt-in.** Even
  under `--auto --fix`. A shared page has other readers.
- **Auto-fixing a human-authored page.** Last editor is the shipping
  author; opt-in required.
- **Running `--fix` on a published release-notes page.** Those are
  immutable by convention — surface findings, do not auto-apply.

## Scope

- **Reviewing a runbook for SEO.** Wrong audience.
- **Reviewing an ADR for implementation detail.** ADRs are about the
  decision, not the implementation.
- **Auditing the code while pretending to audit the doc.** If the
  finding is "the code is wrong", that's a different skill
  (`/adk-code:code-bugfix`).
