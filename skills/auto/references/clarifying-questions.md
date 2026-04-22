# `auto` — clarifying questions

Asked in order, one at a time. Under `--auto`, defaults apply.

1. **Is this slug correct: `<proposed-slug>`?** — _How to pick:_ The slug becomes `.temp/task-<slug>/`. Default: derived from the first 3-5 nouns in the prompt, kebab-cased.
2. **Should I gather context from these links: `<list>`?** — _How to pick:_ If the user pasted any link, default yes. Skip only if the user says "the prompt is self-contained".
3. **Confidence target: 80, 90, or 95?** — _How to pick:_ Production-safe = 95. Standard feature/refactor = 90 (default). Exploratory / personal = 85.
4. **Change tolerance: surgical, bounded, or transformative?** — _How to pick:_ Surgical = touch only what must change; reversible in <1h. Bounded (default) = touch one subsystem; reversible in <1d. Transformative = many subsystems; reversibility hard.
5. **(UI only) Do you want the 5-sample mockup loop or skip design?** — _How to pick:_ Default: 5-sample loop. Skip ONLY if the user has an external design they're handing over (Figma URL, mockup PNG).
6. **Auto-publish to PR after validation green?** — _How to pick:_ Default: yes (push + open PR + start `cicd-monitor`). No = stop after local validation green.
