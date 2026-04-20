#!/usr/bin/env node
// agents-devkit interactive installer.
//
// Usage:
//   adk-install                   # via npm bin (after install)
//   npx adk-install               # one-shot from a clone or after install
//   npm run setup                 # from a clone
//
// Flags:
//   --dry-run                     # preview, write nothing
//   --mode global|project         # force install scope (default: auto-detect)
//   --root <path>                 # override the install root (rare)
//   -y, --yes                     # skip confirmation prompts where safe
//   -h, --help
//
// Two-stage skill model:
//
//   1. Sync `<root>/.agents/skills/adk-*` against this package's `skills/`.
//      User-created entries in `<root>/.agents/skills/` (plain dirs) are
//      left alone.
//   2. Sync each selected runtime's skills mirror dir
//      (`<root>/.claude/skills`, `<root>/.cursor/skills`, …) against the
//      hub. Stale symlinks pointing into the hub are pruned and recreated.
//
// Re-running converges everything to the current state.

import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

import {
  cancel,
  confirm,
  intro,
  isCancel,
  log as clog,
  multiselect,
  note,
  outro,
  select,
  text,
} from "@clack/prompts";

import {
  RUNTIMES,
  agentsHubDir,
  isInstalled,
  runtimeAgentsDir,
  runtimeHookPath,
  runtimeMcpPath,
  runtimeMemoryPath,
  runtimeSkillsDir,
} from "./lib/runtimes.mjs";
import {
  discoverPackageSkills,
  listHubEntries,
  mirrorHubInto,
  syncHub,
} from "./lib/agents-hub.mjs";
import { discoverAgentFiles, installAgentsForRuntime } from "./lib/agents.mjs";
import { installHookForRuntime } from "./lib/hooks.mjs";
import {
  applyGlobalPrompts,
  discoverGlobalPrompts,
} from "./lib/global-prompts.mjs";
import { discoverMcpServers, mergeMcpServers } from "./lib/mcp.mjs";
import { readZshenv, upsertZshenv, zshenvPath } from "./lib/zshenv.mjs";
import {
  effectiveDefaults,
  loadUserSettings,
  rememberPackagePath,
  saveUserSettings,
  setProjectDefaults,
  userSettingsPath,
} from "./lib/settings.mjs";
import { describeInstall, detectInstall, resolveRoot } from "./lib/install-mode.mjs";

const __filename = fileURLToPath(import.meta.url);
const PACKAGE_DIR = resolve(dirname(__filename), "..");

const args = parseArgs(process.argv.slice(2));

function parseArgs(argv) {
  const out = { dryRun: false, mode: null, root: null, yes: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") out.dryRun = true;
    else if (a === "--mode") out.mode = argv[++i];
    else if (a === "--root") out.root = argv[++i];
    else if (a === "--yes" || a === "-y") out.yes = true;
    else if (a === "--help" || a === "-h") {
      printHelp();
      process.exit(0);
    } else {
      console.error(`Unknown argument: ${a}`);
      printHelp();
      process.exit(1);
    }
  }
  return out;
}

function printHelp() {
  let version = "0.0.0";
  try {
    version = JSON.parse(readFileSync(resolve(PACKAGE_DIR, "package.json"), "utf8")).version;
  } catch {}
  process.stdout.write(`agents-devkit installer v${version}

Usage:
  adk-install [flags]              once installed (npm i -g agents-devkit)
  npx adk-install [flags]          one-shot, from a clone or after install
  npm run setup -- [flags]         from a clone of the repo

Flags:
  --dry-run        Preview the plan; write nothing.
  --mode <m>       Force install scope: 'global' ($HOME) or 'project' (cwd / detected project root).
                   Default: auto-detected from how the CLI was launched.
  --root <path>    Override the install root path. Rarely needed.
  -y, --yes        Skip the final confirmation prompt.
  -h, --help       Show this help.

What it does:
  1. Syncs <root>/.agents/skills/adk-* against this package's skills/
     (prunes stale package symlinks, creates fresh ones; user-created
     skills in <root>/.agents/skills/ are left alone).
  2. Mirrors <root>/.agents/skills/* into each selected runtime's skills
     dir (.claude/skills, .cursor/skills, .codex/skills, …).
  3. Installs runtime-specific custom subagents and hook configs.
  4. Merges chosen MCP servers into each runtime's mcp.json, prompting for
     missing env vars and persisting them to ~/.zshenv.
  5. Maintains an <!-- adk:global-prompts:start/end --> block in each
     runtime's memory file (CLAUDE.md / AGENTS.md / GEMINI.md).
  6. Persists your choices to ${userSettingsPath()} (and to <project>/.adk/settings.json5
     when --mode project) so the next run pre-fills.
`);
}

