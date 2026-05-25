# shared/model-depth.md

Model depth and programmatic detail are separate controls:

- `--detailed` means "use more expensive programmatic context building" when a
  skill has such a path. For PR review today, that means the detailed embedding
  model (`bge-m3` by default) and higher-recall retrieval inputs. It does not
  by itself require a stronger chat model.
- `--deep` means "use the stronger reasoning model profile" for the harness
  that is running the skill. A non-detailed PR can still run with `--deep`, and
  a detailed embedding run can stay on the standard model if the task is small.

Harness defaults:

| Harness | Standard | Deep / complex | Planning |
|---|---|---|---|
| Claude Code / Claude CLI | Sonnet | Opus | Sonnet unless `--deep` or the task is complex |
| Cursor | Composer 2.5 (`composer-2.5-fast`) | GPT 5.5 (`gpt-5.5-extra-high`) | GPT 5.5 for planning-heavy or `--deep` runs |
| Codex | Harness default | GPT 5.5 (`gpt-5.5-extra-high`) when selectable | GPT 5.5 when selectable |
| Custom | No model flag unless `--agent-model` is set | No model flag unless `--agent-model` is set | No model flag unless `--agent-model` is set |

Automatic deep selection is allowed for complex work: large PRs, high changed-line
counts, broad cross-module edits, migrations, auth/security/payments/permissions
surfaces, incidents, ambiguous architecture choices, or tasks where the cost of a
miss is high. Prefer Sonnet / Composer 2.5 for narrow, well-scoped work.

When Opus is selected, choose the smallest effort that fits the risk:

- `medium` effort for bounded reviews, single-service investigations, and
  implementation tasks with clear acceptance criteria.
- `high` effort for large PRs, cross-system behavior, security-sensitive changes,
  incident RCAs, or ambiguous design decisions.

Record model-depth choices in the skill's decision log using `fork_id:
model-depth` when the choice is non-trivial.
