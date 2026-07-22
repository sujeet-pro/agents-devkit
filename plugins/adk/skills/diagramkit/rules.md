# diagramkit — hard rules + refusals + safety

## Diagram rules

1. **Never author from memory.** Engine choice, palettes, readability budgets, config schema, and embed markup come from `node_modules/diagramkit/skills/*` — read and follow the relevant skill. The installed copy tracks the installed version; anything you'd restate here would drift.
2. **Verify the toolchain first.** `npx diagramkit doctor` must pass (diagramkit installed, Chromium warm) before any render. A failing doctor stops the work.
3. **Anchor on the local install.** Always `npx diagramkit …` for this repo; never a global diagramkit and never a different version.
4. **Render + validate every diagram.** A diagram ships only after `diagramkit render` produced its light/dark output and `diagramkit validate` passed (structure, embed-safety, WCAG contrast, light/dark readability). A failing gate stops the phase — fix the cause, never suppress the check.
5. **Sources are the source of truth.** Edit the source, then re-render. Never hand-edit a generated `.svg`.
6. **Validate before you embed.** Only embed a diagram that passed validation, and only via the `<picture>` light/dark pattern the installed skill documents.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — GitHub via the `gh` CLI only, SSH-only clones, no force-push / no merge / no protected-branch writes, no `--no-verify` or destructive git, secrets never in output, read-only until a mutation is explicitly intended. On top of the shared contract, for this skill:

1. **Local files only.** This skill writes diagram sources, rendered SVGs, and embed markup into the working repo and stops. It **never commits, pushes, or publishes** — opening a PR is a separate, gated step (`git` + the `gh` CLI, on a feature branch, after confirmation).
2. **Never overwrite an existing diagram source or content file without confirmation.** A new diagram picks a fresh path; an edit to an existing source or an embed into existing content is confirmed first.
3. **The diagramkit CLI runs locally only.** `doctor` / `skills install` / `render` / `validate` and the headless Chromium they spawn run against this repo's local install — never a remote or global toolchain, never a network publish target.
4. **Fall back honestly, never fabricate a flag.** If `--fail-on` / `--scope-dir` (or `skills install`) aren't in the installed version, use the documented fallback and say so — don't invent CLI surface the installed version doesn't have.

## Refusals

- diagramkit is not installed in the repo → stop; recommend installing it (and, for a Pagesmith site, `/adk:pagesmith`), don't attempt to render.
- `diagramkit doctor` fails (Chromium missing, toolchain broken) → stop with the named gap; don't render into a broken toolchain.
- Asked to embed or ship a diagram that fails `diagramkit validate` (contrast/structure/embed-safety) → refuse; report the failure and fix it first.
- Asked to hand-edit rendered SVG output → refuse; change the source and re-render.
- Asked to commit, push, or publish the output → out of scope; produce the local files and hand off (a PR is the gated `git`/`gh` step).
- The target content is a Pagesmith site needing broader page/config work → produce the diagram + embed snippet and route the rest to `/adk:pagesmith`.
