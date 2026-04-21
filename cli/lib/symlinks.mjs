// Idempotent symlink helpers.
//
// The contract:
//   1. Before adding new links into a target directory, scan it and remove
//      every symlink that currently points inside this repo (REPO_DIR).
//   2. Then create the requested links.
//
// This means re-running the installer always converges target dirs to exactly
// the current selection — additions, removals, and renames all propagate.

import {
  existsSync,
  lstatSync,
  mkdirSync,
  readdirSync,
  readlinkSync,
  symlinkSync,
  unlinkSync,
} from "node:fs";
import { dirname, join, resolve } from "node:path";

export function isLink(p) {
  try {
    return lstatSync(p).isSymbolicLink();
  } catch {
    return false;
  }
}

export function readLinkAbs(p) {
  const target = readlinkSync(p);
  if (target.startsWith("/")) return target;
  return resolve(dirname(p), target);
}

/**
 * Make a predicate that matches symlinks pointing inside any of the given
 * absolute root directories.
 */
export function pointsInsideAny(roots) {
  const normalized = roots.filter(Boolean).map((r) => r.replace(/\/$/, ""));
  return (linkPath) => {
    let target;
    try {
      target = readLinkAbs(linkPath);
    } catch {
      return false;
    }
    for (const root of normalized) {
      if (target === root || target.startsWith(root + "/")) return true;
    }
    return false;
  };
}

export function pointsInsideRepo(linkPath, repoDir) {
  return pointsInsideAny([repoDir])(linkPath);
}

/**
 * Remove every symlink in `dir` for which `predicate(linkPath)` is truthy.
 * Returns the list of removed paths.
 */
export function pruneLinks(dir, predicate, { dryRun = false, log = () => {} } = {}) {
  const removed = [];
  if (!existsSync(dir)) return removed;
  let entries;
  try {
    entries = readdirSync(dir);
  } catch {
    return removed;
  }
  for (const name of entries) {
    const full = join(dir, name);
    if (!isLink(full)) continue;
    if (!predicate(full)) continue;
    if (dryRun) {
      log(`[dry-run] prune ${full}`);
    } else {
      try {
        unlinkSync(full);
        log(`pruned ${full}`);
      } catch (err) {
        log(`prune-failed ${full} (${err.message})`);
        continue;
      }
    }
    removed.push(full);
  }
  return removed;
}

/** Backwards-compat helper: prune every link in `dir` pointing into `repoDir`. */
export function pruneRepoLinks(dir, repoDir, opts) {
  return pruneLinks(dir, pointsInsideAny([repoDir]), opts);
}

/**
 * Remove a single managed file symlink if it matches `predicate`.
 */
export function pruneLink(file, predicate, { dryRun = false, log = () => {} } = {}) {
  if (!isLink(file)) return false;
  if (!predicate(file)) return false;
  if (dryRun) {
    log(`[dry-run] prune ${file}`);
    return true;
  }
  try {
    unlinkSync(file);
    log(`pruned ${file}`);
    return true;
  } catch (err) {
    log(`prune-failed ${file} (${err.message})`);
    return false;
  }
}

/** Backwards-compat helper: prune `file` if it points into `repoDir`. */
export function pruneRepoLink(file, repoDir, opts) {
  return pruneLink(file, pointsInsideAny([repoDir]), opts);
}

/**
 * Ensure a symlink at `linkPath` points to `target`.
 *
 * - If `linkPath` already exists as a non-symlink, skip and report.
 * - If it is a symlink with the same target:
 *     - When `force` is true, delete + recreate it. This bumps the link's
 *       ctime/mtime, which is useful for invalidating caches kept by
 *       agent runtimes (e.g. Claude indexes skill metadata once per session
 *       and decides "fresh" by stat). Re-creating ensures the live file
 *       (which the symlink already points at) is treated as new.
 *     - Otherwise, leave it alone.
 * - If it is a symlink to a *different* target:
 *     - When `allowForeignReplace` is true, replace it.
 *     - Otherwise, refuse and skip (avoids silently clobbering a user's
 *       dot-files-managed symlink, e.g. ~/.claude/settings.json).
 */
export function ensureSymlink(
  target,
  linkPath,
  { dryRun = false, log = () => {}, force = false, allowForeignReplace = true } = {},
) {
  if (!existsSync(target)) {
    log(`skip-missing-source ${target}`);
    return { status: "skipped", reason: "source-missing" };
  }
  if (existsSync(linkPath) && !isLink(linkPath)) {
    log(`skip-non-symlink ${linkPath}`);
    return { status: "skipped", reason: "non-symlink" };
  }
  if (isLink(linkPath)) {
    let existing = null;
    try {
      existing = readLinkAbs(linkPath);
    } catch {
      /* fall through to replace */
    }
    if (existing === target) {
      if (!force) return { status: "ok", reason: "already-linked" };
      // force-recreate to bump ctime for cache busters.
      if (dryRun) {
        log(`[dry-run] refresh ${linkPath} -> ${target}`);
        return { status: "would-link", reason: "refresh" };
      }
      try {
        unlinkSync(linkPath);
      } catch (err) {
        log(`refresh-failed ${linkPath} (${err.message})`);
        return { status: "error", reason: err.message };
      }
    } else {
      if (!allowForeignReplace) {
        log(`skip-foreign-symlink ${linkPath} -> ${existing ?? "?"}`);
        return { status: "skipped", reason: "foreign-symlink" };
      }
      if (dryRun) {
        log(`[dry-run] replace ${linkPath} -> ${target}`);
        return { status: "would-link", reason: "replace" };
      }
      try {
        unlinkSync(linkPath);
      } catch (err) {
        log(`replace-failed ${linkPath} (${err.message})`);
        return { status: "error", reason: err.message };
      }
    }
  }
  if (dryRun) {
    log(`[dry-run] link ${linkPath} -> ${target}`);
    return { status: "would-link", reason: "create" };
  }
  try {
    mkdirSync(dirname(linkPath), { recursive: true });
    symlinkSync(target, linkPath);
    log(`linked ${linkPath} -> ${target}`);
    return { status: "ok", reason: "created" };
  } catch (err) {
    log(`link-failed ${linkPath} (${err.message})`);
    return { status: "error", reason: err.message };
  }
}
