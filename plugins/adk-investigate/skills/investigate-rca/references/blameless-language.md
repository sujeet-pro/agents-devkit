# `investigate-rca` — blameless language

Improvements over indictments. The RCA is a learning artifact, not a punishment. This file is the substitution list applied during the Phase 6 blameless-language pass.

## Substitution principle

Every sentence that names a person as the *cause* of an outcome is rewritten to name the *system gap* that allowed the outcome. The person remains in the timeline as metadata (so the team knows whom to ask for context); they do not appear in the root cause / contributing factors sentences.

## Substitutions

| BLAME-SHAPED | SYSTEM-SHAPED |
| --- | --- |
| "Alice's PR caused the outage" | "The new query path in PR #2841 referenced a renamed column; the system gap is no integration test for renamed-column scenarios" |
| "Bob approved the PR without checking" | "The code-review process didn't flag the renamed column reference; the migration ledger isn't surfaced to reviewers" |
| "Carol was slow to respond" | "Time to acknowledge was 2 minutes (page → ack); within target, but the team's runbook is unclear about which channel acknowledges first" |
| "The team forgot to update the runbook" | "The runbook had not been updated since the previous deploy system change; the system gap is no automated runbook-staleness alert" |
| "Dave shouldn't have rolled out 50% → 100% in one step" | "The Statsig rollout convention (50% with 7-day soak before 100%) is policy, not policy-enforced. Anyone with `omni_write` can step-jump rollouts." |
| "Erin made a mistake in the migration" | "The migration ran to completion but the dependent code change was merged 7 days later. The system gap is no enforced ordering between schema migrations and dependent code changes." |
| "We should be more careful in code review" | "Add a CI check that comments on PRs whose queries reference recently-renamed columns" |
| "Frank didn't notice the alert" | "The alert paged the wrong on-call rotation due to a stale schedule. The system gap is the on-call schedule was edited 2 weeks ago without re-testing the page routing." |

## Rules

1. **Names appear in the timeline only.** "13:02: Alice's PR `a3f9c2e` deployed to prod [PR #2841]" is fine — that's metadata. "Root cause: Alice's PR" is not.
2. **The system gap sentence ends section 5.** Always present. Always system-shaped.
3. **Action items name owners (WHO field).** This is operational accountability, not blame. The owner is responsible for *fixing* the gap; they did not *cause* the incident.
4. **"What worked" mentions positive contributors.** "On-call (Carol) acknowledged in 2 minutes" is fine — that's a positive observation, not blame.
5. **Avoid passive voice when it hides agency.** "Mistakes were made" is worse than naming the system gap. "The query referenced a renamed column" is better than "mistakes were made by the team".

## The Phase 6 blameless pass

After drafting the RCA in Phase 6, the skill scans every sentence in sections 5 (Root cause) and 6 (Contributing factors) for blame-shaped language. The scan looks for:

- Named individuals followed by causal verbs ("Alice caused", "Bob missed", "Carol delayed").
- Vague accusatory phrases ("the team forgot", "people weren't paying attention").
- "We should have known" / "we should have caught this" — these put blame on the collective without naming the system gap.

For each match, the skill applies the substitution rule:

1. Identify the system gap that allowed the named outcome.
2. Rewrite the sentence in system-shaped form.
3. Move the named individual (if relevant) to the timeline as metadata.
4. Log the rewrite to `.temp/task-<slug>/investigation/rca/blameless-rewrite-log.md` for transparency.

## What's NOT blame (do not rewrite)

- "Alice authored PR #2841." → metadata; keep.
- "Bob reviewed PR #2841." → metadata; keep.
- "On-call (Carol) acknowledged the page at 13:04." → metadata; keep.
- "The platform team owns this action item." → operational; keep.
- "Alice can answer questions about the v3 implementation." → context; keep.

The rewrite applies only to causal claims, not to factual mentions.

## Why blameless

Blameless RCAs work because:

- People who know they will not be blamed share more honestly. The team learns more.
- The same individual can make the same mistake on a different system; the gap is the durable lesson.
- Action items target the system, which can be improved. People can't be "improved" via an action item.
- Trust in the post-mortem process determines whether the team writes them at all.

This is established post-mortem culture (see Etsy's blameless post-mortem essay, Google SRE Book Chapter 15, Allspaw 2012). The skill enforces the practice mechanically.

## Edge cases

- **Single-engineer team.** When there's only one author / reviewer / on-call, blame is structurally avoided by writing about the system: "The single-maintainer setup creates a single-point-of-knowledge risk; the action item is to onboard a second maintainer to the on-call rotation."
- **Vendor-caused incident.** Don't blame the vendor by name in the root cause; describe the dependency: "The system has no graceful degradation for transient upstream failures."
- **Operator-error during triage.** "The on-call applied the wrong rollback target" → rewritten to "The rollback workflow accepts an arbitrary SHA without verifying it's a known-good build; the system gap is no allowlist of safe rollback targets."

## Hand-off

The RCA, after the blameless pass, goes to the operator for review. The operator may:

- Accept the rewrites as-is.
- Edit further (the operator knows team / political context the skill doesn't).
- Escalate to a peer reviewer before publishing.

The skill never publishes; the human does. The blameless pass ensures the draft they review is already framed correctly.
