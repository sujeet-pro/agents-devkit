// Regenerate `skills-manifest.json` from the current state of `skills/`.
// Replaces the deleted Python `scripts/generate-skills-manifest.py`.

import { existsSync, readFileSync, readdirSync, statSync, writeFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..", "..");

function parseFrontmatter(text) {
  const m = /^---\s*\n([\s\S]*?)\n---/m.exec(text);
  if (!m) return {};
  const out = {};
  for (const line of m[1].split("\n")) {
    const kv = /^([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.*)$/.exec(line.trim());
    if (!kv) continue;
    let val = kv[2].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    out[kv[1]] = val;
  }
  return out;
}

function classifySkill(name) {
  if (name === "adk") return { kind: "top", category: "" };
  const parts = name.split("-");
  if (parts.length === 2) return { kind: "router", category: parts[1] };
  return { kind: "task", category: parts[1] };
}

export function buildManifest({ root = ROOT, version } = {}) {
  const skillsDir = join(root, "skills");
  const names = readdirSync(skillsDir)
    .filter((n) => !n.startsWith("."))
    .filter((n) => {
      try {
        return statSync(join(skillsDir, n)).isDirectory() &&
               existsSync(join(skillsDir, n, "SKILL.md"));
      } catch {
        return false;
      }
    })
    .sort();

  const skills = names.map((name) => {
    const dir = join(skillsDir, name);
    const fm = parseFrontmatter(readFileSync(join(dir, "SKILL.md"), "utf8"));
    const { kind, category } = classifySkill(name);
    return {
      name,
      description: fm.description ?? "",
      kind,
      category,
      path: `skills/${name}`,
      invocation: `/adk:${name}`,
      has_references: existsSync(join(dir, "references")),
      has_scripts: existsSync(join(dir, "scripts")),
      has_assets: existsSync(join(dir, "assets")),
    };
  });

  const categories = {
    top: skills.filter((s) => s.kind === "top").length,
    router: skills.filter((s) => s.kind === "router").length,
    task: skills.filter((s) => s.kind === "task").length,
  };
  const adkCategories = [
    ...new Set(
      skills
        .filter((s) => s.kind === "router")
        .map((s) => s.category)
        .filter(Boolean),
    ),
  ].sort();

  let pkgVersion = version;
  if (!pkgVersion) {
    try {
      pkgVersion = JSON.parse(readFileSync(join(root, "package.json"), "utf8")).version;
    } catch {
      pkgVersion = "0.0.0";
    }
  }

  return {
    version: pkgVersion,
    generated: new Date().toISOString().slice(0, 10),
    distribution: "claude-code-plugin",
    model: "claude-plugin-skill",
    skill_count: skills.length,
    categories,
    adk_categories: adkCategories,
    skills,
  };
}

export function writeManifest({ root = ROOT, dryRun = false, log = console.log } = {}) {
  const manifest = buildManifest({ root });
  const path = join(root, "skills-manifest.json");
  const body = JSON.stringify(manifest, null, 2) + "\n";
  if (dryRun) {
    log(`[dry-run] would write ${path} (${manifest.skill_count} skills)`);
    return manifest;
  }
  writeFileSync(path, body, "utf8");
  log(`wrote ${path} (${manifest.skill_count} skills)`);
  return manifest;
}

const isMain = import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const dryRun = process.argv.includes("--dry-run") || process.argv.includes("--check");
  writeManifest({ dryRun });
}
