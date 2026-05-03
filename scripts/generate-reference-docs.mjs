#!/usr/bin/env node

import {
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const pluginsDir = join(repoRoot, "plugins");
const docsRefDir = join(repoRoot, "docs", "reference");
const marketplacePath = join(repoRoot, ".claude-plugin", "marketplace.json");
let pluginOrder = new Map();

const generatedDirs = ["plugins", "skills", "agents", "mcp", "bin"].map((name) =>
  join(docsRefDir, name),
);

function readText(path) {
  return readFileSync(path, "utf8");
}

function writeFile(path, contents) {
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, `${contents.replace(/\s+$/u, "")}\n`);
}

function resetGeneratedDirs() {
  for (const dir of generatedDirs) {
    if (existsSync(dir)) rmSync(dir, { recursive: true, force: true });
    mkdirSync(dir, { recursive: true });
  }
}

function escapeYaml(value) {
  return `'${String(value ?? "").replace(/'/gu, "''").replace(/\n/gu, " ")}'`;
}

function frontmatter(fields) {
  const lines = ["---"];
  for (const [key, value] of Object.entries(fields)) {
    lines.push(`${key}: ${typeof value === "number" ? value : escapeYaml(value)}`);
  }
  lines.push("---", "");
  return lines.join("\n");
}

function stripQuotes(value) {
  return value.replace(/^['"]|['"]$/gu, "");
}

function parseMarkdownFrontmatter(text) {
  const match = /^---\s*\n([\s\S]*?)\n---\s*\n?/u.exec(text);
  if (!match) {
    return { data: {}, body: text };
  }

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
        data[activeKey] = stripQuotes(value);
        inBlockScalar = false;
      }
      continue;
    }

    if (inBlockScalar && activeKey && /^\s+/.test(rawLine)) {
      data[activeKey] = `${data[activeKey]}${data[activeKey] ? "\n" : ""}${rawLine.trimEnd()}`;
    }
  }

  return {
    data,
    body: text.slice(match[0].length),
  };
}

function slugFromPath(path) {
  return path.replace(/[^a-zA-Z0-9._-]+/gu, "-").replace(/^-|-$/gu, "").toLowerCase();
}

function linkFor(kind, file) {
  return `./${kind}/${file}`;
}

function listPluginDirs() {
  const dirs = new Set(
    readdirSync(pluginsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
      .map((entry) => entry.name),
  );

  if (existsSync(marketplacePath)) {
    const marketplace = JSON.parse(readText(marketplacePath));
    const ordered = (marketplace.plugins ?? [])
      .map((plugin) => plugin.name)
      .filter((name) => dirs.has(name));
    const leftovers = [...dirs].filter((name) => !ordered.includes(name)).sort();
    return [...ordered, ...leftovers];
  }

  return [...dirs].sort();
}

function orderFor(pluginName, category, index = 0) {
  const pluginIndex = pluginOrder.get(pluginName) ?? 99;
  const categoryOrder = {
    skills: 1,
    agents: 2,
    mcp: 3,
    bin: 4,
    plugins: 5,
  }[category] ?? 9;
  return pluginIndex * 1000 + categoryOrder * 100 + index;
}

function groupFor(pluginName, categoryTitle) {
  if (categoryTitle === "Plugin") return "Plugins";
  return `${shortPluginName(pluginName)}-${typeSlug(categoryTitle)}`;
}

function sortByPluginThenName(a, b) {
  const pluginDelta = (pluginOrder.get(a.plugin) ?? 99) - (pluginOrder.get(b.plugin) ?? 99);
  if (pluginDelta !== 0) return pluginDelta;
  return a.name.localeCompare(b.name);
}

function shortPluginName(pluginName) {
  return pluginName.replace(/^adk-/u, "");
}

function typeSlug(categoryTitle) {
  const aliases = {
    "MCP Servers": "mcp",
    "Helper Binaries": "bin",
    Plugin: "plugins",
  };
  return slugFromPath(aliases[categoryTitle] ?? categoryTitle.toLowerCase());
}

function pageSlug(docFile) {
  return docFile.replace(/\.md$/u, "");
}

function referenceSlug(kind, docFile) {
  return `${kind}/${pageSlug(docFile)}`;
}

function findSkillFiles(pluginName) {
  const skillsDir = join(pluginsDir, pluginName, "skills");
  if (!existsSync(skillsDir)) return [];

  return readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => {
      const file = join(skillsDir, entry.name, "SKILL.md");
      return existsSync(file) ? { name: entry.name, file } : null;
    })
    .filter(Boolean)
    .sort((a, b) => a.name.localeCompare(b.name));
}

