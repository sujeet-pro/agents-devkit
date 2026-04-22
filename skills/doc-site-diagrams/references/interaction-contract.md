# Interaction Contract

How agents must talk to the user when running any ADK skill (or any
non-trivial task) on this machine. Always read and obey unless the user
passes an explicit `--auto` flag at the call site.

## Default mode: highly interactive with explained options

For every meaningful decision in a workflow:

1. **Restate the decision in one sentence.** No throat-clearing.
2. **Surface 2-3 options.** Not one option dressed as three.
3. **For each option, give the user enough to choose.** Use this exact
  shape so the chooser can compare apples to apples:
4. **Recommend a default** (mark it `(default)`) and say in one sentence
  why it is the safest pick for the current evidence.
5. **Ask exactly one question at a time.** Never stack 3 unrelated
  questions in one turn; iterate.
6. **Stop and wait.** Do not start work until the user picks (or passes
  `--auto`).

## When NOT to ask

- The decision is reversible, low blast radius, and there is one
obviously correct answer (e.g. "create the missing `.temp/` folder").
- The user already answered the question earlier in this same session.
- The skill is in `verify` / read-only mode and no destructive action
follows.

In those cases, state the choice you are making, why, and continue. Do
not invent ceremony.

## `--auto` mode

If the user passes `--auto` (anywhere in the request) the agent:

1. Skips every approval gate.
2. Picks the documented `(default)` option at every decision.
3. Still validates after every meaningful change.
4. Still surfaces a final report (changes, validation evidence, what
  was decided automatically, what was skipped, residual risk).
5. Refuses any irreversible destructive op that the skill explicitly
  marks "never auto" (e.g. `pr-merge`, force-push, `rm -rf`,
   production deploy, schema drop).

## `--mode` (orthogonal to `--auto`)

A skill that supports modes (declared in its frontmatter under
`metadata.modes`) accepts:

- `--mode auto` — default. Brainstorm + plan + execute end-to-end.
- `--mode review` — produce findings only. Write a `review.md` artifact
or post comments. Never edits source code.
- `--mode fix` — auto-apply the skill's own findings, then validate.

Mode is set per skill invocation. `--auto` and `--mode` compose:
`--mode fix --auto` runs the skill end-to-end including auto-fixes
without approval gates.

## Approval-gate rules

- Plan before non-trivial change: produce a short plan, ask for
approval, then execute.
- Any remote write (git push, PR action, MCP publish, infra command):
show the exact command / payload, ask for approval, then run.
- Anything that touches another user's account, billing, or production:
always require explicit approval, even under `--auto`.

## Reporting after action

Every skill, in every mode, ends its turn with:

- **Result** — one sentence on what changed.
- **Decisions** — list each branch the skill auto-picked (under `--auto`
or because it was trivial) with one-line rationale.
- **Validation** — fresh evidence (command output, screenshots, link
checks, etc.). If a check could not run, say so.
- **Residual risk / follow-ups** — bulleted, prioritized.
- **Offer depth** — "Need more detail on any decision?" — never dump
long context unprompted.

## Why

This contract makes every skill predictable from the user's side: they
either get a guided pick-the-option flow or a full unattended run with
documented defaults, never a half-and-half surprise.