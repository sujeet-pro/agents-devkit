# scaffold-pagesmith-docs — hard rules + refusals + safety

## Scaffold rules

1. **Detect before you write.** Inspect the target dir — git repo, `package.json`, existing `pagesmith.config.*` or a non-empty docs tree — before touching anything.
2. **Never scaffold over an existing `pagesmith.config.*` without explicit confirmation.** An existing config means an existing site: stop, name the file you found, and get a per-invocation OK before overwriting. Absent that, route the user to `/adk:pagesmith` (the existing-site skill).
3. **Package tooling owns the schema.** Follow the installed `pagesmith-docs-setup` skill for the config and the deploy workflow; never hand-author config the skill would generate.
4. **Delegate every version-sensitive detail to `node_modules`.** No Pagesmith config keys, no diagramkit engine names, no palette restated from memory — read and follow the installed skill. If this skill and the installed skill disagree, the installed skill wins.
5. **Prefer the idempotent CLI.** Materialize stubs with `npx pagesmith skills install` / `npx diagramkit skills install`; only fall back to the setup skill's by-hand materialization when the CLI subcommand is unavailable, and say so.
6. **End previewable, not deployed.** Finish on a green build plus a smoke-checked dev server. A failing validator stops the run; don't report "done" over a red gate.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — GitHub access via the `gh` CLI only, SSH-only clones, no force-push / no merge / no protected-branch writes, no `--no-verify` or destructive git, secrets never in output, read-only until a write is intended and confirmed. On top of the shared contract, for this skill:

1. **Never deploy, push, or open a PR.** This skill scaffolds locally and *configures* a deploy target; the deploy command is printed for a human to run. Publishing the site is out of scope by design.
2. **Confirm before any destructive write** — overwriting an existing `pagesmith.config.*`, a non-empty docs directory, or a file the scaffold did not create. Fresh writes into an empty target proceed; clobbering existing work is gated.
3. **New dependencies are named, not smuggled.** `@pagesmith/docs`, `diagramkit` (and `@pagesmith/core` + `@pagesmith/site` for `core-native`) are the expected installs — state them before running `npm install`; surface anything else the setup skill wants to add.
4. **`--dry-run` writes nothing** — it prints the plan and exits after Phase 1.

## Refusals

- **An existing `pagesmith.config.*` (or a populated docs tree) with no overwrite confirmation** → refuse to clobber; recommend `/adk:pagesmith` for the existing site.
- **Target isn't a git repo and the deploy target is `gh-pages`** → surface the gap; offer to `git init` or continue with `--deploy none`.
- **A requested `--engine` isn't one diagramkit ships** → don't guess; the installed `diagramkit-auto` skill names the supported engines — surface that list rather than restating it here.
- **A deploy target other than GitHub Pages** → configure only what the installed deploy skill supports; surface anything unsupported instead of hand-rolling it.
- **The `skills install` CLI and the setup-skill fallback are both unavailable** → stop with the named gap; don't hand-fabricate stubs from memory.
- **Bitbucket / GitLab / other-forge clone URL** → out of scope; this toolkit clones GitHub over SSH only (`../../SAFETY.md`).
