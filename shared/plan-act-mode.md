# shared/plan-act-mode.md — plan vs act mode separation

> Inspired by Cline's plan/act modes. Provides tool-level enforcement of the planning vs execution split. Used by `/adk-implement` and `/adk-review --fix`.

## The two modes

| Mode | Allowed tools | Forbidden | Use case |
|---|---|---|---|
| `--plan` | `Read`, `Grep`, `Glob`, `WebFetch`, `Agent` (Explore only) | `Edit`, `Write`, `Bash` (except read-only commands) | Investigate the repo + design the change. Produce `<task-slug>/plan.md`. |
| `--act` | Full toolset per `SKILL.md.allowed-tools` | — | Apply the plan. Edit files, run commands, push. |
| (default — no flag) | Plan-then-act in one run | — | Skills internally pause at the Plan→Act boundary, present the plan, wait for user OK, then proceed. |

## Why a hard mode (not just prose)

Advisor.md instructs the agent to "plan first." But the agent has Edit tools available — it can (and does) silently start editing mid-plan, undermining the advisor strategy. With `--plan`:

- `Edit` and `Write` are not in the tool list. The agent literally cannot mutate.
- `Bash` is forbidden EXCEPT for these read-only forms: `git status`, `git log`, `git diff`, `git show`, `git rev-parse`, `gh pr view`, `gh pr diff`, `gh issue view`, `gh api` (GET), `python3 scripts/adk_*.py --check|--json`, `python3 scripts/url_classifier.py`.
- The agent must finish with a written plan and stop. No "and also let me just fix this one thing".

## How to invoke

```text
/adk-implement <input> --plan         # planning only; produces plan.md, no edits
/adk-implement <input> --act          # assumes plan.md exists; applies it
/adk-implement <input>                # default — plan then act, with confirm gate

/adk-review <pr-url> --plan           # produces a written findings list, no posting / fixing
/adk-review <pr-url> --fix --plan     # produces a fix-plan; no edits yet
/adk-review <pr-url> --fix --act      # applies the planned fixes
/adk-review <pr-url> --fix            # default — both, with confirm gate before act
```

## Plan output

When `--plan` runs, the skill writes a structured plan to `<repo>/.temp/<task-slug>/plan.md`. The next `--act` invocation reads it from there.

```markdown
# plan: <task-slug>
mode: plan
generated: 2026-05-18T14:22Z

## goal
<one sentence>

## scope
in: [...]
out: [...]

## approach
<chosen option, with rationale>

## changes-by-file (preview of SEARCH/REPLACE blocks)
- path/a.py: <one-line summary of what changes>
- path/b.ts: <…>

## risks
- <risk>: <mitigation>

## validators to run (in --act)
- typecheck (npm run typecheck)
- lint (eslint <changed>)
- tests (vitest <affected>)

## rollback
<one sentence>
```

## Resuming Act from a prior Plan

```text
/adk-implement --act --from-plan .temp/implement-SF-1234/plan.md
```

If the plan is older than 24h OR the repo has had commits since the plan was generated, the Act step asks: "the plan is stale; re-plan or proceed?"

## What this prevents

- Silent file mutations during the "planning" phase.
- Skipping the user-confirm gate by claiming "I'll just do a quick fix while explaining."
- Cost spike from invoking opus for read-only planning when sonnet would do.

## Cost optimization

Plan mode is a great candidate for sonnet (planning is reasoning, not high-context generation). Skills SHOULD declare `metadata.model: opus` for `--act` and override to `sonnet` for `--plan` invocations. (This is enforced by `agents-claude/agents/adk-agent-implementer.md` reading a `mode` env var; future agents will follow the same pattern.)

## Integration with question-first

- `--plan` mode includes the question-first phase as normal.
- `--act` mode skips question-first IF a plan.md exists AND the user explicitly said "go" / "proceed" / "apply this plan". Otherwise re-asks the highest-impact 1-2 questions.
