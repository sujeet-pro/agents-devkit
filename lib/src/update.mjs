/**
 * @module update
 * Update logic for AKIT — pulling from git, copying from local paths,
 * and syncing sources defined in a manifest.
 */

import { execSync } from "node:child_process";
import { cp, readdir, rm, mkdir } from "node:fs/promises";
import { join, basename } from "node:path";
import { readManifest, updateLastSync } from "./manifest.mjs";

/**
 * Pull the latest changes from the remote in the given devkit directory.
 * Runs `git pull --ff-only` so it will fail cleanly on divergent histories.
 *
 * @param {string} devkitDir - Absolute path to the agents-devkit repository.
 * @returns {{ok: boolean, output: string}} Result of the git pull.
 */
export function updateFromGit(devkitDir) {
  try {
    const output = execSync("git pull --ff-only", {
      cwd: devkitDir,
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "pipe"],
    });
    return { ok: true, output: output.trim() };
  } catch (err) {
    return {
      ok: false,
      output: err.stderr?.trim() || err.message,
    };
  }
}

/**
 * Copy files from a local filesystem path into the devkit directory.
 * Uses recursive copy (no symlinks — all content is materialised).
 *
 * @param {string} sourcePath - Absolute path to the source directory.
 * @param {string} devkitDir - Absolute path to the destination inside devkit.
 * @returns {Promise<{ok: boolean, filesCopied: number, error?: string}>}
 */
export async function updateFromFs(sourcePath, devkitDir) {
  try {
    // Ensure destination exists
    await mkdir(devkitDir, { recursive: true });

    // Count files before copy for reporting
    const entries = await readdir(sourcePath, { recursive: true });

    await cp(sourcePath, devkitDir, {
      recursive: true,
      dereference: true, // no symlinks — copy actual content
      force: true,
    });

    return { ok: true, filesCopied: entries.length };
  } catch (err) {
    return { ok: false, filesCopied: 0, error: err.message };
  }
}

/**
 * For each "copy" source in a manifest: clone the repo into a temp directory,
 * then copy the specified paths to their destinations.
 *
 * Manifest source shape for copy sources:
 *   { name, type: "copy", repo, paths: [{src, dest}], ... }
 *
 * @param {string} manifestPath - Path to the manifest.json file.
 * @param {string} tempDir - Writable temp directory for intermediate clones.
 * @returns {Promise<Array<{source: string, ok: boolean, error?: string}>>}
 */
export async function syncCopySources(manifestPath, tempDir) {
  const manifest = await readManifest(manifestPath);
  const sources = (manifest.sources || []).filter((s) => s.type === "copy");
  const results = [];

  for (const source of sources) {
    const cloneDir = join(tempDir, `clone-${basename(source.name)}`);
    try {
      // Clean up previous clone if any
      await rm(cloneDir, { recursive: true, force: true });

      // Shallow clone
      execSync(
        `git clone --depth 1 ${source.repo} ${cloneDir}`,
        { stdio: "pipe", encoding: "utf-8" }
      );

      // Copy each path mapping
      const paths = source.paths || [];
      for (const mapping of paths) {
        const src = join(cloneDir, mapping.src);
        const dest = mapping.dest;
        await mkdir(dest, { recursive: true });
        await cp(src, dest, { recursive: true, dereference: true, force: true });
      }

      // Update sync timestamp
      await updateLastSync(manifestPath, source.name);

      results.push({ source: source.name, ok: true });
    } catch (err) {
      results.push({ source: source.name, ok: false, error: err.message });
    } finally {
      // Clean up clone
      await rm(cloneDir, { recursive: true, force: true }).catch(() => {});
    }
  }

  return results;
}

/**
 * For each "ref" source in a manifest: clone the repo into a temp directory,
 * then diff the cloned content against the current local content.
 *
 * Returns a list of changes per source so the caller can decide whether
 * to apply updates.
 *
 * Manifest source shape for ref sources:
 *   { name, type: "ref", repo, ref_path, local_path, ... }
 *
 * @param {string} manifestPath - Path to the manifest.json file.
 * @param {string} tempDir - Writable temp directory for intermediate clones.
 * @returns {Promise<Array<{source: string, changes: string[], error?: string}>>}
 */
export async function checkRefSources(manifestPath, tempDir) {
  const manifest = await readManifest(manifestPath);
  const sources = (manifest.sources || []).filter((s) => s.type === "ref");
  const results = [];

  for (const source of sources) {
    const cloneDir = join(tempDir, `ref-${basename(source.name)}`);
    try {
      // Clean up previous clone if any
      await rm(cloneDir, { recursive: true, force: true });

      // Shallow clone
      execSync(
        `git clone --depth 1 ${source.repo} ${cloneDir}`,
        { stdio: "pipe", encoding: "utf-8" }
      );

      // Diff the ref path against local path
      const refPath = join(cloneDir, source.ref_path || ".");
      const localPath = source.local_path;

      let diffOutput = "";
      try {
        diffOutput = execSync(
          `diff -rq ${refPath} ${localPath}`,
          { encoding: "utf-8", stdio: ["pipe", "pipe", "pipe"] }
        );
      } catch (diffErr) {
        // diff exits with code 1 when differences are found — that's expected
        if (diffErr.status === 1) {
          diffOutput = diffErr.stdout || "";
        } else {
          throw diffErr;
        }
      }

      const changes = diffOutput
        .split("\n")
        .map((line) => line.trim())
        .filter(Boolean);

      results.push({ source: source.name, changes });
    } catch (err) {
      results.push({ source: source.name, changes: [], error: err.message });
    } finally {
      await rm(cloneDir, { recursive: true, force: true }).catch(() => {});
    }
  }

  return results;
}
