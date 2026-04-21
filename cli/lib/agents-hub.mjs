// The `.agents/skills/` hub: single source of truth for all skills.
//
// Two-stage sync owned by this module:
//
//   Stage A (syncHub):
//     Sync the hub itself against the npm package's `skills/adk-*`.
//
//     - Prune every symlink in the hub whose target lives inside any
//       previously-known package install path (current REPO_DIR plus any
//       paths persisted in `~/.config/adk/settings.json5`). User-created
//       skills (plain dirs) and symlinks to other locations are left
//       untouched.
//     - Re-create one symlink per chosen adk-* skill from the package.
//
//   Stage B (mirrorHubInto):
//     Sync a runtime's skills mirror dir against the hub.
//
//     - Prune every symlink in the mirror dir whose target lives inside
//       the hub.
//     - Re-create one symlink per current hub entry (adk-* + user skills).

import { existsSync, mkdirSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

import {
  ensureSymlink,
  pointsInsideAny,
  pruneLinks,
} from "./symlinks.mjs";

/** List the package's public skills (`<packageDir>/skills/adk-*`). */
export function discoverPackageSkills(packageDir) {
  const dir = join(packageDir, "skills");
  if (!existsSync(dir)) return [];
  let names;
  try {
    names = readdirSync(dir);
  } catch {
    return [];
  }
  return names
    .filter((n) => (n === "adk" || n.startsWith("adk-")) && !n.startsWith("."))
    .map((n) => ({ name: n, path: join(dir, n) }))
    .filter((s) => {
      try {
        return statSync(s.path).isDirectory() && existsSync(join(s.path, "SKILL.md"));
      } catch {
        return false;
      }
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * List every entry currently sitting in the hub. Includes both package-managed
 * symlinks and user-created plain directories.
 */
export function listHubEntries(hubDir) {
  if (!existsSync(hubDir)) return [];
  let names;
  try {
    names = readdirSync(hubDir);
  } catch {
    return [];
  }
  return names
    .filter((n) => !n.startsWith("."))
    .map((n) => {
      const full = join(hubDir, n);
      let isDir = false;
      try {
        isDir = statSync(full).isDirectory();
      } catch {
        return null;
      }
      if (!isDir) return null;
      const skillFile = join(full, "SKILL.md");
      if (!existsSync(skillFile)) return null;
      return { name: n, path: full };
    })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));
}

/**
 * Stage A. Sync the hub against package-supplied skills.
 *
 * @param {Object} opts
 * @param {string} opts.hubDir
 * @param {string} opts.packageDir          The current install location.
 * @param {string[]} opts.knownPackagePaths Past install locations to also use as prune filters.
 * @param {{name: string, path: string}[]} opts.selectedSkills Skills from `discoverPackageSkills` we want linked.
 * @param {boolean} [opts.dryRun]
 * @param {(msg: string) => void} [opts.log]
 */
export function syncHub({
  hubDir,
  packageDir,
  knownPackagePaths,
  selectedSkills,
  dryRun = false,
  log = () => {},
  force = false,
}) {
  if (!hubDir) return { skipped: true, reason: "no-hub" };
  const allRoots = unique([packageDir, ...(knownPackagePaths ?? [])]);
  const ours = pointsInsideAny(allRoots);

  const pruned = pruneLinks(hubDir, ours, { dryRun, log });

  if (!dryRun) mkdirSync(hubDir, { recursive: true });

  const created = [];
  const skipped = [];
  for (const skill of selectedSkills) {
    const linkPath = join(hubDir, skill.name);
    const result = ensureSymlink(skill.path, linkPath, { dryRun, log, force });
    if (result.status === "ok" || result.status === "would-link") created.push(skill.name);
    else skipped.push({ name: skill.name, reason: result.reason });
  }
  return { hubDir, pruned: pruned.length, created, skipped };
}

/**
 * Stage B. Mirror the hub into a runtime's skills directory.
 */
export function mirrorHubInto({
  hubDir,
  mirrorDir,
  selectedNames,
  dryRun = false,
  log = () => {},
  force = false,
}) {
  if (!mirrorDir || !hubDir) return { skipped: true, reason: "no-target" };

  const ours = pointsInsideAny([hubDir]);
  const pruned = pruneLinks(mirrorDir, ours, { dryRun, log });

  if (!dryRun) mkdirSync(mirrorDir, { recursive: true });

  const created = [];
  const skipped = [];
  const all = listHubEntries(hubDir);
  const wanted = selectedNames ? all.filter((e) => selectedNames.includes(e.name)) : all;

  for (const entry of wanted) {
    const linkPath = join(mirrorDir, entry.name);
    const result = ensureSymlink(entry.path, linkPath, { dryRun, log, force });
    if (result.status === "ok" || result.status === "would-link") created.push(entry.name);
    else skipped.push({ name: entry.name, reason: result.reason });
  }
  return { mirrorDir, pruned: pruned.length, created, skipped };
}

function unique(items) {
  const seen = new Set();
  const out = [];
  for (const item of items) {
    if (!item) continue;
    if (seen.has(item)) continue;
    seen.add(item);
    out.push(item);
  }
  return out;
}
