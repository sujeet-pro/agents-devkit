// Custom subagent install (one file per agent → symlinked into runtime's
// agents directory). Same idempotent contract as skills.

import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

import { ensureSymlink, pruneRepoLinks } from "./symlinks.mjs";

/** Discover runtime-specific custom agent files for a given runtime. */
export function discoverAgentFiles(repoDir, runtime) {
  if (!runtime.agentSourceDir || !runtime.agentFilePattern) return [];
  const sourceDir = join(repoDir, runtime.agentSourceDir);
  if (!existsSync(sourceDir)) return [];
  const ext = runtime.agentFilePattern.replace("adk-*", "");
  let names;
  try {
    names = readdirSync(sourceDir);
  } catch {
    return [];
  }
  return names
    .filter((n) => n.startsWith("adk-") && n.endsWith(ext))
    .map((n) => ({ name: n, path: join(sourceDir, n) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function installAgentsForRuntime({
  runtime,
  agentsDir,
  selectedAgentNames,
  repoDir,
  dryRun,
  log,
  force = false,
}) {
  if (!agentsDir || !runtime.agentSourceDir) {
    return { runtime: runtime.id, skipped: true, reason: "no-agents-dir" };
  }
  const pruned = pruneRepoLinks(agentsDir, repoDir, { dryRun, log });
  const created = [];
  const skipped = [];
  const all = discoverAgentFiles(repoDir, runtime);
  const wanted = selectedAgentNames
    ? all.filter((a) => selectedAgentNames.includes(a.name))
    : all;
  for (const agent of wanted) {
    const linkPath = join(agentsDir, agent.name);
    const result = ensureSymlink(agent.path, linkPath, { dryRun, log, force });
    if (result.status === "ok" || result.status === "would-link") created.push(agent.name);
    else skipped.push({ name: agent.name, reason: result.reason });
  }
  return { runtime: runtime.id, pruned: pruned.length, created, skipped };
}
