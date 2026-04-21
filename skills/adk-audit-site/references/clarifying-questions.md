# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Which URL(s) to audit? Single page, top N pages, or full crawl?

**How to pick:** Single = focused investigation. Top N = sample (home + 5-10 high-traffic pages). Full crawl = comprehensive but slow; only with explicit approval.

### Question 2
**Q:** Dimensions: performance / accessibility / SEO / UX / security-headers / all?

**How to pick:** All by default. Narrow when retesting a specific dimension.

### Question 3
**Q:** Devices and connection profiles?

**How to pick:** Default = desktop + mobile, fast 3G + cable. Match real user distribution if known.

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
