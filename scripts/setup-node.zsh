#!/usr/bin/env zsh
set -euo pipefail

# Install Node.js dependencies for AKIT shared utilities

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(dirname "$SCRIPT_DIR")/lib"

if [[ ! -d "$LIB_DIR" ]]; then
  echo "Error: lib/ directory not found at $LIB_DIR"
  exit 1
fi

if ! command -v node &>/dev/null; then
  echo "Error: node is not installed"
  echo "Install Node.js 18+ from https://nodejs.org/"
  exit 1
fi

if ! command -v npm &>/dev/null; then
  echo "Error: npm is not installed"
  exit 1
fi

echo "Installing AKIT Node.js dependencies..."
cd "$LIB_DIR"
npm install --no-fund --no-audit
echo "Done."