function findAgentFiles(pluginName) {
  const agentsDir = join(pluginsDir, pluginName, "agents");
  if (!existsSync(agentsDir)) return [];

  return readdirSync(agentsDir, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith(".md"))
    .map((entry) => ({ name: entry.name.replace(/\.md$/u, ""), file: join(agentsDir, entry.name) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

function findBinFiles(pluginName) {
  const binDir = join(pluginsDir, pluginName, "bin");
  if (!existsSync(binDir)) return [];

  return readdirSync(binDir, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => ({ name: entry.name, file: join(binDir, entry.name) }))
    .sort((a, b) => a.name.localeCompare(b.name));
}

function extractEnvRefs(value) {
  const refs = new Set();
  const text = JSON.stringify(value);
  for (const match of text.matchAll(/\$\{([A-Z0-9_]+)(?::-[^}]*)?\}/gu)) {
    refs.add(match[1]);
  }
  return [...refs].sort();
}

function codeBlockLanguage(file) {
  if (file.endsWith(".js") || file.endsWith(".mjs")) return "js";
  if (file.endsWith(".sh")) return "bash";
  if (file.endsWith(".py")) return "python";
  return "text";
}

function compactDescription(value, maxLength = 220) {
  const compact = String(value ?? "").replace(/\s+/gu, " ").trim();
  if (compact.length <= maxLength) return compact;
  return `${compact.slice(0, maxLength - 3).replace(/\s+\S*$/u, "")}...`;
}

function generatePluginDocs(pluginName, allSkills, allAgents, allBins) {
  const manifestPath = join(pluginsDir, pluginName, ".claude-plugin", "plugin.json");
  if (!existsSync(manifestPath)) return null;

  const manifest = JSON.parse(readText(manifestPath));
  const skills = allSkills.filter((skill) => skill.plugin === pluginName);
  const agents = allAgents.filter((agent) => agent.plugin === pluginName);
  const bins = allBins.filter((bin) => bin.plugin === pluginName);
  const filename = `${pluginName}.md`;

  const deps = (manifest.dependencies ?? [])
    .map((dep) => `- \`${dep.name}\` ${dep.version ?? ""}`.trim())
    .join("\n");

  const body = `${frontmatter({
    title: manifest.name ?? pluginName,
    description: manifest.description ?? "",
    plugin: pluginName,
    source: relative(repoRoot, manifestPath),
    group: groupFor(pluginName, "Plugin"),
    order: orderFor(pluginName, "plugins"),
  })}# ${manifest.name ?? pluginName}

${manifest.description ?? ""}

## Source

\`${relative(repoRoot, manifestPath)}\`

## Dependencies

${deps || "None declared."}

## Skills

${skills.map((skill) => `- [\`${skill.name}\`](../skills/${skill.docFile})`).join("\n") || "No skills."}

## Agents

${agents.map((agent) => `- [\`${agent.name}\`](../agents/${agent.docFile})`).join("\n") || "No agents."}

## Helper Binaries

${bins.map((bin) => `- [\`${bin.name}\`](../bin/${bin.docFile})`).join("\n") || "No helper binaries."}
`;

  writeFile(join(docsRefDir, "plugins", filename), body);
  return { name: manifest.name ?? pluginName, plugin: pluginName, docFile: filename, description: manifest.description ?? "" };
}

function generateSkillDocs(pluginName) {
  const skills = [];
  for (const [skillIndex, skill] of findSkillFiles(pluginName).entries()) {
    const text = readText(skill.file);
    const parsed = parseMarkdownFrontmatter(text);
    const name = parsed.data.name || skill.name;
    const docFile = `${pluginName}-${slugFromPath(name)}.md`;
    const source = relative(repoRoot, skill.file);
    const title = `${pluginName}:${name}`;
    const description = parsed.data.description || `Skill ${name} from ${pluginName}.`;
    const body = `${frontmatter({
      title,
      description,
      plugin: pluginName,
      skill: name,
      source,
      group: groupFor(pluginName, "Skills"),
      order: orderFor(pluginName, "skills", skillIndex + 1),
    })}# ${title}

## Source

\`${source}\`

## Skill Body

${parsed.body.trim()}
`;

    writeFile(join(docsRefDir, "skills", docFile), body);
    skills.push({ name, plugin: pluginName, docFile, source, description });
  }
  return skills;
}

function generateAgentDocs(pluginName) {
  const agents = [];
  for (const [agentIndex, agent] of findAgentFiles(pluginName).entries()) {
    const text = readText(agent.file);
    const parsed = parseMarkdownFrontmatter(text);
    const name = parsed.data.name || agent.name;
    const docFile = `${pluginName}-${slugFromPath(name)}.md`;
    const source = relative(repoRoot, agent.file);
    const title = `${pluginName}:${name}`;
    const description = parsed.data.description || `Agent ${name} from ${pluginName}.`;
    const body = `${frontmatter({
      title,
      description,
      plugin: pluginName,
      agent: name,
      source,
      group: groupFor(pluginName, "Agents"),
      order: orderFor(pluginName, "agents", agentIndex + 1),
    })}# ${title}

## Source

\`${source}\`

## Agent Body

${parsed.body.trim()}
`;

    writeFile(join(docsRefDir, "agents", docFile), body);
    agents.push({ name, plugin: pluginName, docFile, source, description });
  }
  return agents;
}

function generateMcpDocs(pluginName) {
  const mcpPath = join(pluginsDir, pluginName, ".mcp.json");
  if (!existsSync(mcpPath)) return [];

  const json = JSON.parse(readText(mcpPath));
  const servers = Object.entries(json.mcpServers ?? {});
  const docs = [];

  for (const [serverIndex, [name, server]] of servers.entries()) {
    const docFile = `${pluginName}-${slugFromPath(name)}.md`;
    const source = relative(repoRoot, mcpPath);
    const envRefs = extractEnvRefs(server);
    const body = `${frontmatter({
      title: `${pluginName}:${name}`,
      description: server.description ?? `MCP server ${name} from ${pluginName}.`,
      plugin: pluginName,
      mcp: name,
      source,
      group: groupFor(pluginName, "MCP Servers"),
      order: orderFor(pluginName, "mcp", serverIndex + 1),
    })}# ${pluginName}:${name}

${server.description ?? ""}

## Source

\`${source}\`

## Environment Variables

${envRefs.map((envName) => `- \`${envName}\``).join("\n") || "None declared."}

## Configuration

\`\`\`json
${JSON.stringify({ [name]: server }, null, 2)}
\`\`\`
`;

    writeFile(join(docsRefDir, "mcp", docFile), body);
    docs.push({ name, plugin: pluginName, docFile, source, description: server.description ?? "" });
  }

  return docs;
}

