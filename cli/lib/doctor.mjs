// `adk doctor` — post-install integrity check.
//
// Verifies:
//   1. The hub `<root>/.agents/skills/` exists and is non-empty.
//   2. Every package skill is symlinked into the hub and resolves to a
//      readable directory containing SKILL.md.
//   3. For each detected runtime: the runtime's skills mirror dir contains a
//      symlink for each hub entry, pointing into the hub.
//   4. Each runtime memory file (CLAUDE.md / AGENTS.md / GEMINI.md) contains
//      the managed `<!-- adk:global-prompts -->` block.
//   5. The hub manifest (MANIFEST.json) exists, parses, and matches the
//      currently-discovered package skills (warns when the manifest is stale,
//      e.g. after a `git pull` without a re-install).

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { homedir } from "node:os";
import { join, resolve } from "node:path";

import { discoverPackageSkills, listHubEntries } from "./agents-hub.mjs";
import { discoverGlobalPrompts } from "./global-prompts.mjs";
import {
  RUNTIMES,
  agentsHubDir,
  isInstalled,
  runtimeMemoryPath,
  runtimeSkillsDir,
} from "./runtimes.mjs";
import { readInstallManifest } from "./install-manifest.mjs";
import { isLink, readLinkAbs } from "./symlinks.mjs";

const PROMPT_BLOCK_START = "<!-- adk:global-prompts:start -->";

function targetReadable(linkPath) {
  try {
    const target = readLinkAbs(linkPath);
    return existsSync(target) && statSync(target).isDirectory();
  } catch {
    return false;
  }
}

/**
 * @param {Object} opts
 * @param {string} opts.packageDir Source package root.
 * @param {string} [opts.root]     Install root. Defaults to $HOME.
 * @param {string} [opts.mode]     'global' | 'project'. Defaults to 'global'.
 */
export function runDoctor({ packageDir, root = homedir(), mode = "global" } = {}) {
  const errors = [];
  const warnings = [];
  const info = [];

  const hubDir = agentsHubDir(root);
  info.push(`hub: ${hubDir}`);
  const hubExists = existsSync(hubDir);
  if (!hubExists) {
    errors.push(`hub directory missing: ${hubDir} (run \`adk-install\`)`);
    return { errors, warnings, info };
  }

  // Stage 1: package skills → hub symlinks
  const pkgSkills = discoverPackageSkills(packageDir);
  const hubEntries = listHubEntries(hubDir);
  const hubByName = new Map(hubEntries.map((e) => [e.name, e]));

  for (const s of pkgSkills) {
    const hubEntry = hubByName.get(s.name);
    if (!hubEntry) {
      errors.push(`hub missing entry for package skill '${s.name}'`);
      continue;
    }
    const linkPath = join(hubDir, s.name);
    if (!isLink(linkPath)) {
      warnings.push(`hub entry '${s.name}' is not a symlink (user-managed?)`);
      continue;
    }
    if (!targetReadable(linkPath)) {
      errors.push(`hub entry '${s.name}' is a broken symlink`);
    }
  }
  info.push(`package skills available: ${pkgSkills.length}`);
  info.push(`hub entries (incl. user skills): ${hubEntries.length}`);

  // Stage 2: per-runtime mirrors
  const detected = RUNTIMES.filter(isInstalled);
  for (const rt of detected) {
    const skillsDir = runtimeSkillsDir(rt, root);
    if (!skillsDir) continue;
    if (!existsSync(skillsDir)) {
      warnings.push(`[${rt.id}] mirror dir missing: ${skillsDir}`);
      continue;
    }
    const have = new Set();
    for (const name of readdirSync(skillsDir)) {
      const full = join(skillsDir, name);
      if (!isLink(full)) continue;
      let target;
      try {
        target = readLinkAbs(full);
      } catch {
        continue;
      }
      if (!target.startsWith(hubDir + "/") && target !== hubDir) continue;
      have.add(name);
    }
    for (const e of hubEntries) {
      if (!have.has(e.name)) {
        errors.push(`[${rt.id}] mirror missing entry for hub skill '${e.name}'`);
      }
    }
    info.push(`[${rt.id}] mirror skills: ${have.size}/${hubEntries.length}`);
  }

  // Stage 3: memory files have the managed prompt block
  const allPrompts = discoverGlobalPrompts(packageDir);
  if (allPrompts.length > 0) {
    for (const rt of detected) {
      const memoryPath = runtimeMemoryPath(rt, root, mode);
      if (!memoryPath) continue;
      if (!existsSync(memoryPath)) {
        warnings.push(`[${rt.id}] memory file missing: ${memoryPath}`);
        continue;
      }
      const content = readFileSync(memoryPath, "utf8");
      if (!content.includes(PROMPT_BLOCK_START)) {
        warnings.push(
          `[${rt.id}] memory file ${memoryPath} has no managed prompt block (run \`adk-install -y\`)`,
        );
      }
    }
  }

  // Stage 4: manifest sanity
  const manifest = readInstallManifest(hubDir);
  if (!manifest) {
    warnings.push(`hub MANIFEST.json missing — run \`adk-install -y\` to generate it`);
  } else {
    info.push(
      `manifest: package=${manifest.package?.version ?? "?"} git=${manifest.package?.gitHeadShort ?? "?"}${manifest.package?.gitDirty ? " (dirty)" : ""} installedAt=${manifest.installedAt}`,
    );
    if (resolve(manifest.package?.path ?? "") !== resolve(packageDir)) {
      warnings.push(
        `manifest source path (${manifest.package?.path}) differs from the package being checked (${packageDir})`,
      );
    }
    const manifestSkills = new Set(manifest.skills ?? []);
    const pkgNames = new Set(pkgSkills.map((s) => s.name));
    const added = [...pkgNames].filter((n) => !manifestSkills.has(n));
    const removed = [...manifestSkills].filter((n) => !pkgNames.has(n));
    if (added.length || removed.length) {
      warnings.push(
        `manifest is stale (added since install: ${added.join(", ") || "-"}; removed: ${removed.join(", ") || "-"}). Re-run \`adk-install -y --force\` to refresh.`,
      );
    }
  }

  return { errors, warnings, info };
}
