---
title: 'generate-reference-docs.mjs'
description: 'Helper script generate-reference-docs.mjs.'
script: 'generate-reference-docs.mjs'
source: 'scripts/generate-reference-docs.mjs'
group: 'scripts'
order: 4005
---
# generate-reference-docs.mjs

Helper script generate-reference-docs.mjs.

## Source

`scripts/generate-reference-docs.mjs`

## Contents

```js
#!/usr/bin/env node
// generate-reference-docs.mjs — v3 reference-pages generator.
//
// Reads:
//   skills/adk-<name>/SKILL.md
//   agents-claude/agents/adk-agent-<name>.md
//   mcp/adk-mcp-<name>.json
//   scripts/<name>.py (+ scripts/<name>.mjs)
//   hooks/hooks.json + hooks/banner.sh
//   shared/{constitution,advisor,question-first,decision-log-schema,edit-format,plan-act-mode}.md
//   shared/{personas,workflows,input-classifiers,guidelines}/<name>.md
//   agents-cursor/, agents-codex/, agents-junie/ (env wrappers)
//
// Writes:
//   docs/reference/skills/<name>.md
//   docs/reference/agents/<name>.md
//   docs/reference/mcp/<name>.md
//   docs/reference/scripts/<name>.md
//   docs/reference/hooks.md
//   docs/reference/shared/<group>/<file>.md
//   docs/reference/agent-envs/<env>.md
//
// Idempotent: clears all generated dirs first, then re-writes.

import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const docsRefDir = join(repoRoot, "docs", "reference");

const GENERATED_DIRS = [
  "skills",
  "agents",
  "mcp",
  "scripts",
  "agent-envs",
  "shared/personas",
  "shared/workflows",
  "shared/input-classifiers",
  "shared/guidelines",
];

const ORDER_OFFSET = {
  skills: 1000,
  agents: 2000,
  mcp: 3000,
  scripts: 4000,
  "agent-envs": 5000,
  "shared/personas": 6000,
  "shared/workflows": 6100,
  "shared/input-classifiers": 6200,
  "shared/guidelines": 6300,
};

function readText(path) {
  return readFileSync(path, "utf8");
}

function writeFile(path, contents) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${contents.replace(/\s+$/u, "")}\n`);
}

function resetGeneratedDirs() {
  for (const dir of GENERATED_DIRS) {
    const fullDir = join(docsRefDir, dir);
    if (existsSync(fullDir)) rmSync(fullDir, { recursive: true, force: true });
    mkdirSync(fullDir, { recursive: true });
  }
}

function escapeYaml(value) {
  return `'${String(value ?? "").replace(/'/gu, "''").replace(/\n/gu, " ")}'`;
}

function frontmatter(fields) {
  const lines = ["---"];
  for (const [key, value] of Object.entries(fields)) {
    if (value === undefined || value === null) continue;
    lines.push(`${key}: ${typeof value === "number" ? value : escapeYaml(value)}`);
  }
  lines.push("---", "");
  return lines.join("\n");
}

