# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the PR URL?

**How to pick:** Required. Provider auto-detected from host.

### Question 2
**Q:** Filter: address all, only Blockers/Critical, or only specific comment IDs?

**How to pick:** All = default. Severity-only = use when many comments and we want to ship core fixes first. Specific IDs = surgical follow-up.

### Question 3
**Q:** Reply style: terse ('Fixed in <sha>') or explanatory (one-paragraph 'why this fix')?

**How to pick:** Terse for nits, explanatory for design comments and pushbacks.

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
