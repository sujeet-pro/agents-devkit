# `temp-folder` — anti-patterns

- **Writing to the repo root for a working artifact.** No. `.temp/` exists for this.
- **Auto-deleting old `.temp/task-*/` folders.** They're durable context; the user prunes manually.
- **Using a different slug per skill in the same session.** One slug per task. The dispatcher passes it down.
- **Whitespace, uppercase, or punctuation in slugs.** Always kebab-case, lowercase, alphanumeric only.
- **Date-only slugs when descriptive ones are available.** "task-20260503-134242" is the fallback, not the default.
- **Slugs longer than 6 words.** They become unreadable in `ls .temp/`.
- **Date-prefixing every slug.** Date prefix only for disambiguation; not by default.
- **Truncating an existing folder on re-use.** Same slug + same task = same folder, append. Don't `rm -rf` it.
- **Skipping `mkdir -p`.** The folder must exist before the first artifact is written.
- **Using `~` in the path.** Always absolute paths after expansion.