function generateBinDocs(pluginName) {
  const docs = [];
  for (const [binIndex, bin] of findBinFiles(pluginName).entries()) {
    const text = readText(bin.file);
    const docFile = `${pluginName}-${slugFromPath(bin.name)}.md`;
    const source = relative(repoRoot, bin.file);
    const language = codeBlockLanguage(bin.file);
    const body = `${frontmatter({
      title: `${pluginName}:${bin.name}`,
      description: `Helper binary ${bin.name} from ${pluginName}.`,
      plugin: pluginName,
      binary: bin.name,
      source,
      group: groupFor(pluginName, "Helper Binaries"),
      order: orderFor(pluginName, "bin", binIndex + 1),
    })}# ${pluginName}:${bin.name}

## Source

\`${source}\`

## Contents

\`\`\`${language}
${text.trim()}
\`\`\`
`;

    writeFile(join(docsRefDir, "bin", docFile), body);
    docs.push({ name: bin.name, plugin: pluginName, docFile, source, description: "" });
  }
  return docs;
}

function writeIndex(kind, title, description, items) {
  const grouped = new Map();
  for (const item of items) {
    const key = item.plugin ?? "marketplace";
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(item);
  }

  const sections = [...grouped.entries()]
    .sort(([a], [b]) => (pluginOrder.get(a) ?? 99) - (pluginOrder.get(b) ?? 99) || a.localeCompare(b))
    .map(([plugin, pluginItems]) => {
      const rows = pluginItems
        .sort(sortByPluginThenName)
        .map((item) => {
          const summary = compactDescription(item.description);
          return `- [\`${item.name}\`](${item.docFile})${summary ? ` - ${summary}` : ""}`;
        })
        .join("\n");
      return `## ${plugin}\n\n${rows}`;
    })
    .join("\n\n");

  writeFile(
    join(docsRefDir, kind, "README.md"),
    `${frontmatter({ title, description })}# ${title}

${description}

${sections || "No generated items."}
`,
  );
}

