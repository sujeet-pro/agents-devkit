// Runtime descriptors used by the interactive installer.
//
// Skill model (post-refactor):
//
//   .agents/skills/<name>          ← single source of truth for *all* skills
//                                    (managed adk-* symlinks + user-created
//                                    personal skill dirs)
//   .claude/skills/<name>          ← symlink → .agents/skills/<name>
//   .cursor/skills/<name>          ← symlink → .agents/skills/<name>
//   .codex/skills/<name>           ← symlink → .agents/skills/<name>
//   .antigravity/skills/<name>     ← symlink → .agents/skills/<name>
//   .junie/skills/<name>           ← symlink → .agents/skills/<name>
//
// `<root>` is `$HOME` for global installs and `<project-root>` for project
// installs. `.agents` is no longer a "selectable runtime" — it is always
// populated as the central hub.

import { homedir, platform } from "node:os";
import { existsSync } from "node:fs";
import { join } from "node:path";

const HOME = homedir();
const IS_MAC = platform() === "darwin";

const claudeDesktopMcp = IS_MAC
  ? join(HOME, "Library", "Application Support", "Claude", "claude_desktop_config.json")
  : join(HOME, ".config", "Claude", "claude_desktop_config.json");

const claudeDesktopMemory = IS_MAC
  ? join(HOME, "Library", "Application Support", "Claude", "CLAUDE.md")
  : join(HOME, ".config", "Claude", "CLAUDE.md");

const codexDesktopRoot = IS_MAC
  ? join(HOME, "Library", "Application Support", "Codex")
  : join(HOME, ".config", "Codex");

/**
 * Each descriptor declares relative paths under the install root for
 * skills mirror / custom subagents / hook config / mcp config / memory
 * file, plus absolute "global only" paths for runtimes whose canonical
 * config lives outside `$HOME` (e.g. Claude Desktop on macOS uses
 * `~/Library/Application Support/Claude/...`).
 */
