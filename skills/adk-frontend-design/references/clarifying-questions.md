# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What is the surface (page, component, feature flow)?

**How to pick:** Page → screen-level. Component → reusable primitive. Flow → multi-step user journey.

### Question 2
**Q:** What is the design source-of-truth (existing design system, Figma file, sibling components)?

**How to pick:** Existing design system always wins. Figma if a designer is involved. Sibling components when extending a pattern.

### Question 3
**Q:** Constraints: brand, accessibility, performance budget, internationalization?

**How to pick:** List as hard constraints. Brand = colors/fonts/voice. A11y = WCAG level, language support. Perf = LCP/CLS/INP targets. i18n = locale list + LTR/RTL.

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
