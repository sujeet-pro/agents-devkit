# Script Review Guidelines

These guidelines apply to **scripts** -- shell scripts (Bash, Zsh), JavaScript/Node.js
scripts, and Python scripts used for automation, CI/CD, deployment, data processing,
and development tooling. They supplement the general guidelines with rules specific
to writing reliable, portable, and maintainable scripts.

---

## 1. Error Handling

### Shell Scripts (Bash)
- **Always start with `set -euo pipefail`**:
  - `set -e`: Exit immediately on any command failure
  - `set -u`: Treat unset variables as errors
  - `set -o pipefail`: Pipe fails if any command in the pipeline fails (not just
    the last one)
  ```bash
  #!/usr/bin/env bash
  set -euo pipefail
  ```
- **Use `trap` for cleanup**:
  ```bash
  cleanup() {
    rm -f "$TEMP_FILE"
    echo "Cleaned up temporary files"
  }
  trap cleanup EXIT
  ```
- **Check command existence** before using it:
  ```bash
  if ! command -v jq &>/dev/null; then
    echo "Error: jq is required but not installed. Install with: brew install jq" >&2
    exit 1
  fi
  ```
- **Validate required environment variables early**:
  ```bash
  : "${API_KEY:?Error: API_KEY environment variable is required}"
  : "${DEPLOY_ENV:?Error: DEPLOY_ENV must be set to staging or production}"
  ```
- **Handle errors explicitly** for critical operations:
  ```bash
  if ! curl -sf "$API_URL/health"; then
    echo "Error: API health check failed at $API_URL" >&2
    exit 1
  fi
  ```

### Node.js Scripts
- **Use `process.exit(1)`** for failure. Never let a script exit with code 0 when
  it failed.
- **Wrap main logic in a try/catch**:
  ```js
  async function main() {
    // script logic
  }
  main().catch((err) => {
    console.error('Fatal error:', err.message);
    process.exit(1);
  });
  ```
- **Handle signals**:
  ```js
  process.on('SIGINT', () => { cleanup(); process.exit(130); });
  process.on('SIGTERM', () => { cleanup(); process.exit(143); });
  ```

### Python Scripts
- **Use `sys.exit(1)`** for failure:
  ```python
  def main() -> int:
      try:
          # script logic
          return 0
      except Exception as e:
          print(f"Error: {e}", file=sys.stderr)
          return 1

  if __name__ == "__main__":
      sys.exit(main())
  ```
- **Use `argparse`** for argument parsing (not manual `sys.argv` parsing).

## 2. Idempotency

- **Scripts must be safe to run multiple times.** Running the same script twice
  should produce the same result without errors or side effects.
- **Check before creating**:
  ```bash
  # Good: idempotent
  mkdir -p "$OUTPUT_DIR"
  # Bad: fails if directory exists
  mkdir "$OUTPUT_DIR"
  ```
- **Use `CREATE IF NOT EXISTS`** for database scripts.
- **Guard file operations**:
  ```bash
  # Good: only download if not already present
  if [[ ! -f "$CACHE_DIR/data.json" ]]; then
    curl -o "$CACHE_DIR/data.json" "$DATA_URL"
  fi
  ```
- **Use atomic operations** when possible:
  ```bash
  # Good: write to temp file, then move (atomic rename)
  curl -o "$OUTPUT_FILE.tmp" "$URL"
  mv "$OUTPUT_FILE.tmp" "$OUTPUT_FILE"

  # Bad: partial write on failure leaves corrupt file
  curl -o "$OUTPUT_FILE" "$URL"
  ```
- **For deployment scripts**: Implement checks that detect the current state and
  only apply changes needed to reach the desired state.

## 3. Input Validation

- **Validate all arguments** before executing the main logic:
  ```bash
  if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <environment> [--dry-run]" >&2
    exit 1
  fi

  ENVIRONMENT="$1"
  if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
    echo "Error: environment must be 'staging' or 'production', got '$ENVIRONMENT'" >&2
    exit 1
  fi
  ```
- **Validate file paths** before operating on them:
  ```bash
  if [[ ! -f "$INPUT_FILE" ]]; then
    echo "Error: input file not found: $INPUT_FILE" >&2
    exit 1
  fi
  ```
- **Sanitize user input** that will be used in commands, SQL, or file paths:
  ```bash
  # Validate that input is a simple identifier (no special chars)
  if [[ ! "$TABLE_NAME" =~ ^[a-zA-Z_][a-zA-Z0-9_]*$ ]]; then
    echo "Error: invalid table name: $TABLE_NAME" >&2
    exit 1
  fi
  ```