function bail(msg) {
  cancel(msg);
  process.exit(1);
}

const log = (msg) => clog.message(msg);

async function main() {
  intro("agents-devkit setup");

  const install = detectInstall(PACKAGE_DIR);
  note(describeInstall(install), "Install detection");

  if (args.dryRun) {
    note("Running in --dry-run mode. Nothing will be written.", "Heads up");
  }

  let settings = loadUserSettings();
  settings = rememberPackagePath(settings, PACKAGE_DIR);

  const detected = RUNTIMES.filter(isInstalled);
  if (detected.length > 0) {
    note(detected.map((rt) => `  · ${rt.label} (${rt.id})`).join("\n"), "Detected runtimes");
  }

  // ---- Mode + root ----
  const mode = args.mode ?? (await pickMode(install));
  if (mode !== "global" && mode !== "project") bail(`invalid mode: ${mode}`);
  const root = args.root ? resolve(args.root) : resolveRoot({ mode, install, cwd: process.cwd() });
  note(`Install root: ${root}`, "Scope");

  // ---- Defaults pulled from settings ----
  const defaults = effectiveDefaults({
    mode,
    projectRoot: mode === "project" ? root : null,
    userSettings: settings,
  });

  // ---- Runtimes ----
  const selectedRuntimes = await pickRuntimes(detected, defaults.runtimes);
  if (selectedRuntimes.length === 0) {
    note("No runtime mirrors selected. The .agents/skills hub will still be synced.", "Heads up");
  }

  // ---- Sources ----
  const packageSkills = discoverPackageSkills(PACKAGE_DIR);
  const allPrompts = discoverGlobalPrompts(PACKAGE_DIR);
  const allServers = discoverMcpServers(PACKAGE_DIR);

  note(
    [
      `Package adk-* skills available: ${packageSkills.length}`,
      `Global prompts available:       ${allPrompts.length}`,
      `MCP servers available:          ${allServers.length}`,
      `Hub dir (will be managed):      ${agentsHubDir(root)}`,
    ].join("\n"),
    "Inventory",
  );

  const surfaces = await pickSurfaces(defaults.surfaces);

  // ---- Skills ----
  let selectedSkills = [];
  if (surfaces.includes("skills") && packageSkills.length > 0) {
    selectedSkills = await pickSkills(packageSkills, defaults.skills);
  }

  // ---- Custom agents (per runtime that supports them) ----
  /** @type {Record<string,string[]>} */
  const selectedAgentsByRuntime = {};
  if (surfaces.includes("agents")) {
    for (const rt of selectedRuntimes) {
      if (!rt.agentSourceDir) continue;
      const agentFiles = discoverAgentFiles(PACKAGE_DIR, rt);
      if (agentFiles.length === 0) continue;
      const picked = await pickAgents(rt, agentFiles);
      selectedAgentsByRuntime[rt.id] = picked.map((a) => a.name);
    }
  }

  // ---- Hooks ----
  let installHooks = false;
  if (surfaces.includes("hooks")) {
    installHooks = await confirmStep("Install runtime hook configs (claude/cursor/codex)?", true);
  }

  // ---- MCP ----
  let selectedServers = [];
  let envValues = {};
  if (surfaces.includes("mcp") && allServers.length > 0) {
    selectedServers = await pickMcpServers(allServers, defaults.mcpServers);
    if (selectedServers.length > 0) {
      envValues = await collectMcpEnv(selectedServers);
    }
  }

  // ---- Global prompts ----
  let selectedPrompts = [];
  if (surfaces.includes("global-prompts") && allPrompts.length > 0) {
    selectedPrompts = await pickGlobalPrompts(allPrompts, defaults.globalPrompts);
  }

  // ---- Plan summary ----
  note(
    [
      `Mode:           ${mode}`,
      `Root:           ${root}`,
      `Runtimes:       ${selectedRuntimes.map((r) => r.id).join(", ") || "(none)"}`,
      `Hub skills:     ${selectedSkills.length} package adk-* + user skills`,
      `Custom agents:  ${Object.values(selectedAgentsByRuntime).reduce((a, b) => a + b.length, 0)}`,
      `Hook configs:   ${installHooks ? "yes" : "no"}`,
      `MCP servers:    ${selectedServers.length}`,
      `Global prompts: ${selectedPrompts.length}`,
    ].join("\n"),
    "Plan",
  );

  if (!args.yes) {
    const ok = await confirmStep("Apply this plan now?", true);
    if (!ok) bail("aborted by user");
  }

  // ---- Apply: Stage A — sync the hub ----
  const hubDir = agentsHubDir(root);
  if (surfaces.includes("skills")) {
    const result = syncHub({
      hubDir,
      packageDir: PACKAGE_DIR,
      knownPackagePaths: settings.knownPackagePaths,
      selectedSkills,
      dryRun: args.dryRun,
      log,
    });
    log(
      `[hub] ${hubDir}: pruned ${result.pruned ?? 0}, linked ${result.created?.length ?? 0}, skipped ${result.skipped?.length ?? 0}`,
    );
  }

  // List hub entries (post-sync) so we know what to mirror.
  const hubEntries = args.dryRun
    ? selectedSkills.map((s) => ({ name: s.name, path: s.path }))
    : listHubEntries(hubDir);
  const hubNames = hubEntries.map((e) => e.name);

  // ---- Apply: Stage B — mirror hub into each runtime ----
  for (const rt of selectedRuntimes) {
    const skillsDir = runtimeSkillsDir(rt, root);
    if (skillsDir) {
      const result = mirrorHubInto({
        hubDir,
        mirrorDir: skillsDir,
        selectedNames: hubNames,
        dryRun: args.dryRun,
        log,
      });
      log(
        `[${rt.id}] mirror ${skillsDir}: pruned ${result.pruned ?? 0}, linked ${result.created?.length ?? 0}`,
      );
    }

    // Custom subagents (claude/cursor/codex).
    const agentsDir = runtimeAgentsDir(rt, root);
    const wantedAgents = selectedAgentsByRuntime[rt.id];
    if (wantedAgents && agentsDir) {
      const result = installAgentsForRuntime({
        runtime: rt,
        agentsDir,
        selectedAgentNames: wantedAgents,
        repoDir: PACKAGE_DIR,
        dryRun: args.dryRun,
        log,
      });
      log(`[${rt.id}] agents: pruned ${result.pruned ?? 0}, linked ${result.created?.length ?? 0}`);
    }

    if (installHooks) {
      const hookPath = runtimeHookPath(rt, root);
      if (hookPath && rt.hookSource) {
        const result = installHookForRuntime({
          runtime: rt,
          hookPath,
          repoDir: PACKAGE_DIR,
          dryRun: args.dryRun,
          log,
        });
        log(`[${rt.id}] hook: ${JSON.stringify(result.result ?? { skipped: true })}`);
      }
    }

    if (selectedServers.length > 0) {
      const mcpPath = runtimeMcpPath(rt, root, mode);
      if (mcpPath) {
        const result = mergeMcpServers({
          configPath: mcpPath,
          serversKey: rt.mcpServersKey,
          servers: selectedServers,
          dryRun: args.dryRun,
          log,
        });
        log(`[${rt.id}] mcp: ${JSON.stringify(result)}`);
      } else {
        log(`[${rt.id}] mcp: no config path for this runtime in ${mode} mode (skipped)`);
      }
    }

    const memoryPath = runtimeMemoryPath(rt, root, mode);
    if (memoryPath) {
      const result = applyGlobalPrompts({
        memoryPath,
        selectedPrompts,
        dryRun: args.dryRun,
        log,
      });
      log(`[${rt.id}] memory: ${JSON.stringify(result)}`);
    }
  }

  // ---- Persist env vars to ~/.zshenv ----
  if (Object.keys(envValues).length > 0) {
    const result = upsertZshenv(envValues, { dryRun: args.dryRun, log });
    log(`zshenv (${zshenvPath()}): ${JSON.stringify(result)}`);
    note(
      "Open a new shell or run `source ~/.zshenv` so the new env vars are picked up.",
      "Reminder",
    );
  }

  // ---- Persist settings ----
  const choices = {
    runtimes: selectedRuntimes.map((rt) => rt.id),
    surfaces,
    skills: selectedSkills.length === packageSkills.length ? "all" : selectedSkills.map((s) => s.name),
    mcpServers: selectedServers.map((s) => s.name),
    globalPrompts: selectedPrompts.length === allPrompts.length ? "all" : selectedPrompts.map((p) => p.name),
  };

  const updatedUser = {
    ...settings,
    installMode: mode,
    ...choices,
  };
  saveUserSettings(updatedUser, { dryRun: args.dryRun, log });

  if (mode === "project") {
    setProjectDefaults(updatedUser, root, choices, { dryRun: args.dryRun, log });
  }

  outro(args.dryRun ? "Dry-run complete. Re-run without --dry-run to apply." : "Setup complete.");
}

