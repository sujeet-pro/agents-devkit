#!/usr/bin/env zsh
set -euo pipefail

# Generate Google Drive MCP OAuth credentials file from GOOGLE_MCP_CLIENT_ID
# and GOOGLE_MCP_CLIENT_SECRET, then run browser-based auth to obtain tokens.
#
# Prerequisites:
#   export GOOGLE_MCP_CLIENT_ID="your-client-id.apps.googleusercontent.com"
#   export GOOGLE_MCP_CLIENT_SECRET="GOCSPX-..."
#
# Usage: setup-google-drive.zsh [--credentials-only]
#   --credentials-only: Generate the credentials file but skip browser auth

CREDENTIALS_DIR="$HOME/.config/google-drive-mcp"
CREDENTIALS_FILE="$CREDENTIALS_DIR/gcp-oauth.keys.json"
CREDENTIALS_ONLY=false

for arg in "$@"; do
  case "$arg" in
    --credentials-only) CREDENTIALS_ONLY=true ;;
  esac
done

# Check required env vars
if [[ -z "${GOOGLE_MCP_CLIENT_ID:-}" ]]; then
  echo "Error: GOOGLE_MCP_CLIENT_ID is not set." >&2
  echo "Add to ~/.zshenv: export GOOGLE_MCP_CLIENT_ID=\"your-client-id\"" >&2
  exit 1
fi

if [[ -z "${GOOGLE_MCP_CLIENT_SECRET:-}" ]]; then
  echo "Error: GOOGLE_MCP_CLIENT_SECRET is not set." >&2
  echo "Add to ~/.zshenv: export GOOGLE_MCP_CLIENT_SECRET=\"your-secret\"" >&2
  exit 1
fi

# Generate credentials file
mkdir -p "$CREDENTIALS_DIR"

jq -n \
  --arg client_id "$GOOGLE_MCP_CLIENT_ID" \
  --arg client_secret "$GOOGLE_MCP_CLIENT_SECRET" \
  '{
    "installed": {
      "client_id": $client_id,
      "client_secret": $client_secret,
      "redirect_uris": ["http://localhost"],
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token"
    }
  }' > "$CREDENTIALS_FILE"

chmod 600 "$CREDENTIALS_FILE"
echo "Generated credentials file: $CREDENTIALS_FILE"

if [[ "$CREDENTIALS_ONLY" == "true" ]]; then
  echo ""
  echo "Credentials file created. To complete auth, run:"
  echo "  npx @piotr-agier/google-drive-mcp auth"
  exit 0
fi

# Run browser-based OAuth to obtain tokens
echo ""
echo "Starting browser-based OAuth flow..."
echo "A browser window will open. Sign in with your Google account and grant access."
echo ""

GOOGLE_DRIVE_OAUTH_CREDENTIALS="$CREDENTIALS_FILE" npx @piotr-agier/google-drive-mcp auth

echo ""
echo "Google Drive MCP setup complete."
echo ""
echo "Ensure these are in your ~/.zshenv:"
echo "  export GOOGLE_MCP_CLIENT_ID=\"$GOOGLE_MCP_CLIENT_ID\""
echo "  export GOOGLE_MCP_CLIENT_SECRET=\"\$GOOGLE_MCP_CLIENT_SECRET\""
echo "  export GOOGLE_DRIVE_OAUTH_CREDENTIALS=\"$CREDENTIALS_FILE\""
echo ""
echo "Then re-run 'zsh install.zsh' to configure the MCP server."
