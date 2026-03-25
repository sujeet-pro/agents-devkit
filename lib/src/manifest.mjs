/**
 * @module manifest
 * Read, write, and diff operations for AKIT manifest.json files.
 * Manifests track external sources (git repos, local paths) that feed
 * skills and guidelines into the devkit.
 */

import { readFile, writeFile } from "node:fs/promises";
import { stat } from "node:fs/promises";
import { relative, resolve } from "node:path";

/**
 * Read and parse a manifest.json file.
 * @param {string} manifestPath - Absolute or relative path to manifest.json.
 * @returns {Promise<object>} The parsed manifest object.
 * @throws {Error} If the file cannot be read or contains invalid JSON.
 */
export async function readManifest(manifestPath) {
  try {
    const raw = await readFile(manifestPath, "utf-8");
    return JSON.parse(raw);
  } catch (err) {
    if (err.code === "ENOENT") {
      throw new Error(`Manifest not found: ${manifestPath}`);
    }
    if (err instanceof SyntaxError) {
      throw new Error(`Invalid JSON in manifest at ${manifestPath}: ${err.message}`);
    }
    throw new Error(`Failed to read manifest at ${manifestPath}: ${err.message}`);
  }
}

/**
 * Write a manifest object to disk with pretty-printed JSON (2-space indent).
 * @param {string} manifestPath - Absolute or relative path to manifest.json.
 * @param {object} data - The manifest data to serialise.
 * @returns {Promise<void>}
 */
export async function writeManifest(manifestPath, data) {
  try {
    const json = JSON.stringify(data, null, 2) + "\n";
    await writeFile(manifestPath, json, "utf-8");
  } catch (err) {
    throw new Error(`Failed to write manifest at ${manifestPath}: ${err.message}`);
  }
}

/**
 * Compare a manifest source entry against the files that actually exist on
 * disk, returning a list of changes.
 *
 * Each change is an object with:
 *   - file: string   — relative file path
 *   - status: string — "added" | "removed" | "modified"
 *
 * @param {object} source - A manifest source entry. Expected shape:
 *   { name, files: string[], dest: string }
 * @param {string[]} localPaths - Array of absolute paths that currently exist
 *   in the destination directory for this source.
 * @returns {Promise<Array<{file: string, status: string}>>}
 */
export async function diffSource(source, localPaths) {
  const changes = [];
  const destDir = resolve(source.dest || ".");

  // Build a set of relative paths from the local files
  const localSet = new Set(
    localPaths.map((p) => relative(destDir, resolve(p)))
  );

  // Build a set of files the manifest expects
  const manifestSet = new Set(source.files || []);

  // Files in manifest but not on disk => removed
  for (const file of manifestSet) {
    if (!localSet.has(file)) {
      changes.push({ file, status: "removed" });
    }
  }

  // Files on disk but not in manifest => added
  for (const file of localSet) {
    if (!manifestSet.has(file)) {
      changes.push({ file, status: "added" });
    }
  }

  // Files present in both — check modification times if possible
  for (const file of manifestSet) {
    if (localSet.has(file)) {
      try {
        const fullPath = resolve(destDir, file);
        const info = await stat(fullPath);
        // If the source provides a last_sync timestamp we can compare
        if (source.last_sync) {
          const syncDate = new Date(source.last_sync);
          if (info.mtime > syncDate) {
            changes.push({ file, status: "modified" });
          }
        }
      } catch {
        // stat failed — treat as removed
        changes.push({ file, status: "removed" });
      }
    }
  }

  return changes;
}

/**
 * Update the `last_sync` timestamp for a named source inside a manifest file.
 * Reads the manifest, sets `last_sync` to the current ISO timestamp, and
 * writes it back.
 *
 * @param {string} manifestPath - Path to the manifest.json file.
 * @param {string} sourceName - The `name` field of the source to update.
 * @returns {Promise<void>}
 * @throws {Error} If the source is not found in the manifest.
 */
export async function updateLastSync(manifestPath, sourceName) {
  const manifest = await readManifest(manifestPath);
  const sources = manifest.sources || [];
  const source = sources.find((s) => s.name === sourceName);

  if (!source) {
    throw new Error(
      `Source "${sourceName}" not found in manifest at ${manifestPath}`
    );
  }

  source.last_sync = new Date().toISOString();
  await writeManifest(manifestPath, manifest);
}
