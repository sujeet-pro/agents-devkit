# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Does behavior change (new feature, bug fix, enhancement) or is it pure restructure?

**How to pick:** Behavior change → feature. Pure restructure → refactor.

### Question 2
**Q:** Is this a framework/library upgrade across the codebase?

**How to pick:** Yes → migrate. No → feature or refactor.

### Question 3
**Q:** Is the work test-only?

**How to pick:** Yes → test. No → other.

### Question 4
**Q:** Is the work dependency-only (upgrade/audit/prune deps)?

**How to pick:** Yes → deps. No → other.

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
