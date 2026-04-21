// Write a small `MANIFEST.json` into the .agents/skills hub at the end of
// every install. It captures *what is currently live*: the source package
// path, package version, git HEAD (when the source is a git checkout), an
// install timestamp, and the list of skill names linked into the hub.
//
// The manifest serves three purposes:
//   1. Humans can `cat ~/.agents/skills/MANIFEST.json` to confirm the
//      install is the version they expect.
//   2. Agent runtimes (and the validate.mjs check) can use the file's
//      mtime + git hash to detect "stale" caches and force a refresh.
//   3. The act of writing this file itself bumps the hub directory's
//      mtime, which is enough to invalidate most file-watcher / cache
//      schemes Claude Code, Cursor, etc. use to decide "did this change?".

import { execSync } from "node:child_process";
import { existsSync, mkdirSync, readFileSync, utimesSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

function gitHead(repoDir) {
  try {
    return execSync("git rev-parse HEAD", { cwd: repoDir, stdio: ["ignore", "pipe", "ignore"] })
      .toString()
      .trim();
  } catch {
    return null;
  }
}

function gitShortHead(repoDir) {
  const full = gitHead(repoDir);
  return full ? full.slice(0, 12) : null;
}

function gitDirty(repoDir) {
  try {
    const out = execSync("git status --porcelain", {
      cwd: repoDir,
      stdio: ["ignore", "pipe", "ignore"],
    })
      .toString()
      .trim();
    return out.length > 0;
  } catch {
    return null;
  }
}

function packageVersion(packageDir) {
  try {
    return JSON.parse(readFileSync(join(packageDir, "package.json"), "utf8")).version ?? null;
  } catch {
    return null;
  }
}

/**
 * Touch a file (set its mtime/atime to now). Used to nudge runtime watchers
 * to re-scan the surrounding directory when nothing else changed.
 */
export function touchFile(p, { dryRun = false, log = () => {} } = {}) {
  if (!existsSync(p)) return false;
  if (dryRun) {
    log(`[dry-run] touch ${p}`);
    return true;
  }
  try {
    const now = new Date();
    utimesSync(p, now, now);
    return true;
  } catch {
    return false;
  }
}

/**
 * Write the install manifest.
 *
 * @param {Object} opts
 * @param {string} opts.hubDir       Absolute path to <root>/.agents/skills
 * @param {string} opts.packageDir   Absolute path to the source package
 * @param {string} opts.installRoot  Absolute install root (HOME or project)
 * @param {string} opts.installMode  'global' | 'project'
 * @param {string[]} opts.skillNames Skill names linked into the hub
 * @param {string[]} opts.runtimes   Runtime ids that received mirrors
 * @param {boolean} [opts.force]     Whether this run was a forced refresh
 * @param {boolean} [opts.dryRun]
 * @param {(msg: string) => void} [opts.log]
 */
export function writeInstallManifest({
  hubDir,
  packageDir,
  installRoot,
  installMode,
  skillNames,
  runtimes,
  force = false,
  dryRun = false,
  log = () => {},
}) {
  if (!hubDir) return { skipped: true, reason: "no-hub" };
  const manifestPath = join(hubDir, "MANIFEST.json");
  const manifest = {
    schema: "adk-install-manifest/v1",
    installedAt: new Date().toISOString(),
    installMode,
    installRoot,
    package: {
      path: resolve(packageDir),
      version: packageVersion(packageDir),
      gitHead: gitHead(packageDir),
      gitHeadShort: gitShortHead(packageDir),
      gitDirty: gitDirty(packageDir),
    },
    runtimes,
    skills: [...skillNames].sort(),
    skillCount: skillNames.length,
    forcedRefresh: !!force,
  };
  if (dryRun) {
    log(`[dry-run] write ${manifestPath}`);
    return { dryRun: true, manifest };
  }
  mkdirSync(dirname(manifestPath), { recursive: true });
  writeFileSync(manifestPath, JSON.stringify(manifest, null, 2) + "\n", "utf8");
  log(`wrote ${manifestPath}`);
  return { written: true, manifestPath, manifest };
}

/** Read a previously written manifest. Returns null if absent / unreadable. */
export function readInstallManifest(hubDir) {
  if (!hubDir) return null;
  const p = join(hubDir, "MANIFEST.json");
  if (!existsSync(p)) return null;
  try {
    return JSON.parse(readFileSync(p, "utf8"));
  } catch {
    return null;
  }
}
