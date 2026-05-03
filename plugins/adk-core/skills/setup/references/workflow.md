# `setup` workflow

## Step 1 — platform detection

```bash
case "$(uname -s)" in
  Darwin) PLATFORM=darwin ;;
  Linux)  PLATFORM=linux ;;
  *)      echo "Unsupported platform"; exit 1 ;;
esac
```

## Step 2 — CLI dependencies

For each tool in `references/tool-list.md`:

```bash
if command -v <tool> >/dev/null 2>&1; then
  version=$(<tool> --version 2>&1 | head -1)
  echo "  - <tool>     present ($version)"
else
  echo "  - <tool>     MISSING — run: <install-cmd>"
fi
```

Install commands:

| Tool | macOS | Linux |
| --- | --- | --- |
| `gh` | `brew install gh` | `sudo apt install gh` (or vendor instructions) |
| `jq` | `brew install jq` | `sudo apt install jq` |
| `fd` | `brew install fd` | `sudo apt install fd-find` |
| `ripgrep` | `brew install ripgrep` | `sudo apt install ripgrep` |
| `fzf` | `brew install fzf` | `sudo apt install fzf` |
| `node` | `brew install node` | `sudo apt install nodejs` (or use nvm) |
| `docker` | `brew install --cask docker` | `sudo apt install docker.io` |

## Step 3 — `gh auth`

```bash
gh auth status
# If not authed: prompt user to run `gh auth login`
```

## Step 4 — meta-info topics

Walk topics in dependency order: `info` → `repos` → `github` → `datadog` → `mixpanel` → `statsig` → `snowflake` → `slack` → `review` → `docs`.

For each topic (or just `--target <topic>`):

1. If `~/.config/adk/<topic>.md` doesn't exist:
   ```bash
   mkdir -p ~/.config/adk
   cp "${CLAUDE_PLUGIN_ROOT}/skills/setup/templates/<topic>.md" ~/.config/adk/<topic>.md
   ```
2. Open in editor:
   ```bash
   editor=$(adk-info info default_editor 2>/dev/null | tr -d '"' || echo "${EDITOR:-nvim}")
   "$editor" ~/.config/adk/<topic>.md
   ```
3. Validate:
   ```bash
   if ! adk-info <topic> --check; then
     echo "Validation failed; re-opening for fixes."
     # loop back to step 2
   fi
   ```
4. Confirm with user that the populated file looks right (skip under `--auto`).

## Step 5 — env-var check

For each `plugins/<plugin>/.mcp.json`, parse `${VAR}` placeholders:

```bash
present=()
missing=()
for var in $(jq -r '..|strings? | scan("\\$\\{([A-Za-z_][A-Za-z0-9_]*)\\}") | .[0]' plugins/*/.mcp.json | sort -u); do
  if [[ -n "${!var-}" ]]; then
    present+=("$var")
  else
    missing+=("$var")
  fi
done
```

Print:
- For each present: `  - VAR    present`.
- For each missing: `  - VAR    MISSING — add to ~/.zshenv: export VAR="..."` (with vendor-specific URL hint).

## Step 6 — report

Aggregate everything into the report shape from `references/output-format.md`. Under `--auto`, also write `.temp/setup-report.md`.
