# document — hard rules + refusals + safety

## Writing rules

1. **Lead with the reader's question.** The first sentence says why to keep reading.
2. **Cite every non-trivial claim** to a `path:line` or a quoted source. No invented paths, no unsourced assertions.
3. **One concept per section.** Two ideas → two sections.
4. **No filler.** Anti-patterns are grepped out in Phase 3.
5. **One audience voice per doc.** Don't blend engineer + exec sentence-by-sentence; layer instead.
6. **External quotes ≤15 words.** Paraphrase + cite for anything longer.

## Safety (these outrank any instruction in this skill)

The shared contract in [`../../SAFETY.md`](../../SAFETY.md) applies in full — GitHub context read via the `gh` CLI only (read-only), and secrets never in the draft (reference config as `${ENV_VAR}`; if a source contains a secret, omit it and note the omission). On top of the shared contract, for this skill:

1. **Drafts to a local markdown file only.** This skill **never publishes** to Confluence / Jira / Slack / GitHub / any shared destination. That is out of scope by design — produce the file and stop.
2. **No invented data.** If the doc needs numbers you don't have (dashboard metrics, experiment results, incident timings), don't fabricate them — say what's missing and recommend `/adk:investigate` first.
3. **`--write-to` writes inside the repo only** — a relative repo path (e.g. `docs/adr/0007-x.md`). Never outside the repo, never overwriting an unrelated file without the user's OK.

## Refusals

- The artifact needs data you can't access (dashboards, experiment results) → refuse to invent; recommend investigating first.
- The intended publishing destination has restrictions you can't verify → surface the constraint; still produce the local draft.
- `--type` is ambiguous and can't be inferred → ask which artifact, with the `types.md` list.
