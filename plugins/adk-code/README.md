# adk-code

> Code authoring for the `adk` marketplace. One verb per skill: write, fix, refactor, migrate, test, perf, API, security. All skills follow the universal `--auto` / `-i` mode contract from `/adk-core:auto` and write working artifacts to `.temp/task-<slug>/`.

## What it ships


| Component       | What                                                                                                                |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| **Skills (8)**  | `code-write`, `code-bugfix`, `code-refactor`, `code-migrate`, `code-test`, `code-perf`, `code-api`, `code-security` |
| **Agents (2)**  | `implementer`, `test-engineer`                                                                                      |
| **Hooks**       | None — relies on the `PreToolUse:Bash` safety hook from `adk-core`.                                                 |
| **Bin scripts** | None — uses `adk-info`, `adk-task-slug`, `adk-mcp-health` from `adk-core`.                                          |
| **MCP servers** | None shipped. Mutation goes through the `Edit` / `Write` / `Bash` built-ins.                                        |


`adk-code` depends on `adk-core` and is designed to be invoked through `/adk-core:auto`'s dispatcher, but every skill also runs Phase 0 prompt expansion on its own input so direct invocation works the same way.

## Skills

### `code-write` — implement a feature

Read repo conventions first. Plan the smallest correct change in `plan.md`. Touch the minimum number of files. Validate with the repo's own typecheck / lint / tests. No drive-by refactors. No defensive code for impossible cases.

```text
/adk-code:code-write "add a --since flag to the export CLI"
/adk-code:code-write "wire the new pricing rule into the cart calculator"
/adk-code:code-write "build the export-to-csv feature for the dashboard" --auto
```

### `code-bugfix` — fix a bug with a reproducer + regression test

Reproducer first. Root cause stated in one sentence. Smallest correct patch. Regression test that fails on the buggy commit and passes on the fix. Full suite green before claim of done.

```text
/adk-code:code-bugfix "checkout returns 500 when cart total is exactly 0"
/adk-code:code-bugfix "login flow rejects valid emails containing +" -i
```

### `code-refactor` — restructure without changing behavior

Tests stay green between every micro-step. Public API surface is untouched (that is `code-api`). Behavior changes are forbidden in the same diff as a structural change.

```text
/adk-code:code-refactor "extract the rate-limit logic into its own module"
/adk-code:code-refactor "rename getCwd to getCurrentWorkingDirectory across the repo"
```

### `code-migrate` — major-version bumps and tool replacements

WebFetches the upstream migration guide. Inventories call-sites per breaking change. Groups changes so each group can be reviewed independently. Validates between groups.

```text
/adk-code:code-migrate "React 18 to 19"
/adk-code:code-migrate "Spring Boot 2 to 3 in checkout-api"
/adk-code:code-migrate "Jest to Vitest" --scope packages/web
```

### `code-test` — author or expand tests

Tests are evidence. Each test is named after the behavior it asserts, fails first, then is committed. Covers happy path + at least one boundary + at least one error per behavior. No vacuous coverage.

```text
/adk-code:code-test "backfill tests for the order-state machine"
/adk-code:code-test "raise coverage on the discount calculator" --unit
/adk-code:code-test "convert the manual smoke checks for /api/orders into integration tests" --integration
```

### `code-perf` — diagnose and fix a performance regression

Measure first, fix second. Bottleneck identified with quoted profiler / trace evidence. Re-measurement proves the win. Adds a guardrail (perf test, CI budget, DD monitor) so the regression cannot silently recur.

```text
/adk-code:code-perf "checkout API p99 jumped from 250ms to 1.2s after Tuesday's deploy"
/adk-code:code-perf "hit p99 < 500ms on /api/products" --budget p99=500ms
```

### `code-api` — design or evolve a contract

Contract-first. Hyrum's-Law-aware (every observable behavior becomes someone's depended-on contract). One canonical version with documented deprecation policy. Validation lives at the boundary; internal callers are trusted.

```text
/adk-code:code-api "design the v2 endpoint set for /orders"
/adk-code:code-api "evolve the SDK export surface for the @acme/checkout package" --breaking
```

### `code-security` — implement a security-hardening change

Defense-in-depth, but boundary-first. Every mitigation has a documented threat. Every fix has a regression test (malicious input → 400, not 500 or 200). Runs the security-reviewer agent (from `adk-review`) over the diff before claim of done.

```text
/adk-code:code-security "fix CVE-2025-XXXXX in the @acme/auth package"
/adk-code:code-security "add input validation on the new /api/upload endpoint"
/adk-code:code-security "tighten CORS on the public storefront API" --scope apps/store
```

## Agents


