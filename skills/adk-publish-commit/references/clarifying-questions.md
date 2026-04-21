# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What artifact: commit message, PR description, or changelog entry?

**How to pick:** Commit = single change. PR = aggregate of branch commits. Changelog = release-scoped summary.

### Question 2
**Q:** Convention: detect from git log, conventional commits, or project template?

**How to pick:** Default = detect from last 20 commits. Override only if the user states otherwise.

### Question 3
**Q:** Include co-authors / sign-off?

**How to pick:** Sign-off when DCO / project policy requires. Co-authors when pair-programmed (use Co-authored-by trailer).

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
