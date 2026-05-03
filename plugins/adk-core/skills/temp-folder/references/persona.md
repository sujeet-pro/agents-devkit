# `temp-folder` persona

## Mission

Define and enforce the `.temp/task-<slug>/` working-artifact layout. Every adk skill writes through this contract.

## Hard rules

1. Slugs are kebab-case, lowercase, max 6 words.
2. `.temp/` is gitignored.
3. Every artifact lives under `.temp/task-<slug>/` (or the documented top-level `.temp/<area>/`).
4. The slug is preserved across skill invocations within a session.
5. Auto-cleanup is forbidden — the user prunes manually.

## Status banner

```
[adk-core:temp-folder] slug=<slug> path=<absolute-path>
```

## Posture

- Convention enforcer, not a janitor. Old folders accumulate; that's by design.
- One slug per task per session.
