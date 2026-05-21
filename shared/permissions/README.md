# adk permissions

Single source of truth for tool-call permission policies across the agents
adk installs into (Claude Code, Cursor, Codex, Junie).

Goal: **allow all safe / read-only tool calls automatically, prompt the user
only for dangerous or destructive actions.**

Files in this folder:

| File | Target | Mechanism |
|---|---|---|
| `claude.json` | `~/.claude/settings.json` `permissions.{allow,ask,deny,defaultMode}` | JSON union-merge (bookkept under `_adkManagedPermissions`) |
| `cursor.json` | `~/.cursor/cli-config.json` `permissions`, `approvalMode`, `sandbox` | JSON union-merge (bookkept under `_adkManagedPermissions`) |
| `codex.toml`  | `~/.codex/config.toml` `approval_policy`, `sandbox_mode` | Marker block (`# adk-permissions-marker:start` / `:end`) |
| `junie-allowlist.json` | `~/.junie/allowlist.json` | Whole-file write, guarded by `"_adk_managed": true` |

## How it's applied

The installer (`install.py`) calls these merge functions inside each
`install_<agent>` step:

- `merge_permissions_into_claude`
- `merge_permissions_into_cursor`
- `merge_permissions_into_codex`
- `merge_permissions_into_junie`

Behaviour:

- If the target settings file does not exist, it is created.
- If it exists, only the keys we manage are touched. User-added entries
  are preserved (list-valued keys are union-merged; scalar keys back up
  the previous value before overwriting).
- Re-running `./install.sh` is idempotent — adk-managed entries that were
  removed from these template files since the last run are dropped on the
  next install via the `_adkManagedPermissions` bookkeeping block.

## How it's reverted

`./install.sh --uninstall` calls `strip_permissions_from_*`:

- Claude / Cursor: removes only the entries we added, restores any backed-up
  scalar (`defaultMode`, `approvalMode`, `sandbox.mode`, …), and drops the
  bookkeeping key.
- Codex: strips the `# adk-permissions-marker:start` … `:end` block.
- Junie: deletes `~/.junie/allowlist.json` **only if** it still carries the
  `"_adk_managed": true` marker. User-edited allowlists are left alone.

## Editing the policy

Edit the files in this folder and re-run `./install.sh` to push changes to
every supported agent. To exclude a specific entry on a specific machine,
remove it from the relevant config file here or rebuild the entry list in
your `~/.agents-devkit/config/core.yaml (+ repos.md + connectors/*.md)` (planned).

## Safety notes

- The Claude `defaultMode` is set to `"default"` (not `"bypassPermissions"`):
  even with our wide `allow` list, Claude still prompts on anything not
  explicitly allowed and on everything in `ask`.
- Cursor `approvalMode` is `"auto"` and the sandbox is `"workspace-write"`:
  anything outside the workspace or anything that fails the sandbox
  triggers a prompt.
- Codex uses `approval_policy = "on-request"` with `sandbox_mode =
  "workspace-write"`: writes outside the workspace and network access
  require explicit approval.
- Junie inherits its own `allowReadonlyCommands: true` plus our explicit
  `ask` rules for dangerous prefixes (`rm`, `git push`, `terraform
  apply`, …); everything else falls through to a final allow-all pattern.