function writeSectionMeta(filePath, displayName, items, series) {
  const formattedItems = items.map((item) => `    "${item}"`).join(",\n");
  const formattedSeries = series
    .map((group) => {
      const articles = group.articles.map((article) => `        "${article}"`).join(",\n");
      return `    {
      slug: "${group.slug}",
      displayName: "${group.displayName}",
      articles: [
${articles}
      ],
    }`;
    })
    .join(",\n");

  writeFile(
    filePath,
    `{
  displayName: "${displayName}",
  orderBy: "manual",
  collapsed: false,
  items: [
${formattedItems}
  ],
  series: [
${formattedSeries}
  ],
}`,
  );
}

function buildMetaSeries(kind, title, items) {
  if (kind === "plugins") {
    const orderedItems = [...items]
      .sort(sortByPluginThenName)
      .map((item) => pageSlug(item.docFile));
    return {
      orderedItems,
      series: [
        {
          slug: "plugins",
          displayName: "Plugins",
          articles: orderedItems,
        },
      ],
    };
  }

  const series = [];
  const orderedItems = [];
  for (const pluginName of pluginOrder.keys()) {
    const pluginItems = items
      .filter((item) => item.plugin === pluginName)
      .sort(sortByPluginThenName);
    if (!pluginItems.length) continue;

    const type = typeSlug(title);
    series.push({
      slug: `${shortPluginName(pluginName)}-${type}`,
      displayName: `${shortPluginName(pluginName)}-${type}`,
      articles: pluginItems.map((item) => pageSlug(item.docFile)),
    });
    orderedItems.push(...pluginItems.map((item) => pageSlug(item.docFile)));
  }
  return { orderedItems, series };
}

function writeCategoryMeta(kind, title, items) {
  const { orderedItems, series } = buildMetaSeries(kind, title, items);
  writeSectionMeta(join(docsRefDir, kind, "meta.json5"), title, orderedItems, series);
}

function writeReferenceMeta({ plugins, skills, agents, mcp, bins }) {
  const categories = [
    { kind: "plugins", title: "Plugins", items: plugins },
    { kind: "skills", title: "Skills", items: skills },
    { kind: "agents", title: "Agents", items: agents },
    { kind: "mcp", title: "MCP Servers", items: mcp },
    { kind: "bin", title: "Helper Binaries", items: bins },
  ];
  const items = ["marketplace"];
  const series = [];

  for (const category of categories) {
    const { orderedItems, series: categorySeries } = buildMetaSeries(
      category.kind,
      category.title,
      category.items,
    );
    items.push(category.kind, ...orderedItems.map((item) => `${category.kind}/${item}`));
    series.push(
      ...categorySeries.map((group) => ({
        ...group,
        articles: group.articles.map((article) => referenceSlug(category.kind, `${article}.md`)),
      })),
    );
  }

  writeSectionMeta(join(docsRefDir, "meta.json5"), "Reference", items, series);
}

function renderItemList(kind, items) {
  if (!items.length) return "None.";
  return items
    .sort(sortByPluginThenName)
    .map((item) => {
      const summary = compactDescription(item.description, 160);
      return `- [\`${item.name}\`](./${kind}/${item.docFile})${summary ? ` - ${summary}` : ""}`;
    })
    .join("\n");
}

