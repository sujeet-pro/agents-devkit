# adk-implement — fork IDs

Each fork is a decision point the skill logs to `~/.agents-devkit/improve/learning/decisions.jsonl`. `/adk-improve` reads these to propose defaults for `~/.agents-devkit/config/core.yaml.defaults.adk-implement.<fork_id>`.

| fork_id | options | first-time recommendation |
|---|---|---|
| `scope` | vertical-slice / full / spike | vertical-slice (challenge to "smallest ship today") |
| `approach` | from previous sub-flow's options | from `references/<sub-flow>.md` |
| `test-framework` | repo-detected (jest / vitest / pytest / go test / cargo test / …) | repo-detected; pick existing over installing new |
| `pr-strategy` | single / split-by-area / draft-first | single unless >800 LOC changed |
| `commit-style` | conventional / semantic-release / freeform | repo-detected from `git log -10` style |
| `linter-tolerance` | strict / warn-allowed / autofix-only | strict on changed code |
| `breaking-change-policy` | block / require-migration-note / require-flag | block unless flag-gated |
| `mode` | plan / act / plan-then-act | plan-then-act |
| `dispatch-override` | none / `<chosen-sub-flow>` | none (classifier wins) |
