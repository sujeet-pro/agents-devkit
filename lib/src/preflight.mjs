/**
 * @module preflight
 * Programmatic preflight checker for AKIT skills.
 * Validates that required commands, npm packages, and MCP servers are available
 * before a skill runs.
 */

import { execSync } from "node:child_process";
import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { homedir } from "node:os";

/**
 * Check whether a command-line tool is installed and available on PATH.
 * @param {string} name - The command name to look up (e.g. "git", "node").
 * @returns {{ok: boolean, name: string, installed: boolean}}
 */
export function checkCommand(name) {
  try {
    execSync(`command -v ${name}`, { stdio: "ignore" });
    return { ok: true, name, installed: true };
  } catch {
    return { ok: false, name, installed: false };
  }
}

/**
 * Check whether a global npm package is installed.
 * @param {string} name - The npm package name (e.g. "typescript").
 * @returns {{ok: boolean, name: string, installed: boolean}}
 */
export function checkGlobalNpmPackage(name) {
  try {
    const output = execSync("npm ls -g --depth=0 --json", {
      encoding: "utf-8",
      stdio: ["pipe", "pipe", "ignore"],
    });
    const parsed = JSON.parse(output);
    const deps = parsed.dependencies || {};
    const installed = name in deps;
    return { ok: installed, name, installed };
  } catch {
    return { ok: false, name, installed: false };
  }
}

/**
 * Check whether an MCP server is configured in the Claude config file.
 * @param {string} name - The MCP server name to look for.
 * @param {string} [configPath] - Path to the Claude config file.
 *   Defaults to ~/.claude.json.
 * @returns {Promise<{ok: boolean, name: string, installed: boolean}>}
 */
export async function checkMcpServer(name, configPath) {
  const resolvedPath = configPath || join(homedir(), ".claude.json");
  try {
    const raw = await readFile(resolvedPath, "utf-8");
    const config = JSON.parse(raw);
    const servers = config.mcpServers || {};
    const installed = name in servers;
    return { ok: installed, name, installed };
  } catch (err) {
    if (err.code === "ENOENT") {
      return { ok: false, name, installed: false };
    }
    throw new Error(
      `Failed to read Claude config at ${resolvedPath}: ${err.message}`
    );
  }
}

/**
 * Detect the provider type from a URL string.
 * Recognises GitHub, Bitbucket, Confluence, and Google Drive.
 * @param {string} input - A URL or string to inspect.
 * @returns {string|null} One of "github", "bitbucket", "confluence",
 *   "google-drive", or null if unrecognised.
 */
export function detectProvider(input) {
  if (!input || typeof input !== "string") return null;

  const lower = input.toLowerCase();

  if (lower.includes("github.com") || lower.includes("github.dev")) {
    return "github";
  }
  if (lower.includes("bitbucket.org") || lower.includes("bitbucket.com")) {
    return "bitbucket";
  }
  if (
    lower.includes("confluence") ||
    lower.includes("atlassian.net/wiki")
  ) {
    return "confluence";
  }
  if (
    lower.includes("drive.google.com") ||
    lower.includes("docs.google.com")
  ) {
    return "google-drive";
  }

  return null;
}

/**
 * Run all preflight checks for a given skill definition.
 *
 * The `skill` object may contain:
 *   - commands: string[]      — CLI tools that must be on PATH
 *   - npmPackages: string[]   — global npm packages required
 *   - mcpServers: string[]    — MCP servers that must be configured
 *
 * The optional `context` object may contain:
 *   - configPath: string      — path to the Claude config file
 *
 * @param {object} skill - Skill descriptor with dependency arrays.
 * @param {object} [context] - Optional runtime context.
 * @returns {Promise<{errors: string[], warnings: string[], results: object[]}>}
 */
export async function runPreflight(skill, context = {}) {
  const errors = [];
  const warnings = [];
  const results = [];

  // Check required CLI commands
  if (Array.isArray(skill.commands)) {
    for (const cmd of skill.commands) {
      const result = checkCommand(cmd);
      results.push({ type: "command", ...result });
      if (!result.ok) {
        errors.push(`Required command not found: ${cmd}`);
      }
    }
  }

  // Check required global npm packages
  if (Array.isArray(skill.npmPackages)) {
    for (const pkg of skill.npmPackages) {
      const result = checkGlobalNpmPackage(pkg);
      results.push({ type: "npmPackage", ...result });
      if (!result.ok) {
        warnings.push(`Global npm package not found: ${pkg}`);
      }
    }
  }

  // Check required MCP servers
  if (Array.isArray(skill.mcpServers)) {
    for (const server of skill.mcpServers) {
      const result = await checkMcpServer(server, context.configPath);
      results.push({ type: "mcpServer", ...result });
      if (!result.ok) {
        errors.push(`MCP server not configured: ${server}`);
      }
    }
  }

  return { errors, warnings, results };
}