export const RUNTIMES = [
  {
    id: "claude-code",
    label: "Claude Code (CLI)",
    family: "claude",
    detectPaths: [join(HOME, ".claude")],
    skillsRel: ".claude/skills",
    agentsRel: ".claude/agents",
    agentSourceDir: "agents-claude",
    agentFilePattern: "adk-*.md",
    hookRel: ".claude/settings.json",
    hookSource: "hooks/claude.json",
    mcpRel: ".claude/mcp.json",
    memoryRel: "CLAUDE.md",
    globalMemoryAbs: join(HOME, ".claude", "CLAUDE.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "claude-desktop",
    label: "Claude Desktop App",
    family: "claude",
    detectPaths: [
      claudeDesktopMcp,
      IS_MAC ? join(HOME, "Library", "Application Support", "Claude") : join(HOME, ".config", "Claude"),
    ],
    skillsRel: null,
    agentsRel: null,
    agentSourceDir: null,
    agentFilePattern: null,
    hookRel: null,
    hookSource: null,
    mcpRel: null,
    memoryRel: null,
    globalMcpAbs: claudeDesktopMcp,
    globalMemoryAbs: claudeDesktopMemory,
    mcpServersKey: "mcpServers",
  },
  {
    id: "cursor",
    label: "Cursor (App + CLI)",
    family: "cursor",
    detectPaths: [join(HOME, ".cursor")],
    skillsRel: ".cursor/skills",
    agentsRel: ".cursor/agents",
    agentSourceDir: "agents-cursor",
    agentFilePattern: "adk-*.md",
    hookRel: ".cursor/hooks.json",
    hookSource: "hooks/cursor.json",
    mcpRel: ".cursor/mcp.json",
    memoryRel: "AGENTS.md",
    globalMemoryAbs: join(HOME, ".cursor", "AGENTS.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "codex-cli",
    label: "Codex CLI",
    family: "codex",
    detectPaths: [join(HOME, ".codex")],
    skillsRel: ".codex/skills",
    agentsRel: ".codex/agents",
    agentSourceDir: "agents-codex",
    agentFilePattern: "adk-*.toml",
    hookRel: ".codex/hooks.json",
    hookSource: "hooks/codex.json",
    mcpRel: ".codex/mcp.json",
    memoryRel: "AGENTS.md",
    globalMemoryAbs: join(HOME, ".codex", "AGENTS.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "codex-desktop",
    label: "Codex Desktop App",
    family: "codex",
    detectPaths: [codexDesktopRoot],
    skillsRel: null,
    agentsRel: null,
    agentSourceDir: null,
    agentFilePattern: null,
    hookRel: null,
    hookSource: null,
    mcpRel: null,
    memoryRel: null,
    globalMcpAbs: join(codexDesktopRoot, "mcp.json"),
    globalMemoryAbs: join(codexDesktopRoot, "AGENTS.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "antigravity",
    label: "Antigravity",
    family: "generic",
    detectPaths: [join(HOME, ".antigravity")],
    skillsRel: ".antigravity/skills",
    agentsRel: null,
    agentSourceDir: null,
    agentFilePattern: null,
    hookRel: null,
    hookSource: null,
    mcpRel: null,
    memoryRel: "AGENTS.md",
    globalMemoryAbs: join(HOME, ".antigravity", "AGENTS.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "junie",
    label: "JetBrains Junie",
    family: "generic",
    detectPaths: [join(HOME, ".junie")],
    skillsRel: ".junie/skills",
    agentsRel: null,
    agentSourceDir: null,
    agentFilePattern: null,
    hookRel: null,
    hookSource: null,
    mcpRel: null,
    memoryRel: "AGENTS.md",
    globalMemoryAbs: join(HOME, ".junie", "AGENTS.md"),
    mcpServersKey: "mcpServers",
  },
  {
    id: "gemini-cli",
    label: "Gemini CLI",
    family: "generic",
    detectPaths: [join(HOME, ".gemini")],
    skillsRel: null,
    agentsRel: null,
    agentSourceDir: null,
    agentFilePattern: null,
    hookRel: null,
    hookSource: null,
    mcpRel: ".gemini/mcp.json",
    memoryRel: "GEMINI.md",
    globalMcpAbs: join(HOME, ".gemini", "mcp.json"),
    globalMemoryAbs: join(HOME, ".gemini", "GEMINI.md"),
    mcpServersKey: "mcpServers",
  },
];

/** Path of the central `.agents/skills` hub for the chosen install root. */
export function agentsHubDir(rootDir) {
  return join(rootDir, ".agents", "skills");
}

export function isInstalled(rt) {
  return rt.detectPaths.some((p) => existsSync(p));
}

export function getRuntime(id) {
  return RUNTIMES.find((rt) => rt.id === id);
}

export function runtimeSkillsDir(rt, rootDir) {
  if (!rt.skillsRel) return null;
  return join(rootDir, rt.skillsRel);
}

export function runtimeAgentsDir(rt, rootDir) {
  if (!rt.agentsRel) return null;
  return join(rootDir, rt.agentsRel);
}

export function runtimeHookPath(rt, rootDir) {
  if (!rt.hookRel) return null;
  return join(rootDir, rt.hookRel);
}

export function runtimeMcpPath(rt, rootDir, mode) {
  // Some runtimes (claude-desktop, codex-desktop, gemini) only support a
  // global mcp config; project mode just skips them.
  if (rt.mcpRel) return join(rootDir, rt.mcpRel);
  if (mode === "global" && rt.globalMcpAbs) return rt.globalMcpAbs;
  return null;
}

export function runtimeMemoryPath(rt, rootDir, mode) {
  if (rt.memoryRel && mode === "project") return join(rootDir, rt.memoryRel);
  if (mode === "global" && rt.globalMemoryAbs) return rt.globalMemoryAbs;
  if (rt.memoryRel) return join(rootDir, rt.memoryRel);
  return null;
}
