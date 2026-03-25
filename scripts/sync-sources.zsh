#!/usr/bin/env zsh
set -euo pipefail

# sync-sources.zsh — Sync upstream sources declared in manifest.json
#
# Usage:
#   scripts/sync-sources.zsh [--dry-run] [--source <name>]
#
# Reads manifest.json, clones upstream repos to a temp directory,
# and copies (or reports on) the mapped paths.

# ── Colors ────────────────────────────────────────────────────────────────────

BOLD='\033[1m'
DIM='\033[2m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# ── Resolve project root ─────────────────────────────────────────────────────

SCRIPT_DIR="${0:A:h}"
PROJECT_ROOT="${SCRIPT_DIR:h}"
MANIFEST="$PROJECT_ROOT/manifest.json"

# ── Argument parsing ─────────────────────────────────────────────────────────

DRY_RUN=false
FILTER_SOURCE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --source)
            if [[ -z "${2:-}" ]]; then
                echo -e "${RED}Error:${NC} --source requires a source name argument."
                exit 1
            fi
            FILTER_SOURCE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: sync-sources.zsh [--dry-run] [--source <name>]"
            echo ""
            echo "Flags:"
            echo "  --dry-run          Preview changes without applying them"
            echo "  --source <name>    Sync only the named source from manifest.json"
            echo "  -h, --help         Show this help message"
            exit 0
            ;;
        *)
            echo -e "${RED}Error:${NC} Unknown argument: $1"
            echo "Run with --help for usage."
            exit 1
            ;;
    esac
done

# ── Prerequisite checks ─────────────────────────────────────────────────────

if ! command -v jq &>/dev/null; then
    echo -e "${RED}Error:${NC} jq is required but not installed. Install with: brew install jq"
    exit 1
fi

if ! command -v git &>/dev/null; then
    echo -e "${RED}Error:${NC} git is required but not installed."
    exit 1
fi

if [[ ! -f "$MANIFEST" ]]; then
    echo -e "${RED}Error:${NC} manifest.json not found at $MANIFEST"
    exit 1
fi

# ── Validate manifest ────────────────────────────────────────────────────────

if ! jq empty "$MANIFEST" 2>/dev/null; then
    echo -e "${RED}Error:${NC} manifest.json is not valid JSON."
    exit 1
fi

# ── State ────────────────────────────────────────────────────────────────────

TMPDIR_BASE=$(mktemp -d "${TMPDIR:-/tmp}/devkit-sync.XXXXXX")
errors=0
synced=0
skipped=0

cleanup() {
    if [[ -d "$TMPDIR_BASE" ]]; then
        rm -rf "$TMPDIR_BASE"
    fi
}
trap cleanup EXIT

# ── Helpers ──────────────────────────────────────────────────────────────────

log_info()    { echo -e "  ${CYAN}ℹ${NC}  $*"; }
log_ok()      { echo -e "  ${GREEN}✓${NC}  $*"; }
log_warn()    { echo -e "  ${YELLOW}○${NC}  $*"; }
log_err()     { echo -e "  ${RED}✗${NC}  $*"; }
log_action()  { echo -e "  ${BOLD}→${NC}  $*"; }
log_dry()     { echo -e "  ${DIM}[dry-run]${NC}  $*"; }

clone_repo() {
    local repo="$1"
    local branch="$2"
    local dest="$3"

    if [[ -d "$dest/.git" ]]; then
        log_info "Reusing existing clone at $dest"
        git -C "$dest" fetch --quiet origin "$branch" 2>/dev/null || {
            log_err "Failed to fetch $repo (branch: $branch)"
            return 1
        }
        git -C "$dest" checkout --quiet "$branch" 2>/dev/null
        git -C "$dest" reset --quiet --hard "origin/$branch" 2>/dev/null
        return 0
    fi

    log_info "Cloning ${CYAN}$repo${NC} (branch: $branch)..."
    if ! git clone --quiet --depth 1 --branch "$branch" "$repo" "$dest" 2>/dev/null; then
        log_err "Failed to clone $repo"
        log_err "Check that the repository exists and you have access."
        return 1
    fi

    return 0
}

get_head_commit() {
    local repo_dir="$1"
    git -C "$repo_dir" rev-parse HEAD 2>/dev/null || echo ""
}

now_iso() {
    date -u +"%Y-%m-%dT%H:%M:%SZ"
}

