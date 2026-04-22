# `temp-folder` — anti-patterns

- Writing intermediate artifacts to the repo root.
- Writing to `~/Desktop`, `/tmp`, `~/Downloads`.
- Putting browser screenshots in `assets/` or `public/`.
- Committing `.temp/`.
- Using a different slug per artifact in the same task.
- Cleaning up `.temp/task-<slug>/` after task completion (it is durable context).
- Using `.temp/notes/` for an artifact that has a canonical type (use the right sub-path).
- Symlinking `.temp/` to a shared location across repos (every repo's `.temp/` is local).