function writeReferenceOverview({ plugins, skills, agents, mcp, bins }) {
  const sections = [...pluginOrder.keys()]
    .map((pluginName) => {
      const pluginDocs = plugins.filter((item) => item.plugin === pluginName);
      const skillDocs = skills.filter((item) => item.plugin === pluginName);
      const agentDocs = agents.filter((item) => item.plugin === pluginName);
      const mcpDocs = mcp.filter((item) => item.plugin === pluginName);
      const binDocs = bins.filter((item) => item.plugin === pluginName);

      return `## ${pluginName}

### Skills

${renderItemList("skills", skillDocs)}

### Agents

${renderItemList("agents", agentDocs)}

### MCP Servers

${renderItemList("mcp", mcpDocs)}

### Helper Binaries

${renderItemList("bin", binDocs)}

### Plugin Manifest

${renderItemList("plugins", pluginDocs)}`;
    })
    .join("\n\n");

  writeFile(
    join(docsRefDir, "README.md"),
    `${frontmatter({
      title: "Reference",
      description: "Generated reference grouped by plugin, then by component type: skills, agents, MCP servers, helper binaries, and plugin manifests.",
    })}# Reference

This section is generated from source files in \`plugins/\` and \`.claude-plugin/marketplace.json\`.

The reference is organized plugin-first. Plugin overview pages live under the \`Plugins\` series. Component pages use plugin/type series groups (for example, \`core-skills\`), ordered by marketplace plugin order and then by component type: skills, agents, MCP servers, helper binaries, plugin manifests.

Run this command after changing source artifacts:

\`\`\`bash
npm run docs:reference
\`\`\`

${sections}
`,
  );
}

function writeMarketplacePage() {
  if (!existsSync(marketplacePath)) return;

  const marketplace = JSON.parse(readText(marketplacePath));
  const body = `${frontmatter({
    title: "Marketplace Manifest",
    description: marketplace.metadata?.description ?? "",
    source: relative(repoRoot, marketplacePath),
  })}# Marketplace Manifest

${marketplace.metadata?.description ?? ""}

## Source

\`${relative(repoRoot, marketplacePath)}\`

## Plugins

${(marketplace.plugins ?? []).map((plugin) => `- [\`${plugin.name}\`](./plugins/${plugin.name}.md) - ${plugin.description}`).join("\n")}
`;

  writeFile(join(docsRefDir, "marketplace.md"), body);
}

function main() {
  if (!existsSync(pluginsDir)) {
    throw new Error(`plugins directory not found: ${pluginsDir}`);
  }

  resetGeneratedDirs();

  const pluginNames = listPluginDirs();
  pluginOrder = new Map(pluginNames.map((name, index) => [name, index]));
  const allSkills = pluginNames.flatMap(generateSkillDocs);
  const allAgents = pluginNames.flatMap(generateAgentDocs);
  const allMcp = pluginNames.flatMap(generateMcpDocs);
  const allBins = pluginNames.flatMap(generateBinDocs);
  const allPlugins = pluginNames
    .map((pluginName) => generatePluginDocs(pluginName, allSkills, allAgents, allBins))
    .filter(Boolean);

  writeIndex("plugins", "Plugins", "Generated reference pages for marketplace plugin manifests.", allPlugins);
  writeIndex("skills", "Skills", "Generated reference pages for every SKILL.md shipped by the marketplace.", allSkills);
  writeIndex("agents", "Agents", "Generated reference pages for every subagent persona shipped by the marketplace.", allAgents);
  writeIndex("mcp", "MCP Servers", "Generated reference pages for shipped plugin-local MCP servers.", allMcp);
  writeIndex("bin", "Helper Binaries", "Generated reference pages for executable helper files shipped by plugins.", allBins);
  writeCategoryMeta("plugins", "Plugins", allPlugins);
  writeCategoryMeta("skills", "Skills", allSkills);
  writeCategoryMeta("agents", "Agents", allAgents);
  writeCategoryMeta("mcp", "MCP Servers", allMcp);
  writeCategoryMeta("bin", "Helper Binaries", allBins);
  writeReferenceMeta({ plugins: allPlugins, skills: allSkills, agents: allAgents, mcp: allMcp, bins: allBins });
  writeReferenceOverview({ plugins: allPlugins, skills: allSkills, agents: allAgents, mcp: allMcp, bins: allBins });
  writeMarketplacePage();

  console.log(
    `docs:reference generated ${allPlugins.length} plugins, ${allSkills.length} skills, ${allAgents.length} agents, ${allMcp.length} MCP servers, ${allBins.length} helper binaries`,
  );
}

main();
