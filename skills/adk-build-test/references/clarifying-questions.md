# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What test type: unit, integration, end-to-end, contract, regression?

**How to pick:** Unit = pure functions / isolated modules. Integration = collaborating modules + real adapters. E2E = full user flow through deployed surface. Contract = API consumer/provider agreement. Regression = locks down a fixed bug.

### Question 2
**Q:** Is the work test-only, or are tests part of a larger feature/fix?

**How to pick:** Test-only → this skill. Tests-with-feature → adk-build-feature, with tests written in the same change.

### Question 3
**Q:** What coverage target — by line, by branch, by behavior?

**How to pick:** Behavior > branch > line. State the behaviors that must be covered, not a percent.

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
