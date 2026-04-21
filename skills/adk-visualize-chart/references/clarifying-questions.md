# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the data source (file path, URL, query)?

**How to pick:** File = csv/json/parquet. URL = HTTP fetch (cache to .temp/notes/). Query = SQL/PromQL/etc., capture the query string.

### Question 2
**Q:** What story does the chart tell — what should the reader take away?

**How to pick:** One sentence. The chart type and design follow from this.

### Question 3
**Q:** Audience (engineer / leadership / external)?

**How to pick:** Engineer = denser, more annotations OK. Leadership = simpler, big takeaway label. External = no jargon, brand-safe colors.

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
