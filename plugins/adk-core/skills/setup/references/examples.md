# `setup` — examples

## Example 1 — first run on a fresh laptop

```text
/adk-core:setup
```

**Phase 1:** platform = darwin.

**Phase 2:** all 7 CLI tools missing.

```
[adk-core:setup] platform=darwin
CLI tools:
- brew         MISSING — install: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
- gh           MISSING — install: brew install gh
- jq           MISSING — install: brew install jq
- ...
```

User runs the brew installer; re-runs `setup`.

**Phase 2 (round 2):** brew present; remaining tools printed with install commands.

User runs `brew install gh jq fd ripgrep fzf node && brew install --cask docker`; re-runs `setup`.

**Phase 3:** `gh auth status` says NOT authed.

```
gh             present, NOT authed — run: gh auth login
```

User runs `gh auth login`.

**Phase 4:** for each topic: copies template, opens in `$EDITOR`, validates.

User fills `info.md` (name, email), `repos.md` (3 repos), `datadog.md` (site + service aliases). Skips others for now.

**Phase 5:** env-var report — `GITHUB_PAT` and `DD_API_KEY` present (from earlier shell config); `DD_APP_KEY` and `STATSIG_CONSOLE_API_KEY` missing.

**Phase 6:** final report. 2 warnings (missing env vars).

User adds the exports to `~/.zshenv`, restarts Claude Code.

---

## Example 2 — adding Mixpanel later

```text
/adk-core:setup --target mixpanel
```

**Phase 4 only:** copies `templates/mixpanel.md` to `~/.config/adk/mixpanel.md`, opens for editing. User fills `project_id` and `common_events`. Validation passes.

**Phase 5:** prints env-var status for `MIXPANEL_PROJECT_TOKEN` if referenced by any plugin.

**Phase 6:** one-line report — "mixpanel meta-info ready".

---

## Example 3 — repeat run, everything OK

```text
/adk-core:setup --auto
```

**All phases run silently except for the final report:**

```
[adk-core:setup] platform=darwin target=all mode=auto
CLI tools: 7/7 present
meta-info: 10/10 present, valid
env vars: 7/7 present
mcp servers: 3/3 ready
doctor: 0 warnings, 0 errors
```

No questions asked; nothing changed.

---

## Example 4 — meta-info fix triggered by a skill error

User runs `/adk-investigate:investigate-datadog "p99 on checkout"`. Skill fails:

```
ERROR: ~/.config/adk/datadog.md missing required field: site.
       Run: /adk-core:setup --target datadog
```

User runs `/adk-core:setup --target datadog`. Setup opens the file in `$EDITOR`, user fills `site: datadoghq.com`, validation passes, skill rerun succeeds.
