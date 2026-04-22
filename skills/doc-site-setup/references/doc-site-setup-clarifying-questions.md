# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Is there already a pagesmith.config.json5? Should we overwrite it?

**How to pick:** Default = no, never silent. Yes = explicit user approval needed.

### Question 2
**Q:** What is the base path (GitHub Pages style `/<repo>/` or custom-domain root `/`)?

**How to pick:** GitHub Pages without custom domain → `/<repo>/`. Custom domain → `/`. Subpath hosting → explicit.

### Question 3
**Q:** Skip GitHub Pages workflow (--skip-deploy)?

**How to pick:** Skip when the repo deploys via Vercel/Netlify/S3/custom; the gh-pages workflow would conflict.

### Question 4
**Q:** Diagram-only repo (Graphviz only, no Mermaid/Excalidraw/Draw.io)?

**How to pick:** Yes → skip `diagramkit warmup`. No → warmup required.

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