function parseFrontmatter(text) {
  const match = /^---\s*\n([\s\S]*?)\n---\s*\n?/u.exec(text);
  if (!match) return { data: {}, body: text };
  const data = {};
  let activeKey = null;
  let inBlock = false;
  for (const line of match[1].split("\n")) {
    const kv = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (kv) {
      activeKey = kv[1];
      const v = kv[2].trim();
      if (v === "|" || v === ">") {
        data[activeKey] = "";
        inBlock = true;
      } else {
        data[activeKey] = v.replace(/^['"]|['"]$/g, "");
        inBlock = false;
      }
    } else if (inBlock && activeKey && /^\s+/.test(line)) {
      data[activeKey] = (data[activeKey] ? data[activeKey] + " " : "") + line.trim();
    }
  }
  return { data, body: text.slice(match[0].length) };
}

function compactDesc(value, maxLength = 220) {
  const compact = String(value ?? "").replace(/\s+/gu, " ").trim();
  if (compact.length <= maxLength) return compact;
  return `${compact.slice(0, maxLength - 3).replace(/\s+\S*$/u, "")}...`;
}

function langForFile(name) {
  if (name.endsWith(".py")) return "python";
  if (name.endsWith(".mjs") || name.endsWith(".js")) return "js";
  if (name.endsWith(".sh")) return "bash";
  if (name.endsWith(".json")) return "json";
  if (name.endsWith(".json5")) return "json5";
  if (name.endsWith(".yaml") || name.endsWith(".yml")) return "yaml";
  if (name.endsWith(".toml")) return "toml";
  return "text";
}

// ----- Skills --------------------------------------------------------------

function generateSkillPages() {
  const skillsDir = join(repoRoot, "skills");
  if (!existsSync(skillsDir)) return [];
  const entries = readdirSync(skillsDir, { withFileTypes: true })
    .filter((e) => e.isDirectory() && e.name.startsWith("adk-"))
    .sort((a, b) => a.name.localeCompare(b.name));
  const generated = [];
  for (const [i, entry] of entries.entries()) {
    const skillDir = join(skillsDir, entry.name);
    const skillMd = join(skillDir, "SKILL.md");
    if (!existsSync(skillMd)) continue;
    const text = readText(skillMd);
    const { data, body } = parseFrontmatter(text);
    const name = data.name || entry.name;
    const description = data.description || "";
    const referencesDir = join(skillDir, "references");
    const refs = existsSync(referencesDir)
      ? readdirSync(referencesDir).filter((f) => f.endsWith(".md")).sort()
      : [];
    const refsList = refs.length
      ? refs.map((r) => `- \`references/${r}\` — see [\`/${entry.name}/references/${r}\`](https://github.com/sujeet-pro/agents-devkit/blob/main/skills/${entry.name}/references/${r})`).join("\n")
      : "_(References authored on first real use of each sub-flow.)_";
    const md = `${frontmatter({
      title: name,
      description: compactDesc(description),
      skill: name,
      source: relative(repoRoot, skillMd),
      group: "skills",
      order: ORDER_OFFSET.skills + i,
    })}# ${name}

${description}

## Source

\`${relative(repoRoot, skillMd)}\`

## Frontmatter

\`\`\`yaml
${(text.match(/^---\s*\n([\s\S]*?)\n---/) || ["", ""])[1]}
\`\`\`

## Workflow body

${body.trim()}

## References shipped

${refsList}
`;
    writeFile(join(docsRefDir, "skills", `${entry.name}.md`), md);
    generated.push({ name: entry.name, description, file: `${entry.name}.md` });
  }
  return generated;
}

// ----- Agents --------------------------------------------------------------

function generateAgentPages() {
  const dir = join(repoRoot, "agents-claude", "agents");
  if (!existsSync(dir)) return [];
  const files = readdirSync(dir)
    .filter((f) => f.startsWith("adk-agent-") && f.endsWith(".md"))
    .sort();
  const generated = [];
  for (const [i, file] of files.entries()) {
    const full = join(dir, file);
    const text = readText(full);
    const { data, body } = parseFrontmatter(text);
    const name = data.name || basename(file, ".md");
    const description = data.description || "";
    const md = `${frontmatter({
      title: name,
      description: compactDesc(description),
      agent: name,
      source: relative(repoRoot, full),
      group: "agents",
      order: ORDER_OFFSET.agents + i,
    })}# ${name}

${description}

## Source

\`${relative(repoRoot, full)}\`

## Frontmatter

\`\`\`yaml
${(text.match(/^---\s*\n([\s\S]*?)\n---/) || ["", ""])[1]}
\`\`\`

## Body

${body.trim()}
`;
    writeFile(join(docsRefDir, "agents", file), md);
    generated.push({ name, description, file });
  }
  return generated;
}

// ----- MCPs ----------------------------------------------------------------

function extractEnvRefs(value) {
  const text = JSON.stringify(value);
  const refs = new Set();
  for (const m of text.matchAll(/\$\{([A-Z0-9_]+)(?::-[^}]*)?\}/g)) refs.add(m[1]);
  return [...refs].sort();
}

function generateMcpPages() {
  const dir = join(repoRoot, "mcp");
  if (!existsSync(dir)) return [];
  const files = readdirSync(dir)
    .filter((f) => f.startsWith("adk-mcp-") && f.endsWith(".json"))
    .sort();
  const generated = [];
  for (const [i, file] of files.entries()) {
    const full = join(dir, file);
    const cfg = JSON.parse(readText(full));
    const name = cfg.name || basename(file, ".json");
    const description = cfg.description || "";
    const envs = extractEnvRefs(cfg);
    const md = `${frontmatter({
      title: name,
      description: compactDesc(description),
      mcp: name,
      source: relative(repoRoot, full),
      group: "mcp",
      order: ORDER_OFFSET.mcp + i,
    })}# ${name}

${description}

## Source

\`${relative(repoRoot, full)}\`

## Environment variables referenced

${envs.length ? envs.map((e) => `- \`${e}\``).join("\n") : "_(none)_"}

## Configuration

\`\`\`json
${JSON.stringify(cfg, null, 2)}
\`\`\`
`;
    writeFile(join(docsRefDir, "mcp", file.replace(/\.json$/, ".md")), md);
    generated.push({ name, description, file: file.replace(/\.json$/, ".md") });
  }
  return generated;
}

