# `docs-commit-message` — clarifying questions

Asked under `-i`; defaults apply under `--auto`.

## Phase 0 questions

(none; repo resolution is deterministic from CWD)

## Phase 1 questions

1. **Detected convention: `<style>` (`<N>/10` recent matches).
   Override?**
   - _How to pick:_ Default is the detected style. Override with
     `--style conventional|semantic|free`.
   - _Default under `--auto`:_ the detected style.

2. **Staged changes span `<N>` files across `<M>` directories. The
   dominant area is `<dir>`. Commit as one unit, or split?**
   - _When to ask:_ `-i` mode and the diff looks multi-logical (e.g.
     `src/checkout/` + `db/migrations/` + unrelated docs).
   - _Default under `--auto`:_ one unit; the skill will note the
     cross-area nature in the body.

## Phase 2 questions

3. **Proposed subject: `<subject>`. Accept?**
   - _Default under `--auto`:_ accept; the user can always edit
     `commit-msg.txt` before `--fix`.

4. **Include a Co-authored-by trailer?**
   - _Default under `--auto`:_ no, unless the diff has explicit
     co-author hints.

## Phase 4 questions (under `--fix`)

5. **Run `git commit --file .temp/task-<slug>/commit-msg.txt` now?**
   - _Default under `--auto --fix`:_ **still asks once** — this is
     the one ask that survives `--auto`.

6. **Hook rejected: `<output>`. Re-draft, or stop?**
   - _Default under `--auto`:_ stop (do NOT silently retry).
   - Never retry with `--no-verify`.

## Anti-rules

- Never ask more than one question per turn.
- Never ask the user to pick a ticket ref — read it from the
  branch name / diff context or don't include it.
- Never ask "should I commit?" without re-showing the message.
- Never offer `--no-verify` as an option. It isn't.