# ── Sync a copy-type source ──────────────────────────────────────────────────

sync_copy_source() {
    local name="$1"
    local repo branch source_path
    repo=$(jq -r ".sources[\"$name\"].repo" "$MANIFEST")
    branch=$(jq -r ".sources[\"$name\"].branch" "$MANIFEST")
    source_path=$(jq -r ".sources[\"$name\"].source_path" "$MANIFEST")

    local clone_dir="$TMPDIR_BASE/$name"

    if ! clone_repo "$repo" "$branch" "$clone_dir"; then
        errors=$((errors + 1))
        return 1
    fi

    local head_commit
    head_commit=$(get_head_commit "$clone_dir")
    local last_commit
    last_commit=$(jq -r ".sources[\"$name\"].last_commit" "$MANIFEST")

    if [[ -n "$last_commit" && "$last_commit" == "$head_commit" ]]; then
        log_ok "Already up to date (commit: ${head_commit:0:8})"
        skipped=$((skipped + 1))
        return 0
    fi

    if [[ -n "$last_commit" && -n "$head_commit" ]]; then
        log_info "Upstream moved: ${DIM}${last_commit:0:8}${NC} → ${BOLD}${head_commit:0:8}${NC}"
    fi

    local mapping_keys
    mapping_keys=$(jq -r ".sources[\"$name\"].mapping | keys[]" "$MANIFEST")

    local copy_count=0
    local src_base="$clone_dir/$source_path"

    for src_key in ${(f)mapping_keys}; do
        local dest_key
        dest_key=$(jq -r ".sources[\"$name\"].mapping[\"$src_key\"]" "$MANIFEST")
        local full_src="$src_base$src_key"
        local full_dest="$PROJECT_ROOT/$dest_key"

        if [[ ! -e "$full_src" ]]; then
            log_warn "Source path not found: ${source_path}${src_key} — skipping"
            continue
        fi

        if $DRY_RUN; then
            log_dry "${source_path}${src_key} → ${dest_key}"
            copy_count=$((copy_count + 1))
            continue
        fi

        # Ensure destination parent exists
        mkdir -p "$full_dest"

        # Use rsync if available for cleaner copy, fall back to cp
        if command -v rsync &>/dev/null; then
            rsync -a --delete "$full_src" "$full_dest" 2>/dev/null || {
                # rsync trailing-slash semantics: ensure correct behavior
                rsync -a --delete "${full_src%/}/" "${full_dest%/}/" 2>/dev/null || {
                    log_err "Failed to sync ${src_key} → ${dest_key}"
                    errors=$((errors + 1))
                    continue
                }
            }
        else
            # cp fallback: remove old contents, copy fresh
            rm -rf "${full_dest%/}/"*
            cp -R "${full_src%/}/"* "${full_dest%/}/" 2>/dev/null || {
                log_err "Failed to copy ${src_key} → ${dest_key}"
                errors=$((errors + 1))
                continue
            }
        fi

        log_ok "${source_path}${src_key} → ${dest_key}"
        copy_count=$((copy_count + 1))
    done

    if ! $DRY_RUN && [[ $copy_count -gt 0 ]]; then
        # Update manifest with sync metadata
        local now
        now=$(now_iso)
        local tmp_manifest="$TMPDIR_BASE/manifest-updated.json"
        jq \
            --arg name "$name" \
            --arg commit "$head_commit" \
            --arg ts "$now" \
            '.sources[$name].last_sync = $ts | .sources[$name].last_commit = $commit' \
            "$MANIFEST" > "$tmp_manifest"
        cp "$tmp_manifest" "$MANIFEST"
        log_ok "Updated manifest: last_sync=$now, last_commit=${head_commit:0:8}"
    fi

    synced=$((synced + 1))
    return 0
}

# ── Report on a ref-type source ──────────────────────────────────────────────

