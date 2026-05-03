# Interaction Contract

How adk skills must talk to the user when running any non-trivial task. Always read and obey unless the user passes an explicit `--auto` flag at the call site.

> **Canonical text.** This file is shared identically across every adk skill's `references/` folder. The canonical version lives at `plugins/adk-core/skills/auto/references/interaction-contract.md` and is mirrored at build time.

## Default mode: highly interactive with explained options

For every meaningful decision in a workflow:

1. **Restate the decision in one sentence.** No throat-clearing.
2. **Surface 2-3 options.** Not one option dressed as three.
3. **For each option, give the user enough to choose.** Use this exact shape so the chooser can compare apples to apples:
  ```
   ### Option <A | B | C>: <short label>
   - What it does: <one sentence>
   - Pros: <2-3 bullets>
   - Cons: <2-3 bullets>
   - Best when: <one sentence with concrete signal>
   - Blast radius: surgical | bounded | transformative
   - Reversibility: easy | moderate | hard
  ```
4. **Recommend a default** (mark it `(default)`) and say in one sentence why it is the safest pick for the current evidence.
5. **Ask exactly one question at a time.** Never stack 3 unrelated questions in one turn; iterate.
6. **Stop and wait.** Do not start work until the user picks (or passes `--auto`).

## When NOT to ask

- The decision is reversible, low blast radius, and there is one obviously correct answer (e.g. "create the missing `.temp/` folder").
- The user already answered the question earlier in this same session.
- The skill is in `verify` / read-only mode and no destructive action follows.

In those cases, state the choice you are making, why, and continue. Do not invent ceremony.

## Phase 1 dependency preflight

Before the main work of any non-trivial skill, run a dependency preflight and report the result in the status banner.

1. Derive dependencies from the skill frontmatter (`metadata.needs_mcp`, `metadata.needs_meta_info`, modes) and the selected workflow branch.
2. Classify each dependency:
   - **Required now**: the selected mode cannot produce a correct result without it.
   - **Optional capability**: improves accuracy or coverage but is not needed for the selected mode.
   - **Write-only dependency**: only needed for posting, publishing, pushing, resolving, or other remote mutation.
3. Validate required-now dependencies before continuing:
   - CLI tools: `command -v <tool>` plus a lightweight version/auth check when the tool has one.
   - Meta-info: `bin/adk-info <topic> --check` for each required topic.
   - Shipped MCPs in Claude Code: verify the plugin-local `.mcp.json` server is visible/reachable, or use the documented CLI fallback.
   - Claude Desktop and workspace connectors: plugin-local `.mcp.json` files are not loaded by Desktop. If a required MCP or connector is missing, stop and ask the user to configure the named connector/custom MCP in Desktop or their workspace before continuing.
4. Allow an explicit skip only when the user states the capability is not needed for the chosen mode. Example: a dry-run PR review may skip a write-capable PR connector if it will only draft comments and a read path is already available. Never skip a dependency required to gather the primary evidence.
5. Record every skipped, missing, or degraded dependency in the final report with its impact on accuracy, coverage, or ability to mutate remote state.

## `--auto` mode

If the user passes `--auto` (anywhere in the request) the agent:

1. Skips every approval gate.
2. Picks the documented `(default)` option at every decision.
3. Still validates after every meaningful change.
4. Still surfaces a final report (changes, validation evidence, what was decided automatically, what was skipped, residual risk).
5. Refuses any irreversible destructive op that the skill explicitly marks "never auto" (e.g. `pr-merge`, force-push, `rm -rf`, production deploy, schema drop).

## `-i` / `--interactive` mode

- Mutually exclusive with `--auto`.
- Per-phase approval gates.
- Shows the plan; allows the user to edit before execution.

## `--fix` (orthogonal to `--auto` / `-i`)

A skill that supports `--fix` (declared in its frontmatter under `metadata.modes`) auto-applies the skill's own findings, then validates. `--fix` composes with `--auto` and `-i`:

- `--auto --fix` — auto-apply + skip approval gates.
- `-i --fix` — auto-apply + per-phase approval.

Hard rules across all skills:

1. `--fix` only available where mutation is the skill's purpose (`review-pr`, `review-code-changes`, `review-feedback`, `docs-review`, `audit-pr`).
2. Push to a remote branch ALWAYS asks before the first push, even under `--auto --fix`.
3. Posting a comment on a PR is a shared-state action; same rule as push.
4. Merging a PR is NEVER auto. Always asks.
5. Deleting a branch is NEVER auto. Always asks.
6. Force-pushing to `main` / `master` / `develop` / any branch in `~/.config/adk/github.md.forbid_force_push_branches` is BLOCKED, even under `--auto --fix`.

## Approval-gate rules

- Plan before non-trivial change: produce a short plan, ask for approval, then execute.
- Any remote write (git push, PR action, MCP publish, infra command): show the exact command / payload, ask for approval, then run.
- Anything that touches another user's account, billing, or production: always require explicit approval, even under `--auto`.

## Reporting after action

Every skill, in every mode, ends its turn with:

- **Result** — one sentence on what changed.
- **Decisions** — list each branch the skill auto-picked (under `--auto` or because it was trivial) with one-line rationale.
- **Validation** — fresh evidence (command output, screenshots, link checks, etc.). If a check could not run, say so.
- **Residual risk / follow-ups** — bulleted, prioritized.
- **Offer depth** — "Need more detail on any decision?" — never dump long context unprompted.

## Why this contract exists

It makes every skill predictable from the user's side: they either get a guided pick-the-option flow or a full unattended run with documented defaults, never a half-and-half surprise.