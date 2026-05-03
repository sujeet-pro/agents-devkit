# `docs-publish-gdrive` — clarifying questions

Asked under `-i`; defaults apply under `--auto` (except the always-
ask Phase 4 gate).

## Phase 0

1. **Source: `<md-file>`. Target name: `<resolved>`. Confirm?**
   - _Default under `--auto`:_ proceed.

2. **Folder: `<resolved>`. Override?**
   - _Default under `--auto`:_ CLI arg or `docs.md` default.

3. **Format: `<resolved>`. Override? (`gdoc` | `md` | `pdf`)**
   - _Default under `--auto`:_ `gdoc`.

## Phase 1

4. **Workspace Google Drive connector: connected?**
   - _Default under `--auto`:_ must be yes; else stop.

5. **(Only if format=pdf) pandoc available?**
   - _Default under `--auto`:_ must be yes; else stop with install
     hint.

## Phase 2

6. **Show converted artifact?**
   - _Default under `--auto`:_ no; logged to `converted.*`.
   - _When to ask:_ `-i` mode.

## Phase 3

7. **Existence check found `<N>` matches. Which to target?**
   - _When to ask:_ N > 1; always stop and ask. Never auto-pick.

## Phase 4 — always asks

8. **Publish `<source>` as `<name>` (`<format>`) into folder
   `<folder-id>`? Sharing will NOT be changed. [yes / no / diff]**
   - _Default under `--auto`:_ no default; block until response.

9. **(Only if human last-editor) The existing item was last edited
   by `<human>`. Overwrite?**
   - Default: DEFER.

## Phase 5

10. **Sharing drift detected. Show drift and stop?**
    - _Default under `--auto`:_ stop (no retry). The skill does not
      attempt to "fix" sharing; that's human-owned.

## Anti-rules

- Never ask the skill to change sharing. Even if the user requests
  it, redirect to the Drive UI.
- Never skip the Phase 4 ask under `--auto`.
- Never auto-pick between N>1 matches.
- Never default to overwriting human-authored items.
