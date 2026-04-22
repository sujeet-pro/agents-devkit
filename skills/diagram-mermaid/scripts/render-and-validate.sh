#!/usr/bin/env bash
# render-and-validate.sh — generate SVGs and validate them with diagramkit.
#
# Usage:
#   render-and-validate.sh <file-or-dir> [extra diagramkit render flags...]
#
# Examples:
#   render-and-validate.sh diagrams/architecture.mermaid
#   render-and-validate.sh docs/ --format svg,png --scale 2
#   render-and-validate.sh diagrams/ --theme light
#
# Behaviour:
#   1. Ensures `diagramkit` is on the PATH (globally installed).
#      If missing, prompts for permission, then runs:
#        npm install -g diagramkit@${DIAGRAMKIT_VERSION}
#   2. Runs `diagramkit warmup` once (idempotent — skipped if Chromium is
#      already installed). Skip with --no-warmup.
#   3. Runs `diagramkit render <target> --force --json` and prints the
#      result envelope so callers / agents can parse failures.
#   4. Runs `diagramkit validate <target> --recursive --json` against the
#      same target and prints the result envelope.
#   5. Exits non-zero (1) if either step reports a failure, or any
#      validation issue with severity == "error", LOW_CONTRAST_TEXT,
#      ASPECT_RATIO_EXTREME, or SVG_VIEWBOX_TOO_WIDE survives.
#
# Env vars:
#   DIAGRAMKIT_VERSION  Pinned diagramkit version. Default: 0.3.3
#   AUTO_YES            When set to 1, skips the interactive install prompt.
#   SKIP_WARMUP         When set to 1, skips `diagramkit warmup`.
#
# Exit codes:
#   0 — render and validate clean
#   1 — render or validate surfaced blocking issues
#   2 — install was declined or failed
#   3 — usage / invalid arguments

set -euo pipefail

DIAGRAMKIT_VERSION="${DIAGRAMKIT_VERSION:-0.3.3}"
AUTO_YES="${AUTO_YES:-0}"
SKIP_WARMUP="${SKIP_WARMUP:-0}"

err()  { printf 'ERROR: %s\n' "$*" >&2; }
info() { printf '%s\n' "$*" >&2; }

if [[ $# -lt 1 ]]; then
  err "usage: $0 <file-or-dir> [extra diagramkit render flags...]"
  exit 3
fi

TARGET="$1"; shift
if [[ ! -e "$TARGET" ]]; then
  err "target does not exist: $TARGET"
  exit 3
fi

ensure_diagramkit() {
  if command -v diagramkit >/dev/null 2>&1; then
    local installed_version
    installed_version="$(diagramkit --version 2>/dev/null | head -n1 | tr -d 'v ' || echo unknown)"
    info "[diagram] using diagramkit v${installed_version} ($(command -v diagramkit))"
    if [[ "$installed_version" != "$DIAGRAMKIT_VERSION" && "$installed_version" != "unknown" ]]; then
      info "[diagram] WARNING: installed v${installed_version}, this skill is pinned to v${DIAGRAMKIT_VERSION}."
      info "[diagram] Re-install pinned version with: npm install -g diagramkit@${DIAGRAMKIT_VERSION}"
    fi
    return 0
  fi

  info "[diagram] diagramkit is not installed globally."
  info "[diagram] This skill needs: npm install -g diagramkit@${DIAGRAMKIT_VERSION}"

  local reply
  if [[ "$AUTO_YES" == "1" ]]; then
    reply="y"
  else
    if [[ ! -t 0 ]]; then
      err "non-interactive shell and AUTO_YES != 1 — refuse to install diagramkit silently."
      err "either re-run with AUTO_YES=1, or install manually: npm install -g diagramkit@${DIAGRAMKIT_VERSION}"
      exit 2
    fi
    printf '[diagram] install diagramkit@%s globally now? [y/N] ' "$DIAGRAMKIT_VERSION" >&2
    read -r reply
  fi

  case "$reply" in
    y|Y|yes|YES)
      info "[diagram] installing diagramkit@${DIAGRAMKIT_VERSION}…"
      if ! npm install -g "diagramkit@${DIAGRAMKIT_VERSION}"; then
        err "global install failed."
        exit 2
      fi
      ;;
    *)
      err "user declined install. exiting."
      exit 2
      ;;
  esac
}

