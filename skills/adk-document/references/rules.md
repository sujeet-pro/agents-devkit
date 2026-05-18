# adk-document — hard rules + refusals

## Hard rules

1. Lead with the user's question. First sentence = why the reader keeps reading.
2. Cite every non-trivial claim. "The code does X" → `path:line`.
3. No filler phrases. Anti-pattern grep enforced at Phase 3.
4. External quotes ≤15 words. Paraphrase + link for more.
5. Match audience: engineer / pm / exec / mixed. Don't mix voices.
6. **Never publish** — markdown stays local. `/adk-sync` publishes.

## Refusals

- Required source data missing (RCA without incident, experiment-report without Statsig data) → refuse; suggest `/adk-investigate` first.
- Publication destination requested in args (`--to confluence`) → refuse; route to `/adk-sync`.
- `--type` unrecognized → ask user to pick from catalog OR map to a similar type.
- Source URL fetch failed → refuse; surface the gap.
