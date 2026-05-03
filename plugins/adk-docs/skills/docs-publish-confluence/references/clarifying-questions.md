# `docs-publish-confluence` — clarifying questions

Asked under `-i`; defaults apply under `--auto` (except the always-
ask gates in Phase 4, which survive `--auto`).

## Phase 0

1. **Source: `<md-file>`. Title: `<resolved>`. Confirm?**
   - _Default under `--auto`:_ proceed.

2. **Space: `<resolved>`. Override?**
   - _Default under `--auto`:_ CLI arg or `docs.md` default.

3. **Parent: `<resolved>`. Override?**
   - _Default under `--auto`:_ CLI arg or `docs.md` default.

## Phase 1

4. **Workspace Atlassian connector: connected? `<yes/no>`**
   - _Default under `--auto`:_ must be yes; else stop.

## Phase 2

5. **Show converted XHTML before publish?**
   - _Default under `--auto`:_ no; logged to `storage.xhtml`.
   - _When to ask:_ `-i` mode; conversion might have lost something.

## Phase 3

6. **Existence check found `<N>` matches. Which to target?**
   - _When to ask:_ N > 1 (ambiguous match); always stop and ask.
     Never auto-pick.

## Phase 4 — always asks (even under `--auto`)

7. **Publish `<source>` as `<title>` to `<space>` / `<parent>`?
   Action: `<new | update | defer>`**
   - Options: `yes` / `no` / `diff` (show diff, re-ask).
   - _Default under `--auto`:_ no default; the skill blocks until
     the user responds.

8. **(Only when last-editor is human) The page was last edited by
   `<human>` on `<date>`. Overwrite anyway?**
   - Default: DEFER (leave untouched).
   - Options: `yes, update` / `no` / `diff`.

## Phase 5

9. **Re-fetch drift detected. Show drift?**
   - _When to ask:_ storage re-fetch doesn't match.
   - _Default under `--auto`:_ show drift in the report; no retry.

## Anti-rules

- Never skip the Phase 4 ask under `--auto`. It's a shared-state
  write.
- Never auto-pick between N>1 existing matches.
- Never default to overwriting a human-authored page.
