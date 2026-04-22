# `doc-site-diagrams` — anti-patterns

- Skipping the Phase-1 validator.
- Producing the artifact without cited evidence.
- Writing outside `.temp/task-<slug>/` before user approval.
- Mixing `--mode review` with source edits.
- Looping more than 3 times on the same failure without escalating to the user.
- Auto-doing anything irreversible (force-push, rm -rf, schema drop, prod deploy) — refuse even under `--auto`.