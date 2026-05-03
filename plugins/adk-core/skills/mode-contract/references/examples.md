# `mode-contract` — behavior table by combination

## End-to-end behavior matrix

| Invocation | Per-phase gate? | Apply changes? | First push gate? | Post comment gate? | Auto-merge? |
| --- | --- | --- | --- | --- | --- |
| `<skill>` (no flags) | yes (interactive default if not under top-level `--auto`) | no | yes | yes | NEVER |
| `<skill> --auto` | no | no (skill must opt-in to mutation via `--fix`) | yes (always asks first push) | yes | NEVER |
| `<skill> -i` | yes | no | yes | yes | NEVER |
| `<skill> --fix` | yes (interactive defaults to `-i`-shaped) | yes | yes | yes | NEVER |
| `<skill> --auto --fix` | no | yes | yes (first push only) | no (after first OK) | NEVER |
| `<skill> -i --fix` | yes | yes (per-finding accept) | yes | yes | NEVER |

## Sample sessions

### Review-and-post (default)

```text
/adk-review:review-pr <url>
```

- `--auto` is the marketplace default → skips per-phase gates.
- For each finding: validates against current diff, posts inline.
- Before first post: asks "ready to post N findings?".
- After: re-fetches and confirms IDs (post-confirmation protocol).

### Interactive review

```text
/adk-review:review-pr <url> -i
```

- Walks each finding; for each: accept / edit / discard.
- Asks before posting each batch.
- Same first-push / first-post gates.

### Fix-and-push (yours)

```text
/adk-review:review-pr <my-pr-url> --fix
```

- Switches to Path B (own-PR feedback path).
- For each accepted reviewer comment: applies the fix locally via `code-bugfix` / `code-refactor` / etc.
- Stages commits but does NOT push. Push is a separate user action.
- Replies to comments after push referencing the commit SHA.

### Auto-fix-and-push

```text
/adk-review:review-pr <my-pr-url> --auto --fix
```

- Same as above but without per-finding accept.
- Still asks before the first push.
- Never auto-merges.

### Force-push attempt

```text
git push --force origin main   # via the skill's Bash tool
```

- Blocked by the `PreToolUse:Bash` safety hook.
- Skill receives `{"decision":"block","reason":"force-push to main is forbidden"}`.

### Merge attempt

```text
gh pr merge <number>           # via the skill's Bash tool
```

- Hook permits `gh pr merge` only if the user has explicitly requested it earlier in the session.
- Otherwise: blocked.