// ----- Scripts -------------------------------------------------------------

function generateScriptPages() {
  const dir = join(repoRoot, "scripts");
  if (!existsSync(dir)) return [];
  const files = readdirSync(dir)
    .filter((f) => /\.(py|mjs)$/.test(f))
    .sort();
  const generated = [];
  for (const [i, file] of files.entries()) {
    const full = join(dir, file);
    const text = readText(full);
    // Pull the docstring (Python) or top comment (JS)
    let summary = "";
    const pyDoc = /^#!.*\n+"""([\s\S]*?)"""/m.exec(text);
    const jsDoc = /^#!.*\n+\/\*\*([\s\S]*?)\*\//m.exec(text);
    if (pyDoc) summary = pyDoc[1].split("\n")[0].trim();
    else if (jsDoc) summary = jsDoc[1].split("\n").map((l) => l.replace(/^\s*\*\s?/, "")).filter(Boolean)[0] || "";
    if (!summary) summary = `Helper script ${file}.`;
    const md = `${frontmatter({
      title: file,
      description: compactDesc(summary),
      script: file,
      source: relative(repoRoot, full),
      group: "scripts",
      order: ORDER_OFFSET.scripts + i,
    })}# ${file}

${summary}

## Source

\`${relative(repoRoot, full)}\`

## Contents

\`\`\`${langForFile(file)}
${text}
\`\`\`
`;
    writeFile(join(docsRefDir, "scripts", file.replace(/\.(py|mjs)$/, ".md")), md);
    generated.push({ name: file, description: summary, file: file.replace(/\.(py|mjs)$/, ".md") });
  }
  return generated;
}

// ----- Hooks ---------------------------------------------------------------

function generateHooksPage() {
  const hooksJson = join(repoRoot, "hooks", "hooks.json");
  const bannerSh = join(repoRoot, "hooks", "banner.sh");
  if (!existsSync(hooksJson)) return null;
  const json = JSON.parse(readText(hooksJson));
  const banner = existsSync(bannerSh) ? readText(bannerSh) : "";
  const md = `${frontmatter({
    title: "Hooks",
    description: "Deterministic enforcement of the constitution. PreToolUse:Bash safety, PostToolUse:Edit validator, SessionStart banner. Wired into ~/.claude/settings.json by install.sh.",
    source: "hooks/",
    group: "hooks",
    order: 5500,
  })}# Hooks

Deterministic enforcement of \`shared/constitution.md\`. Three events:

- **PreToolUse:Bash** — blocks force-push, hard-reset on protected branches, \`rm -rf $HOME\`, unrequested PR merges, writes to \`~/.config/adk/learning/archive/\`, \`--no-verify\` bypasses.
- **PostToolUse:Edit\\|Write** — validates SKILL.md frontmatter on writes; touches \`.temp/<task-slug>/.last-modified\`; refuses raw-token writes to \`~/.config/adk/overrides.yaml\`.
- **SessionStart** — prints the adk status banner.

\`install.sh\` merges these into \`~/.claude/settings.json\` with an \`_adk_managed: true\` tag so they're idempotent and removable on uninstall.

## hooks/hooks.json

\`\`\`json
${JSON.stringify(json, null, 2)}
\`\`\`

## hooks/banner.sh

\`\`\`bash
${banner}
\`\`\`
`;
  writeFile(join(docsRefDir, "hooks.md"), md);
  return { file: "hooks.md" };
}

// ----- Shared --------------------------------------------------------------

