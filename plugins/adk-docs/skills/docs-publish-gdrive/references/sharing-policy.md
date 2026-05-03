# Sharing policy — hard rules

`docs-publish-gdrive` NEVER changes sharing permissions. This file
codifies the rule so that the skill's validator can enforce it and
any future maintainer inherits the invariant.

## The rule

> The skill does not call `permissions.create`,
> `permissions.update`, `permissions.delete`, or any sharing-related
> operation. A published item inherits its folder's sharing. Any
> deviation is a bug.

## Why this rule

- **Org security policy.** Automated sharing changes are a common
  vector for accidental data exposure. The operator's org requires
  human action for any sharing change.
- **Predictability.** A user who placed a file in a private folder
  should never discover it's been auto-shared with their team or
  the public.
- **Blast radius.** The skill publishes 1 item per run. A sharing
  bug could over-expose dozens of items before detection. The
  policy eliminates the whole class.

## What "sharing" includes

- Individual user/group `permissions` entries.
- Link-sharing settings (`anyone`, `anyone with link`, `domain`,
  `restricted`).
- Role changes (`reader`, `commenter`, `writer`, `owner`).
- Domain-scoped access (`domain:acme.com`).
- Published-on-web settings.
- Publish-to-web (Google Apps Publisher).

## What the skill DOES touch

- `files.create` (new items).
- `files.update` (existing items — body only).
- `documents.batchUpdate` (GDoc content ops after create).
- `files.get` (read metadata; read-only).
- `permissions.list` (read-only snapshot for the invariant check;
  never write).

## Pre- and post-publish invariant

1. Before publish:
   - Read the target folder's permissions.
   - For updates: read the existing item's permissions.
   - Write both to `sharing-snapshot.md` as the "pre" block.

2. After publish:
   - Re-read the item's permissions.
   - Write to `sharing-snapshot.md` as the "post" block.
   - Compute the diff.

3. Diff rule:
   - **Expected: empty** (modulo the connector's own service account
     identity, which is always present as owner of anything it
     creates).
   - **Any non-expected diff = FAILURE.** Stop. Do not claim
     success. Surface the drift to the user. Do NOT attempt to
     "revert" the drift (that would be another sharing write,
     which the policy forbids).

## Enforcement in the skill

- Static: the skill's source code does not contain any call to
  `permissions.create`, `permissions.update`, `permissions.delete`.
  Reviewers enforce this at code-review time.
- Dynamic: the validator (`references/validator.md`) asserts the
  pre/post snapshot diff is empty at the end of Phase 5. If the
  assertion fails, the report marks the run as a failure even if
  the content landed.

## Why the skill still records `permissions.list`

Reading permissions is safe and necessary for the invariant check.
The skill uses `permissions.list` only in Phase 1 (folder snapshot)
and Phase 5 (post-publish check). Never in Phase 4 (the publish).

## What about shared drives?

- **Shared drives** (formerly Team Drives) have their own sharing
  model.
- The preflight checks that the service account has `writer` on
  the shared drive before publishing.
- Sharing on a shared drive item is governed by the shared drive's
  policy; the skill's invariant still applies (diff pre/post = 0).

## When the user wants sharing

If the user's prompt is "publish and share with alice@acme.com",
the skill:

1. Publishes without sharing changes (as usual).
2. Surfaces in the report:
   ```
   Sharing change requested but NOT applied by this skill (per
   policy). Share manually via the Drive UI or a separate admin
   workflow:
     https://docs.google.com/document/d/<id>/edit -> Share
   ```
3. Never makes the sharing call itself.

## Why never "just this once"

Policies that allow exceptions become policies that drift. The
simplest enforceable rule is "no sharing calls, ever, by this
skill". If a different automation needs to change sharing, build a
separate skill with its own audit surface, its own approval gate,
and its own log trail. Don't conflate "publish" and "share".
