#!/usr/bin/env node

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const pluginsDir = join(repoRoot, "plugins");
const docsDir = join(repoRoot, "docs");
const canonicalContract = join(
  pluginsDir,
  "adk-core",
  "skills",
  "auto",
  "references",
  "interaction-contract.md",
);

const errors = [];
const warnings = [];

function readText(path) {
  return readFileSync(path, "utf8");
}

function rel(path) {
  return relative(repoRoot, path);
}

function parseFrontmatter(text) {
  const match = /^---\s*\n([\s\S]*?)\n---/u.exec(text);
  if (!match) return {};

  const data = {};
  let activeKey = null;
  let inBlockScalar = false;

  for (const rawLine of match[1].split("\n")) {
    const keyValue = /^([A-Za-z0-9_-]+):\s*(.*)$/u.exec(rawLine);
    if (keyValue) {
      activeKey = keyValue[1];
      const value = keyValue[2].trim();
      if (value === "|" || value === ">") {
        data[activeKey] = "";
        inBlockScalar = true;
      } else {
        data[activeKey] = value.replace(/^['"]|['"]$/gu, "");
        inBlockScalar = false;
      }
      continue;
    }

    if (inBlockScalar && activeKey && /^\s+/.test(rawLine)) {
      data[activeKey] = `${data[activeKey]}${data[activeKey] ? "\n" : ""}${rawLine.trimEnd()}`;
    }
  }

  return data;
}

function pluginDirs() {
  return readdirSync(pluginsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name)
    .sort();
}

function skillDirs(pluginName) {
  const dir = join(pluginsDir, pluginName, "skills");
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => join(dir, entry.name))
    .sort();
}

function agentFiles(pluginName) {
  const dir = join(pluginsDir, pluginName, "agents");
  if (!existsSync(dir)) return [];
  return readdirSync(dir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => join(dir, entry.name))
    .sort();
}

function validateScaffold() {
  for (const path of [
    join(repoRoot, "package.json"),
    join(repoRoot, "pagesmith.config.json5"),
    join(docsDir, "README.md"),
    join(docsDir, "reference", "README.md"),
  ]) {
    if (!existsSync(path)) errors.push(`Missing docs scaffold file: ${rel(path)}`);
  }
}

function validatePlugin(pluginName) {
  const manifest = join(pluginsDir, pluginName, ".claude-plugin", "plugin.json");
  if (!existsSync(manifest)) {
    errors.push(`Missing plugin manifest: ${rel(manifest)}`);
    return;
  }

  try {
    const json = JSON.parse(readText(manifest));
    if (!json.name) errors.push(`${rel(manifest)} missing name`);
    if (!json.description) errors.push(`${rel(manifest)} missing description`);
  } catch (error) {
    errors.push(`${rel(manifest)} is invalid JSON: ${error.message}`);
  }
}

function validateSkill(skillDir) {
  const skillFile = join(skillDir, "SKILL.md");
  if (!existsSync(skillFile)) {
    errors.push(`Missing SKILL.md: ${rel(skillDir)}`);
    return;
  }

  const text = readText(skillFile);
  const fm = parseFrontmatter(text);
  if (!fm.name) errors.push(`${rel(skillFile)} missing frontmatter name`);
  if (!fm.description) errors.push(`${rel(skillFile)} missing frontmatter description`);
  const phaseOnePattern = new RegExp("Phase 1\\s+\\p{Pd}\\s+(preflight|platform check)", "iu");
  if (!phaseOnePattern.test(text)) {
    warnings.push(`${rel(skillFile)} does not spell out a Phase 1 preflight`);
  }

  const contractPath = join(skillDir, "references", "interaction-contract.md");
  if (!existsSync(contractPath)) {
    errors.push(`${rel(skillDir)} missing references/interaction-contract.md`);
  }
}

function validateAgent(agentFile) {
  const fm = parseFrontmatter(readText(agentFile));
  if (!fm.name) errors.push(`${rel(agentFile)} missing frontmatter name`);
  if (!fm.description) errors.push(`${rel(agentFile)} missing frontmatter description`);
}

function validateInteractionContracts() {
  if (!existsSync(canonicalContract)) {
    errors.push(`Missing canonical interaction contract: ${rel(canonicalContract)}`);
    return;
  }

  const canonical = readText(canonicalContract);
  for (const pluginName of pluginDirs()) {
    for (const skillDir of skillDirs(pluginName)) {
      const contractPath = join(skillDir, "references", "interaction-contract.md");
      if (existsSync(contractPath) && readText(contractPath) !== canonical) {
        errors.push(`${rel(contractPath)} differs from canonical interaction contract`);
      }
    }
  }
}

function validateMcpJson(pluginName) {
  const mcpPath = join(pluginsDir, pluginName, ".mcp.json");
  if (!existsSync(mcpPath)) return;

  try {
    const json = JSON.parse(readText(mcpPath));
    if (!json.mcpServers || typeof json.mcpServers !== "object") {
      errors.push(`${rel(mcpPath)} missing mcpServers object`);
    }
  } catch (error) {
    errors.push(`${rel(mcpPath)} is invalid JSON: ${error.message}`);
  }
}

function main() {
  validateScaffold();
  for (const pluginName of pluginDirs()) {
    validatePlugin(pluginName);
    validateMcpJson(pluginName);
    for (const skillDir of skillDirs(pluginName)) validateSkill(skillDir);
    for (const agentFile of agentFiles(pluginName)) validateAgent(agentFile);
  }
  validateInteractionContracts();

  for (const warning of warnings) console.warn(`WARN ${warning}`);
  if (errors.length > 0) {
    for (const error of errors) console.error(`ERROR ${error}`);
    process.exit(1);
  }

  console.log(`validate-marketplace: ok (${warnings.length} warnings)`);
}

main();