| Agent           | Persona                                                                                                                                    | Used by                                                                                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `implementer`   | Smallest correct change. No drive-by cleanup. Match repo conventions. Read before write. Trust internal code; validate at boundaries only. | `code-write`, `code-bugfix` (patch step), `code-refactor`, `code-migrate`, `code-perf` (the fix step), `code-api` (reference impl), `code-security` (the mitigation step) |
| `test-engineer` | Tests are evidence. Fail-first, then green. Behavior-named tests, not function-named. Cover happy path + boundary + error.                 | `code-test`, `code-bugfix` (regression-test step)                                                                                                                         |


Both agents are thin: they hold persona + hard rules; the workflow lives in the SKILL.md of whichever skill spawned them.

## Composition with `adk-core:auto`

Every `code-*` skill is registered with `disable-model-invocation: false`, so `adk-core:auto` can auto-route a free-form prompt directly. The router uses the `When to use` and `Common prompts` sections in each SKILL.md to pick.

The standard chain in practice:

1. `**/adk-core:auto**` (Phase 0–3) restates the prompt, resolves `<repo>` against `~/.config/adk/repos.md`, and proposes a skill chain.
2. `**/adk-code:<skill>**` (Phase 0–6) runs the actual change. Phase 0 still prompt-expands its own input so the skill can be called directly.
3. `**/adk-review:review-code-changes**` is the conventional follow-up before push (called by `/adk-core:auto` when the chain implies "before push" / "self review").

`/adk-code:*` skills NEVER push, commit, or open a PR. They stop with a
validated working tree; the operator then uses `docs-commit-message`,
`docs-pr-description`, and explicit `git` / `gh` commands when ready.

## Mode contract

All skills support:

- `--auto` (default) — end-to-end with no per-phase approval gate. Still stops before destructive shared-state actions (none of the `code-*` skills do those — they only touch the local working tree).
- `-i` / `--interactive` — per-phase approval. Mutually exclusive with `--auto`.

`code-*` skills do **not** support `--fix`. Mutation IS the goal of every skill in this plugin, so `--fix` is meaningless here. The `--fix` flag is reserved for `adk-review:`* and `adk-docs:docs-review`, where mutation is opt-in on top of a default read-only flow.

The full canonical interaction contract lives at `[plugins/adk-core/skills/auto/references/interaction-contract.md](../adk-core/skills/auto/references/interaction-contract.md)` and is mirrored byte-identical into every `code-*` skill's `references/interaction-contract.md` so the skill brings it into context when activated. Read the canonical version once; the mirrors exist for the load-on-activation system.

## Working artifacts

Every skill writes to `.temp/task-<slug>/` (gitignored) per `/adk-core:temp-folder`:

```
.temp/task-<slug>/
├── prompt.txt              # verbatim user prompt + ISO timestamp
├── plan.md                 # skill's plan (files-touched, approach, validation plan)
├── (skill-specific)
│   ├── migration-notes.md  # code-migrate
│   ├── measurement.md      # code-perf (before/after)
│   ├── design.md           # code-api
│   ├── threat-model.md     # code-security
│   └── reproducer.md       # code-bugfix
├── validation/
│   └── per-skill/<skill>.md
└── report.md               # final report (what changed, evidence, residual risk)
```

The slug is generated by `bin/adk-task-slug` from the prompt nouns/verbs (kebab-case, max 6 words).

## Meta-info consumed


| Skill           | `~/.config/adk/*.md` topics read |
| --------------- | -------------------------------- |
| `code-write`    | `info`, `repos`                  |
| `code-bugfix`   | `info`, `repos`                  |
| `code-refactor` | `repos`                          |
| `code-migrate`  | `repos`                          |
| `code-test`     | `repos`                          |
| `code-perf`     | `repos`, `datadog`               |
| `code-api`      | `repos`                          |
| `code-security` | `repos`                          |


If a required topic is missing, the skill stops and offers to call `/adk-core:setup --target <topic>`.

## Installation

```text
/plugin install adk-code@adk
/reload-plugins
/adk-core:setup    # one-time, populates ~/.config/adk/*.md
```

Every other adk plugin install also pulls `adk-core` since it is declared as a dependency.

## Repo layout

```
adk-code/
├── .claude-plugin/plugin.json
├── README.md                       # this file
├── agents/
│   ├── implementer.md
│   └── test-engineer.md
└── skills/
    ├── code-write/{SKILL.md, references/*.md}
    ├── code-bugfix/{SKILL.md, references/*.md}
    ├── code-refactor/{SKILL.md, references/*.md}
    ├── code-migrate/{SKILL.md, references/*.md}
    ├── code-test/{SKILL.md, references/*.md}
    ├── code-perf/{SKILL.md, references/*.md}
    ├── code-api/{SKILL.md, references/*.md}
    └── code-security/{SKILL.md, references/*.md}
```