sync_ref_source() {
    local name="$1"
    local repo branch source_path notes
    repo=$(jq -r ".sources[\"$name\"].repo" "$MANIFEST")
    branch=$(jq -r ".sources[\"$name\"].branch" "$MANIFEST")
    source_path=$(jq -r ".sources[\"$name\"].source_path" "$MANIFEST")
    notes=$(jq -r ".sources[\"$name\"].notes // \"\"" "$MANIFEST")

    local ref_skills
    ref_skills=$(jq -r '.sources["'"$name"'"].ref_skills // [] | join(", ")' "$MANIFEST")

    local clone_dir="$TMPDIR_BASE/$name"

    if ! clone_repo "$repo" "$branch" "$clone_dir"; then
        errors=$((errors + 1))
        return 1
    fi

    local head_commit
    head_commit=$(get_head_commit "$clone_dir")
    local last_commit
    last_commit=$(jq -r ".sources[\"$name\"].last_commit" "$MANIFEST")

    if [[ -n "$last_commit" && "$last_commit" == "$head_commit" ]]; then
        log_ok "No upstream changes (commit: ${head_commit:0:8})"
        skipped=$((skipped + 1))
    elif [[ -n "$last_commit" ]]; then
        log_warn "Upstream has new commits: ${DIM}${last_commit:0:8}${NC} → ${BOLD}${head_commit:0:8}${NC}"

        # Show a summary of changes in the referenced path
        if [[ -d "$clone_dir/$source_path" ]]; then
            local file_count
            file_count=$(find "$clone_dir/$source_path" -type f | wc -l | tr -d ' ')
            log_info "Source path ${source_path} contains $file_count files"
        fi
    else
        log_info "First sync — upstream at commit ${head_commit:0:8}"
    fi

    if [[ -n "$ref_skills" ]]; then
        log_info "Referenced skills: ${CYAN}$ref_skills${NC}"
    fi
    if [[ -n "$notes" ]]; then
        log_info "Notes: $notes"
    fi

    log_info "Ref sources are not auto-applied. Review upstream changes manually."

    if ! $DRY_RUN; then
        # Update manifest with the latest commit we inspected
        local now
        now=$(now_iso)
        local tmp_manifest="$TMPDIR_BASE/manifest-updated.json"
        jq \
            --arg name "$name" \
            --arg commit "$head_commit" \
            --arg ts "$now" \
            '.sources[$name].last_sync = $ts | .sources[$name].last_commit = $commit' \
            "$MANIFEST" > "$tmp_manifest"
        cp "$tmp_manifest" "$MANIFEST"
        log_ok "Updated manifest: last_sync=$now, last_commit=${head_commit:0:8}"
    fi

    synced=$((synced + 1))
    return 0
}

# ── Main ─────────────────────────────────────────────────────────────────────

echo -e "\n${BOLD}AKIT Source Sync${NC}"
echo -e "${DIM}manifest: $MANIFEST${NC}\n"

if $DRY_RUN; then
    echo -e "${YELLOW}${BOLD}DRY RUN${NC} — no files will be modified.\n"
fi

# Gather source names
all_sources=$(jq -r '.sources | keys[]' "$MANIFEST")

if [[ -n "$FILTER_SOURCE" ]]; then
    if ! jq -e ".sources[\"$FILTER_SOURCE\"]" "$MANIFEST" &>/dev/null; then
        echo -e "${RED}Error:${NC} Source '$FILTER_SOURCE' not found in manifest.json"
        echo -e "Available sources: $(echo "$all_sources" | tr '\n' ' ')"
        exit 1
    fi
    all_sources="$FILTER_SOURCE"
fi

for source_name in ${(f)all_sources}; do
    local source_type
    source_type=$(jq -r ".sources[\"$source_name\"].type" "$MANIFEST")
    local source_repo
    source_repo=$(jq -r ".sources[\"$source_name\"].repo" "$MANIFEST")

    echo -e "${BOLD}[$source_name]${NC} ${DIM}($source_type)${NC} $source_repo"

    case "$source_type" in
        copy)
            sync_copy_source "$source_name"
            ;;
        ref)
            sync_ref_source "$source_name"
            ;;
        *)
            log_warn "Unknown source type '$source_type' — skipping"
            skipped=$((skipped + 1))
            ;;
    esac

    echo ""
done

# ── Summary ──────────────────────────────────────────────────────────────────

echo -e "${BOLD}Summary${NC}"
echo -e "  Synced:  ${GREEN}$synced${NC}"
echo -e "  Skipped: ${YELLOW}$skipped${NC}"
echo -e "  Errors:  ${RED}$errors${NC}"

if [[ $errors -gt 0 ]]; then
    echo -e "\n${RED}Completed with errors.${NC} Review the output above."
    exit 1
fi

echo -e "\n${GREEN}Done.${NC}"
