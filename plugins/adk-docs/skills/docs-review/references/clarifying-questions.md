# `docs-review` — clarifying questions

Asked under `-i`; defaults apply under `--auto`.

## Phase 0 questions

1. **Target: `<path-or-URL>`. Confirm?**
   - _Default under `--auto`:_ the argument as given.

2. **Audit scope: accuracy, structure, both? Override?**
   - _Default under `--auto`:_ both.
   - _When to ask:_ user wants a quick accuracy-only pass before a
     release cut.

## Phase 1 questions

3. **Repo to audit against: `<repo>`. Override?**
   - _Default under `--auto`:_ matched from `repos.md`; if no match,
     audit is structure-only.

4. **Target was last edited by `<human>` on `<date>`. Treat as
   bot-authored for `--fix`?**
   - _Default under `--auto --fix`:_ still requires explicit opt-in
     for human-authored shared pages — this is one of the few asks
     that survives `--auto`.

## Phase 4 questions (after findings surface)

5. **`<N>` findings, `<B>` Blockers. Continue to `--fix`?**
   - _Default under `--auto`:_ continue if `--fix` was passed.
   - _When to ask:_ `-i` mode; the user wants to inspect findings
     before any write.

## Phase 5 questions (under `--fix`)

6. **Apply these `<N>` non-controversial fixes now?**
   - _Default under `--auto --fix`:_ yes for local md; yes-with-
     backup for bot-authored shared pages; opt-in for human-authored.

7. **Controversial findings: surface in `fixes-deferred.md` only?**
   - _Default under `--auto`:_ yes (default).

## Anti-rules for asking

- Never ask about something the target argument already disambiguates
  (e.g. a full URL unambiguously names the target).
- Never ask the user to tier findings for you — that's your job.
- Never stack 3 questions in one turn.
- Never silently apply a fix to a human-authored shared page under
  `--auto --fix` — this is the one prompt that survives `--auto`.