- **Use `--` to separate options from arguments** when passing user input to
  commands:
  ```bash
  grep -- "$SEARCH_TERM" "$FILE"
  ```

## 4. Logging and Output

- **Distinguish stdout and stderr**:
  - `stdout`: Script output (data, results) that may be piped to other commands
  - `stderr`: Progress messages, warnings, errors, and debug information
  ```bash
  echo "Processing file: $FILE" >&2    # progress to stderr
  echo "$RESULT"                        # output to stdout
  ```
- **Use consistent log formatting**:
  ```bash
  log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >&2; }
  log_error() { echo "[ERROR] $*" >&2; }
  log_warn() { echo "[WARN] $*" >&2; }

  log "Starting deployment to $ENVIRONMENT"
  log_error "Failed to connect to database"
  ```
- **Support `--verbose` / `--quiet` flags** for controlling output level:
  ```bash
  VERBOSE=false
  debug() { [[ "$VERBOSE" == true ]] && echo "[DEBUG] $*" >&2; }
  ```
- **Show progress for long-running operations**:
  ```bash
  total=${#FILES[@]}
  for i in "${!FILES[@]}"; do
    echo "Processing [$((i+1))/$total]: ${FILES[$i]}" >&2
    process_file "${FILES[$i]}"
  done
  ```
- **Print a summary at the end**:
  ```bash
  echo "Done. Processed $PROCESSED files, $ERRORS errors, $SKIPPED skipped." >&2
  ```

## 5. Documentation

- **Every script must have a header comment** explaining:
  - What the script does (one paragraph)
  - Usage/syntax with examples
  - Required environment variables
  - Prerequisites (tools, permissions)
  ```bash
  #!/usr/bin/env bash
  # deploy.sh -- Deploy the application to a target environment.
  #
  # Usage:
  #   ./deploy.sh <environment> [--dry-run] [--skip-tests]
  #
  # Arguments:
  #   environment     Target environment (staging, production)
  #
  # Options:
  #   --dry-run       Show what would be done without making changes
  #   --skip-tests    Skip running tests before deployment
  #
  # Environment variables:
  #   DEPLOY_TOKEN    (required) Authentication token for deployment
  #   SLACK_WEBHOOK   (optional) Slack webhook URL for notifications
  #
  # Prerequisites:
  #   - kubectl configured for the target cluster
  #   - Docker logged in to the container registry
  #
  # Examples:
  #   ./deploy.sh staging
  #   ./deploy.sh production --dry-run
  ```
- **Support `--help`** and show usage information when invoked without arguments
  or with `--help` / `-h`.
- **Comment non-obvious logic**: Shell scripts are inherently less readable than
  application code. Comment anything that is not immediately obvious.
  ```bash
  # Strip ANSI color codes from output before logging
  CLEAN_OUTPUT=$(echo "$OUTPUT" | sed 's/\x1b\[[0-9;]*m//g')
  ```

## 6. Exit Codes

- **Use meaningful exit codes**:
  - `0`: Success
  - `1`: General error
  - `2`: Usage/argument error
  - `126`: Command found but not executable
  - `127`: Command not found
  - `130`: Interrupted by Ctrl+C (SIGINT)
  - `143`: Terminated by SIGTERM
- **Document exit codes** in the script header if the script uses custom codes.
- **Exit with non-zero on failure.** Never let a script succeed silently when it
  failed. With `set -e`, most failures are caught automatically, but also verify
  exit codes for critical operations.
- **Propagate exit codes** from subcommands when appropriate:
  ```bash
  some_command
  exit_code=$?
  if [[ $exit_code -ne 0 ]]; then
    log_error "some_command failed with exit code $exit_code"
    exit $exit_code
  fi
  ```

## 7. Signal Handling

- **Handle SIGTERM and SIGINT** for graceful shutdown:
  ```bash
  SHUTDOWN=false
  handle_signal() {
    echo "Received signal, shutting down gracefully..." >&2
    SHUTDOWN=true
  }
  trap handle_signal SIGINT SIGTERM

  for item in "${ITEMS[@]}"; do
    if [[ "$SHUTDOWN" == true ]]; then
      echo "Shutdown requested, stopping after $PROCESSED items" >&2
      break
    fi
    process_item "$item"
    PROCESSED=$((PROCESSED + 1))
  done
  ```
