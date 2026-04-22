# `temp-folder` — first-write protocol

Every skill, on its first write to `.temp/`, runs this:

1. Check `.gitignore`. If it does not contain a line equal to `.temp/` or `.temp` or starts with `.temp/`, append `.temp/`.
2. Check `.temp/` exists. `mkdir -p .temp` if not.
3. Resolve slug. If caller passed a slug, use it. Else derive from prompt nouns.
4. Check `.temp/task-<slug>/` exists. `mkdir -p` if not.
5. Resolve artifact sub-path per the canonical table.
6. Write.
7. Emit one-line `[adk:temp-folder] task=<slug> wrote=<path>` so the user can `cat` it.

For repeated writes in the same session, skip steps 1-4 (cached).
