/**
 * @module temp
 * .temp folder management for AKIT.
 * Provides helpers to create, organise, and clean up temporary working
 * directories used by skills and plans.
 */

import { mkdir, readFile, writeFile, readdir, stat, rm } from "node:fs/promises";
import { join } from "node:path";

/**
 * Ensure the .temp/ directory exists inside the given working directory.
 * If it does not exist it is created. The function also ensures .temp/ is
 * listed in .gitignore (creating the file if necessary).
 *
 * @param {string} cwd - The project root / working directory.
 * @returns {Promise<string>} Absolute path to the .temp/ directory.
 */
export async function ensureTemp(cwd) {
  const tempDir = join(cwd, ".temp");
  await mkdir(tempDir, { recursive: true });

  // Ensure .temp/ is in .gitignore
  const gitignorePath = join(cwd, ".gitignore");
  try {
    const content = await readFile(gitignorePath, "utf-8");
    if (!content.split("\n").some((line) => line.trim() === ".temp/")) {
      await writeFile(gitignorePath, content.trimEnd() + "\n.temp/\n", "utf-8");
    }
  } catch (err) {
    if (err.code === "ENOENT") {
      await writeFile(gitignorePath, ".temp/\n", "utf-8");
    } else {
      throw new Error(`Failed to update .gitignore: ${err.message}`);
    }
  }

  return tempDir;
}

/**
 * Return the path for a plan file inside .temp/plans/.
 * Creates the plans directory if it does not exist.
 *
 * @param {string} cwd - The project root / working directory.
 * @param {string} planId - Unique identifier for the plan.
 * @returns {Promise<string>} Absolute path to .temp/plans/<planId>.md
 */
export async function planPath(cwd, planId) {
  const plansDir = join(cwd, ".temp", "plans");
  await mkdir(plansDir, { recursive: true });
  return join(plansDir, `${planId}.md`);
}

/**
 * Return a timestamped temporary directory for a skill invocation.
 * Creates the directory tree if it does not exist.
 *
 * @param {string} cwd - The project root / working directory.
 * @param {string} skillName - Name of the skill requesting temp space.
 * @returns {Promise<string>} Absolute path to
 *   .temp/<skillName>/<timestamp>/
 */
export async function skillTempPath(cwd, skillName) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, "-");
  const dir = join(cwd, ".temp", skillName, timestamp);
  await mkdir(dir, { recursive: true });
  return dir;
}

/**
 * Remove temporary directories older than the given threshold.
 * Walks only one level deep inside .temp/ (skill-name directories) and
 * removes any subdirectory whose modification time exceeds maxAgeDays.
 *
 * @param {string} cwd - The project root / working directory.
 * @param {number} [maxAgeDays=7] - Maximum age in days before cleanup.
 * @returns {Promise<string[]>} List of removed directory paths.
 */
export async function cleanOldTemp(cwd, maxAgeDays = 7) {
  const tempDir = join(cwd, ".temp");
  const removed = [];
  const cutoff = Date.now() - maxAgeDays * 24 * 60 * 60 * 1000;

  let topEntries;
  try {
    topEntries = await readdir(tempDir, { withFileTypes: true });
  } catch (err) {
    if (err.code === "ENOENT") return removed;
    throw new Error(`Failed to read .temp directory: ${err.message}`);
  }

  for (const entry of topEntries) {
    if (!entry.isDirectory()) continue;

    const skillDir = join(tempDir, entry.name);
    let subEntries;
    try {
      subEntries = await readdir(skillDir, { withFileTypes: true });
    } catch {
      continue;
    }

    for (const sub of subEntries) {
      if (!sub.isDirectory()) continue;

      const subPath = join(skillDir, sub.name);
      try {
        const info = await stat(subPath);
        if (info.mtimeMs < cutoff) {
          await rm(subPath, { recursive: true, force: true });
          removed.push(subPath);
        }
      } catch {
        // Skip entries we cannot stat
      }
    }
  }

  return removed;
}
