# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Is this an implement, debug, or verify task?

**How to pick:** Implement = building from spec/roadmap. Debug = a failure exists and we need root cause + fix. Verify = no code change, prove a prior change is correct.

### Question 2
**Q:** What is the validation target (tests to pass, behavior to demonstrate, metric to hit)?

**How to pick:** Pick the smallest signal that proves correctness. Prefer existing tests > new test > manual repro.

### Question 3
**Q:** Can the work be split into thin vertical slices, or must it land atomically?

**How to pick:** Split unless the change is trivially atomic (one function, one config). Slicing reduces blast radius and gives faster validation.

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
