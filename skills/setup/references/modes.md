# `setup` — modes

| Mode | Behavior |
| --- | --- |
| `auto` (default) | Each install step is gated by approval. Best for first run. |
| `fix` | Install everything missing without asking (still respects `--auto` for the entire run). Best for CI / re-provisioning. |
| `review` | Not supported. (`setup` always intends to converge state; review-only would be just `bin/adk-doctor`.) |