function generateSharedPages() {
  const out = {};
  const sharedDir = join(repoRoot, "shared");
  if (!existsSync(sharedDir)) return out;
  const topLevel = [
    "constitution.md",
    "advisor.md",
    "question-first.md",
    "decision-log-schema.md",
    "edit-format.md",
    "plan-act-mode.md",
  ];
  for (const [i, f] of topLevel.entries()) {
    const full = join(sharedDir, f);
    if (!existsSync(full)) continue;
    const text = readText(full);
    const title = `shared/${f.replace(/\.md$/, "")}`;
    const firstLine = text.split("\n").find((l) => l.trim() && !l.startsWith("#") && !l.startsWith(">")) || "";
    const md = `${frontmatter({
      title,
      description: compactDesc(firstLine),
      source: `shared/${f}`,
      group: "shared",
      order: 5600 + i,
    })}# ${title}

> Source: \`shared/${f}\`

${text}
`;
    writeFile(join(docsRefDir, "shared", f), md);
    out[f] = `shared/${f}`;
  }
  // Subgroups
  const subgroups = ["personas", "workflows", "input-classifiers", "guidelines"];
  for (const group of subgroups) {
    const groupDir = join(sharedDir, group);
    if (!existsSync(groupDir)) continue;
    const files = readdirSync(groupDir).filter((f) => f.endsWith(".md")).sort();
    out[group] = [];
    for (const [i, f] of files.entries()) {
      const full = join(groupDir, f);
      const text = readText(full);
      const firstLine = text.split("\n").find((l) => l.trim() && !l.startsWith("#") && !l.startsWith(">")) || "";
      const md = `${frontmatter({
        title: `${group}/${f.replace(/\.md$/, "")}`,
        description: compactDesc(firstLine),
        source: `shared/${group}/${f}`,
        group: `shared-${group}`,
        order: ORDER_OFFSET[`shared/${group}`] + i,
      })}# shared/${group}/${f.replace(/\.md$/, "")}

> Source: \`shared/${group}/${f}\`

${text}
`;
      writeFile(join(docsRefDir, "shared", group, f), md);
      out[group].push(f);
    }
  }
  return out;
}

// ----- Per-agent-env wrappers ---------------------------------------------

function generateAgentEnvPages() {
  const envs = ["claude", "cursor", "codex", "junie"];
  for (const [i, env] of envs.entries()) {
    const dir = join(repoRoot, `agents-${env}`);
    if (!existsSync(dir)) continue;
    const readme = join(dir, "README.md");
    let bodyExtra = "";
    if (existsSync(readme)) {
      bodyExtra = `\n\n## README\n\n${readText(readme)}`;
    }
    // List the wrapper files installed for this env
    function listDir(sub) {
      const p = join(dir, sub);
      if (!existsSync(p)) return [];
      return readdirSync(p).filter((f) => !f.startsWith(".")).sort();
    }
    const sections = [];
    const agentFiles = listDir("agents");
    if (agentFiles.length) sections.push(`### Subagents (${agentFiles.length})\n\n${agentFiles.map((f) => `- \`agents-${env}/agents/${f}\``).join("\n")}`);
    const cmdFiles = listDir("commands");
    if (cmdFiles.length) sections.push(`### Commands (${cmdFiles.length})\n\n${cmdFiles.map((f) => `- \`agents-${env}/commands/${f}\``).join("\n")}`);
    const ruleFiles = listDir("rules");
    if (ruleFiles.length) sections.push(`### Rules (${ruleFiles.length})\n\n${ruleFiles.map((f) => `- \`agents-${env}/rules/${f}\``).join("\n")}`);
    const promptFiles = listDir("prompts");
    if (promptFiles.length) sections.push(`### Prompts (${promptFiles.length})\n\n${promptFiles.map((f) => `- \`agents-${env}/prompts/${f}\``).join("\n")}`);
    const templates = readdirSync(dir).filter((f) => f.endsWith(".tmpl") || f.endsWith(".append"));
    if (templates.length) sections.push(`### Append templates\n\n${templates.map((f) => `- \`agents-${env}/${f}\``).join("\n")}`);

    const md = `${frontmatter({
      title: `agents-${env}`,
      description: `adk wrappers for ${env}. See agents-${env}/README.md (if present) for capability status.`,
      env,
      source: `agents-${env}/`,
      group: "agent-envs",
      order: ORDER_OFFSET["agent-envs"] + i,
    })}# agents-${env}

Wrappers that install adk into \`${env}\` at user level. Installed via \`./install.sh --target ${env}\`.

${sections.join("\n\n")}${bodyExtra}
`;
    writeFile(join(docsRefDir, "agent-envs", `${env}.md`), md);
  }
}

// ----- Main ---------------------------------------------------------------

function main() {
  resetGeneratedDirs();
  const skills = generateSkillPages();
  const agents = generateAgentPages();
  const mcps = generateMcpPages();
  const scripts = generateScriptPages();
  generateHooksPage();
  generateSharedPages();
  generateAgentEnvPages();

  console.log(`generated:`);
  console.log(`  skills:  ${skills.length}`);
  console.log(`  agents:  ${agents.length}`);
  console.log(`  mcp:     ${mcps.length}`);
  console.log(`  scripts: ${scripts.length}`);
  console.log(`  hooks:   1`);
  console.log(`  shared:  shared/, shared/personas/, shared/workflows/, shared/input-classifiers/, shared/guidelines/`);
  console.log(`  agent-envs: claude / cursor / codex / junie`);
}

main();

```
