# pagesmith — hard rules + refusals + safety

## Build rules

1. **Detect the flavor first.** `pagesmith.config.json5` → docs-preset; `site.config.json5` → core-native; neither → greenfield (out of scope). Route on the file, not a guess.
2. **Delegate the deep task** to the installed skill — read and follow `node_modules/<pkg>/skills/<name>/SKILL.md`, which points at the version-matched `node_modules/<pkg>/REFERENCE.md` / schemas. The installed files outrank training data.
3. **Never restate version-sensitive package knowledge** — config schema, nav/meta keys, theme tokens, page frontmatter fields, search options, CLI flags — from memory. Read them from the installed skill + `node_modules/<pkg>/REFERENCE.md` every time.
4. **Read before write; match the site.** Copy the conventions already in the site over any personal preference.
5. **Regenerate, don't hand-hack.** Generated output (`dist/`, the search index) is produced by the build — never edit it by hand to pass a check.
6. **Validate with the repo's own scripts** (from `package.json`), never assumed commands. A red gate stops the work.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — GitHub via the `gh` CLI only, SSH-only clones, no force-push / no merge / no protected-branch writes, no `--no-verify` or destructive git, secrets never in output, and read-only by default (this skill writes only after a plan is confirmed, and confirms before any deploy/push). On top of the shared contract, for this skill:

1. **Writes are scoped to the site's own content + config** — the flavor's config file, the content directories, and theme/override files. Never edit files under `node_modules/` (the installed package source), and never hand-edit generated output (`dist/`, the search index) — regenerate via the repo's build.
2. **Deploy is gated and gh-pages-only via the repo's own path.** Run the repo's GitHub Actions workflow or its deploy script; any `git push` / `gh pr create` is confirmed against the named branch first, never force, never to a protected branch. A non-GitHub-Pages deploy target is out of scope for the deploy step (`Refusals`).
3. **Version fidelity is a safety rule.** Do not restate or guess a package's schema/frontmatter/flags from memory, and do not bump the installed `@pagesmith/*` or `diagramkit` version to match a remembered API — work against what's installed and recommend an upgrade separately.
4. **Materialize, don't fabricate.** If the package skills aren't present, run `npx pagesmith skills install` / `npx diagramkit skills install`, or follow `node_modules/<pkg>/skills/<pkg>-setup/SKILL.md`. If neither is available, stop with the named gap — never invent the missing skill's steps.

## Refusals

- No `pagesmith.config.json5` and no `site.config.json5` (greenfield) → this skill maintains an *existing* site; route to `/adk:scaffold-pagesmith-docs`.
- The task is authoring or repairing diagrams → route to `/adk:diagramkit`.
- The matched `node_modules` skill can't be found or materialized (package not installed; both the CLI subcommand and the setup-skill fallback unavailable) → stop with the named gap; don't guess the schema.
- Build/validate keeps failing after the planned retries → stop and report; never ship a red build or hand-patch generated output.
- The requested deploy target isn't GitHub Pages / isn't the `gh` CLI path → out of scope for the deploy step; produce the built site and hand off.
- Bitbucket / GitLab / other-forge hosting → GitHub only, per `../../SAFETY.md`.
