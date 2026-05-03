# `setup` — clarifying questions

Asked one at a time, only when the answer changes the plan.

1. **Target: all topics or just `<topic>`?**
   - Default: `all` for first-run; `<topic>` if surfaced from a skill error.

2. **Default editor for meta-info file edits?**
   - Default: `info.md.default_editor` if set; else `$EDITOR`; else `nvim`; else `vi`.
   - Only ask the first time setup runs on a fresh machine.

3. **Install missing CLI tool `<X>` now?**
   - Default: NO (just print the install command). Setup never runs `brew install` for the user.

4. **Open `~/.config/adk/<topic>.md` in editor now? (file doesn't exist yet — will copy template first.)**
   - Default: YES (under interactive mode). Under `--auto`: copy template, do NOT auto-open; print "edit at <path> when ready".

5. **Topic `<topic>` validation failed: `<error>`. Re-open for fixes?**
   - Default: YES. Loops until valid or user opts out.

6. **Print `export` lines for missing env vars to ~/.zshenv? (will NOT auto-append.)**
   - Default: YES (just print). Setup never appends to shell rc files.

## Anti-rules

- Never ask 3 confirmations in one turn. One at a time.
- Never ask under `--auto` — defaults apply silently.
- Never ask for confirmation on a read-only action (e.g. running `command -v`).
