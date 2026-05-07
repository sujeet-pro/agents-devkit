# `config-update` — anti-patterns

- **Bootstrapping a missing file.** That's `setup`'s job. If `~/.config/adk/<topic>.md` is absent, redirect to `/adk-core:setup --target <topic>` and stop.
- **Auto-deleting a user-added entry.** The user wrote it on purpose. Removals are *proposed*, never executed without explicit consent — even under `--auto --fix`.
- **Treating the source as ground truth.** Datadog has zombie dashboards; Statsig has half-finished experiments; Mixpanel has misnamed events. The code cross-reference is the truth-check.
- **Dumping every active experiment / dashboard / event.** Filter aggressively. A `common_*` entry should be something the user actually uses — top by hit-count, code-referenced, recent.
- **Resolving `${ENV_VAR}` placeholders during the rewrite.** Turns the file into a secret store. Always preserve the literal placeholder.
- **Rewriting the `# Notes` body.** Front-matter only. The body is the user's prose.
- **Auto-renaming `service_aliases` even when confidence is high.** Renames break downstream queries. Flag and ask.
- **Mutating the source.** No `Update_Gate_Entirely`, no `upsert_datadog_dashboard`, no `gh repo create`. This skill is read-only against external systems.
- **Writing a raw secret.** Same regex check as setup — refuse if the proposed file contains `github_pat_`, `sk-`, `xox[bp]-`, etc.
- **Skipping the post-write `--check`.** Always validate after writing; restore the original on failure.
- **Stacking 5 confirmations in one turn.** One topic at a time. The interaction contract applies.
- **Running when the *current* file is invalid.** `bin/adk-info <topic> --check` must pass before the skill proposes changes — otherwise the diff is meaningless.
- **Auto-cloning a missing repo.** `repos.md` adds may include uncloned repos; flag the missing path, don't `gh repo clone` for the user.
- **Touching `info.md`, `slack.md`, `review.md`, `docs.md`.** Out of scope. The skill lists them as "not refreshable" and moves on.
- **Backing up the original to disk.** In-memory backup only. The skill's blast radius is bounded to `~/.config/adk/`; it does NOT scatter `.bak` files around.
- **Performing a code grep for every source item in series.** The grep across every configured repo path can be slow; the skill should fan out grep operations per (item, repo) pair where it can.