async function pickMode(install) {
  const v = await select({
    message: "Where should the installer write?",
    options: [
      {
        value: "global",
        label: "Global ($HOME)",
        hint: install.kind === "npm-global" || install.kind === "clone" ? "default" : "",
      },
      {
        value: "project",
        label: install.projectRoot
          ? `Project (${install.projectRoot})`
          : `Project (cwd: ${process.cwd()})`,
        hint: install.kind === "npm-project" ? "default — auto-detected" : "",
      },
    ],
    initialValue: install.defaultMode,
  });
  if (isCancel(v)) bail("cancelled");
  return v;
}

async function pickRuntimes(detected, defaultIds) {
  const detectedIds = new Set(detected.map((rt) => rt.id));
  const initial = defaultIds && defaultIds.length > 0
    ? defaultIds.filter((id) => RUNTIMES.find((rt) => rt.id === id))
    : detected.map((rt) => rt.id);
  const opts = RUNTIMES.map((rt) => ({
    value: rt.id,
    label: rt.label,
    hint: detectedIds.has(rt.id) ? "detected" : "not detected",
  }));
  const v = await multiselect({
    message: "Which runtime mirrors should I populate from .agents/skills?",
    options: opts,
    initialValues: initial,
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return v.map((id) => RUNTIMES.find((rt) => rt.id === id)).filter(Boolean);
}

async function pickSurfaces(defaultSurfaces) {
  const v = await multiselect({
    message: "Which surfaces should I configure?",
    options: [
      { value: "skills", label: "Skills (.agents/skills hub + runtime mirrors)" },
      { value: "agents", label: "Custom subagents (claude/cursor/codex)" },
      { value: "hooks", label: "Hook configs (claude/cursor/codex)" },
      { value: "mcp", label: "MCP servers" },
      { value: "global-prompts", label: "Global prompts (managed memory-file block)" },
    ],
    initialValues: defaultSurfaces ?? ["skills", "agents", "hooks", "mcp", "global-prompts"],
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return v;
}

async function pickSkills(allSkills, defaultSkills) {
  const initial =
    defaultSkills === "all" || !defaultSkills
      ? allSkills.map((s) => s.name)
      : defaultSkills.filter((n) => allSkills.find((s) => s.name === n));
  const choice = await select({
    message: `Found ${allSkills.length} package skill(s) (adk-*). Install all, or pick?`,
    options: [
      { value: "all", label: "Install all" },
      { value: "pick", label: "Pick a subset" },
      { value: "none", label: "None (only sync user-created skills in the hub)" },
    ],
    initialValue: defaultSkills === "all" || !defaultSkills ? "all" : "pick",
  });
  if (isCancel(choice)) bail("cancelled");
  if (choice === "all") return allSkills;
  if (choice === "none") return [];
  const v = await multiselect({
    message: "Choose the package skills to install",
    options: allSkills.map((s) => ({ value: s.name, label: s.name })),
    initialValues: initial,
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return allSkills.filter((s) => v.includes(s.name));
}

async function pickAgents(runtime, agentFiles) {
  const v = await multiselect({
    message: `Custom subagents for ${runtime.label}`,
    options: agentFiles.map((a) => ({ value: a.name, label: a.name })),
    initialValues: agentFiles.map((a) => a.name),
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return agentFiles.filter((a) => v.includes(a.name));
}

async function pickMcpServers(servers, defaultNames) {
  const initial = (defaultNames ?? []).filter((n) => servers.find((s) => s.name === n));
  const v = await multiselect({
    message: "Which MCP servers should I configure?",
    options: servers.map((s) => ({
      value: s.name,
      label: s.title,
      hint: s.description.slice(0, 80),
    })),
    initialValues: initial,
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return servers.filter((s) => v.includes(s.name));
}

async function pickGlobalPrompts(prompts, defaultPrompts) {
  const initial =
    defaultPrompts === "all" || !defaultPrompts
      ? prompts.map((p) => p.name)
      : defaultPrompts.filter((n) => prompts.find((p) => p.name === n));
  const v = await multiselect({
    message: "Which global prompts should I install into runtime memory files?",
    options: prompts.map((p) => ({ value: p.name, label: p.name })),
    initialValues: initial,
    required: false,
  });
  if (isCancel(v)) bail("cancelled");
  return prompts.filter((p) => v.includes(p.name));
}

async function collectMcpEnv(selectedServers) {
  const existing = readZshenv();
  const collected = {};
  const allVars = new Map();
  for (const server of selectedServers) {
    for (const v of server.envVars) {
      if (!allVars.has(v)) allVars.set(v, new Set());
      allVars.get(v).add(server.title);
    }
  }
  if (allVars.size === 0) return {};

  note(
    `Each MCP server above expects shell env vars. I'll read existing values from ${zshenvPath()} and prompt for any that are missing.`,
    "MCP env",
  );

  for (const [key, servers] of allVars) {
    const usedBy = [...servers].join(", ");
    const help = serverHelpFor(key, selectedServers);
    if (help) clog.info(help);
    const def = existing[key] ?? process.env[key] ?? "";
    const v = await text({
      message: `${key}  (used by: ${usedBy})`,
      placeholder: def ? "(press enter to keep current value)" : "<value>",
      initialValue: def,
      validate: (val) => {
        if (!val && !def) return "value required";
        return undefined;
      },
    });
    if (isCancel(v)) bail("cancelled");
    if (v && v !== existing[key]) collected[key] = v;
  }
  return collected;
}

function serverHelpFor(envVar, selectedServers) {
  for (const s of selectedServers) {
    if (s.envVars.includes(envVar)) {
      return `${envVar} — ${s.instructions}`;
    }
  }
  return null;
}

async function confirmStep(message, initial = true) {
  const v = await confirm({ message, initialValue: initial });
  if (isCancel(v)) bail("cancelled");
  return v;
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
