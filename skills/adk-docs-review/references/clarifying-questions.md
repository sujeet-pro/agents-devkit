# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Where is the doc (path or URL)?

**How to pick:** Required. URLs are fetched if reachable.

### Question 2
**Q:** Where is the source-of-truth (path, URL, or 'inferred from doc')?

**How to pick:** Explicit > inferred. State the file/dir that the doc claims to describe.

### Question 3
**Q:** Focus: accuracy / freshness / structure / readability / all?

**How to pick:** All for first review. Narrow when iterating after a fix pass.

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
