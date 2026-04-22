# `mode-contract` — author's workflow

When you author a new skill that should support multiple modes:

1. Decide which subset of `[auto, review, fix]` makes sense (see the table in `SKILL.md`).
2. Declare in frontmatter:
   ```yaml
   metadata:
     modes: [auto, review, fix]
   ```
3. In the skill's `references/modes.md`, document for THIS skill what each supported mode does. Be concrete (what gets written, what does NOT get written, what files change).
4. Add the mode to the status banner: `[adk:<skill>] mode=<X>`.
5. In the validator, add a Phase 1 check that the requested mode is in the supported set.
6. In `--mode fix`, always end by re-running `--mode review` to confirm zero residual findings (or report what remains).
