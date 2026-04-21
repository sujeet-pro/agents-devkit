# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Where do the changes live: a remote PR, local working tree, or already-pushed branch?

**How to pick:** Remote PR → adk-review-pr. Local uncommitted → adk-review-local. Already-pushed but no PR yet → adk-review-local first, then publish.

### Question 2
**Q:** Are there existing reviewer comments to address?

**How to pick:** Yes → adk-review-feedback. No → adk-review-pr or adk-review-local.

### Question 3
**Q:** Is the goal a session handoff (capture state for the next agent/human)?

**How to pick:** Yes → adk-review-handoff.

## Standard option-presentation shape

Where the answer is multiple-choice (mode, focus, depth, severity filter, etc.), present each option as:

```
### Option <A | B | C>: <short label>
- What it does: <one sentence>
- Pros: <2-3 bullets>
- Cons: <2-3 bullets>
- Best when: <one sentence with a concrete signal>
- Blast radius: surgical | bounded | transformative
- Reversibility: easy | moderate | hard
```

Mark exactly one option `(default)` and say in one sentence why it is the safest pick for the current evidence.