- **Clean up temporary files** on exit:
  ```bash
  TEMP_DIR=$(mktemp -d)
  trap 'rm -rf "$TEMP_DIR"' EXIT
  ```
- **Do not trap EXIT and SIGINT separately** unless you need different behavior.
  EXIT is triggered on all exits (including signal handlers), so it is usually
  sufficient for cleanup.

## 8. Portability (macOS + Linux)

- **Use `#!/usr/bin/env bash`** instead of `#!/bin/bash` for the shebang. The
  former works on systems where Bash is not at `/bin/bash` (e.g., NixOS, Homebrew
  on macOS).
- **Avoid Bash-specific features when possible.** If the script must be portable
  to `sh`, avoid arrays, `[[ ]]`, `$(())`, `<<<`, `<()`, and associative arrays.
  If Bash features are needed, document the Bash requirement.
- **macOS vs Linux differences**:
  - `sed -i`: macOS requires `sed -i ''`, Linux uses `sed -i`. Use
    `sed -i.bak` and delete the backup, or detect the OS.
  - `date`: macOS `date` does not support `--date`. Use `date -v` on macOS or
    install GNU coreutils.
  - `readlink -f`: Not available on macOS by default. Use `realpath` (from
    coreutils) or a portable alternative.
  - `grep -P` (Perl regex): Not available on macOS. Use `grep -E` for extended
    regex.
- **Detect the OS** when behavior must differ:
  ```bash
  OS="$(uname -s)"
  case "$OS" in
    Darwin) SED_INPLACE=(sed -i '') ;;
    Linux)  SED_INPLACE=(sed -i) ;;
    *)      echo "Unsupported OS: $OS" >&2; exit 1 ;;
  esac
  ```
- **Test on both macOS and Linux** (CI should run on both).

## 9. Security

- **Never use `eval`** on user input or external data. There is almost always a
  safer alternative.
  ```bash
  # Dangerous
  eval "$USER_COMMAND"

  # Safe alternative: use arrays for dynamic commands
  CMD=("$BINARY" "--flag" "$ARG")
  "${CMD[@]}"
  ```
- **Quote all variable expansions** to prevent word splitting and globbing:
  ```bash
  # Good
  cp "$SOURCE_FILE" "$DEST_DIR/"
  # Bad (breaks on paths with spaces)
  cp $SOURCE_FILE $DEST_DIR/
  ```
- **Use arrays for command arguments** instead of building command strings:
  ```bash
  # Good
  CURL_ARGS=(-s -H "Authorization: Bearer $TOKEN" "$API_URL")
  curl "${CURL_ARGS[@]}"

  # Bad
  CURL_CMD="curl -s -H 'Authorization: Bearer $TOKEN' $API_URL"
  $CURL_CMD  # word splitting nightmare
  ```
- **Validate URLs, file paths, and identifiers** before using them in commands.
- **Use `mktemp` for temporary files** instead of hardcoded paths:
  ```bash
  TEMP_FILE=$(mktemp)
  ```
- **Set restrictive permissions** on files containing sensitive data:
  ```bash
  umask 077
  echo "$SECRET" > "$CONFIG_FILE"
  ```
- **Do not store secrets in script files.** Read them from environment variables,
  files (with proper permissions), or a secrets manager.
- **Use HTTPS** for all URL fetches. Never download scripts or data over HTTP.

## 10. Dependency Checking

- **Check for required tools at the start** of the script:
  ```bash
  REQUIRED_TOOLS=(curl jq aws docker)
  MISSING=()
  for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &>/dev/null; then
      MISSING+=("$tool")
    fi
  done
  if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "Error: missing required tools: ${MISSING[*]}" >&2
    echo "Install with: brew install ${MISSING[*]}" >&2
    exit 1
  fi
  ```
- **Check tool versions** when the script requires specific features:
  ```bash
  REQUIRED_NODE_VERSION="18"
  ACTUAL_NODE_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
  if [[ "$ACTUAL_NODE_VERSION" -lt "$REQUIRED_NODE_VERSION" ]]; then
    echo "Error: Node.js $REQUIRED_NODE_VERSION+ required, found $(node -v)" >&2
    exit 1
  fi
  ```
- **Document installation instructions** for non-standard dependencies in the
  script header or a README.
- **Prefer widely available tools.** Use `curl` over `wget`, `jq` for JSON
  processing, `sed`/`awk` for text processing. Avoid obscure or platform-specific
  tools when a common alternative exists.
- **For CI scripts**: Do not assume tools are pre-installed. Either check for them
  or install them as part of the script (with caching for performance).
