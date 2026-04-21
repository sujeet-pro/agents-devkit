# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** What framework and meta-framework (React/Next, Vue/Nuxt, Svelte/SvelteKit, Astro, Solid, Angular, ...)?

**How to pick:** Detect from package.json. State explicitly so the agent uses the right idioms.

### Question 2
**Q:** Is this a new component, a feature on an existing component, or a screen/route?

**How to pick:** New component → in components/ with story + test. Feature on existing → minimal diff, preserve API. Screen/route → in routes/ + data hooks.

### Question 3
**Q:** Design source-of-truth (Figma, design spec, sibling component)?

**How to pick:** Figma → reference frame URL. Spec → adk-frontend-design output path. Sibling → call out the pattern being matched.

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