ensure_warmup() {
  if [[ "$SKIP_WARMUP" == "1" ]]; then return 0; fi
  # Fast: warmup is idempotent and cheap when Chromium is already present.
  diagramkit warmup >/dev/null 2>&1 || {
    info "[diagram] warmup failed once; retrying with verbose output…"
    diagramkit warmup
  }
}

ensure_diagramkit
ensure_warmup

WORK_DIR="${WORK_DIR:-$(mktemp -d -t diagram-render.XXXXXX)}"
mkdir -p "$WORK_DIR"
RENDER_JSON="$WORK_DIR/render.json"
VALIDATE_JSON="$WORK_DIR/validate.json"

info "[diagram] render: diagramkit render \"$TARGET\" --force --json $*"
if ! diagramkit render "$TARGET" --force --json "$@" > "$RENDER_JSON"; then
  err "diagramkit render exited non-zero. JSON envelope:"
  cat "$RENDER_JSON" >&2 || true
  exit 1
fi
cat "$RENDER_JSON"

# Determine validate target — if user passed a file, validate the sibling .diagramkit/
# folder if present, otherwise validate recursively from the directory.
if [[ -d "$TARGET" ]]; then
  VAL_TARGET="$TARGET"
else
  PARENT_DIR="$(dirname "$TARGET")"
  if [[ -d "$PARENT_DIR/.diagramkit" ]]; then
    VAL_TARGET="$PARENT_DIR/.diagramkit"
  else
    VAL_TARGET="$PARENT_DIR"
  fi
fi

info "[diagram] validate: diagramkit validate \"$VAL_TARGET\" --recursive --json"
if ! diagramkit validate "$VAL_TARGET" --recursive --json > "$VALIDATE_JSON"; then
  err "diagramkit validate exited non-zero. JSON envelope:"
  cat "$VALIDATE_JSON" >&2 || true
  exit 1
fi
cat "$VALIDATE_JSON"

# Lightweight result inspection: fail when any blocking issue remains.
# Uses node since diagramkit already requires it.
node --input-type=module - "$RENDER_JSON" "$VALIDATE_JSON" <<'NODE'
import { readFileSync } from 'node:fs';
const [renderPath, validatePath] = process.argv.slice(2);
const blocking = new Set(['LOW_CONTRAST_TEXT', 'ASPECT_RATIO_EXTREME', 'SVG_VIEWBOX_TOO_WIDE']);
let bad = 0;
try {
  const r = JSON.parse(readFileSync(renderPath, 'utf8'));
  if (Array.isArray(r?.failed) && r.failed.length) {
    process.stderr.write(`[diagram] render failed for ${r.failed.length} source(s)\n`);
    bad += r.failed.length;
  }
} catch (e) {
  process.stderr.write(`[diagram] could not parse render JSON: ${e.message}\n`);
  bad += 1;
}
try {
  const v = JSON.parse(readFileSync(validatePath, 'utf8'));
  const files = Array.isArray(v) ? v : (v.files || v.results || []);
  for (const f of files) {
    for (const issue of f.issues || []) {
      if (issue.severity === 'error' || blocking.has(issue.code)) {
        process.stderr.write(`[diagram] ${f.path || '<?>'}: ${issue.code} (${issue.severity}) — ${issue.message || ''}\n`);
        bad += 1;
      }
    }
  }
} catch (e) {
  process.stderr.write(`[diagram] could not parse validate JSON: ${e.message}\n`);
  bad += 1;
}
if (bad > 0) {
  process.stderr.write(`[diagram] FAILED — ${bad} blocking issue(s). Apply fixes per the SKILL.md and re-run.\n`);
  process.exit(1);
}
process.stderr.write('[diagram] OK — render and validate are clean.\n');
NODE
