#!/usr/bin/env node
/**
 * Generate `docs/reference/skill-<name>.md` for every skill in `skills/`.
 *
 * Each generated file is the SKILL.md body wrapped with a docs-site
 * frontmatter (title / description / skill_name / category). Re-running
 * regenerates idempotently — the docs mirrors never drift from the SKILL.md.
 *
 * Output is byte-stable across runs so this can be wired into release
 * workflows and CI without producing noise.
 *
 * The category for each skill is detected from the manifest:
 *   - "top"     -> top router (currently just `adk`)
 *   - "router"  -> category routers (`adk-build`, `adk-plan`, etc.)
 *   - "task"    -> task skills under a category router
 *   - "standalone" -> task skills with no category router (`adk-doc-site-setup`,
 *                    `adk-adopt-ai-in-repo`)
 */

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from "node:fs";
import { join, dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(__dirname, "..", "..");
const SKILLS_DIR = join(REPO_ROOT, "skills");
const DOCS_REF_DIR = join(REPO_ROOT, "docs", "reference");
const MANIFEST_PATH = join(REPO_ROOT, "skills-manifest.json");

function parseFrontmatter(text) {
  const m = /^---\s*\n([\s\S]*?)\n---/m.exec(text);
  if (!m) return { ok: false, body: text };
  const out = {};
  for (const raw of m[1].split("\n")) {
    if (!raw.trim() || raw.trim().startsWith("#")) continue;
    const top = /^([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.*)$/.exec(raw);
    if (!top) continue;
    out[top[1]] = top[2].trim().replace(/^['"]|['"]$/g, "");
  }
  return { ok: true, frontmatter: out, body: text.slice(m[0].length).replace(/^\s*\n/, "") };
}

function escapeYamlString(s) {
  // Single-quote and double internal single-quotes per YAML spec.
  return `'${String(s).replace(/'/g, "''")}'`;
}

function loadManifestCategories() {
  const map = new Map();
  if (!existsSync(MANIFEST_PATH)) return map;
  try {
    const data = JSON.parse(readFileSync(MANIFEST_PATH, "utf8"));
    for (const s of data.skills || []) {
      let category = s.kind || "task";
      // Promote standalone task skills with no router to their own category.
      if (category === "task" && (!s.category || s.category === "")) {
        category = "standalone";
      }
      map.set(s.name, category);
    }
  } catch {
    // ignore
  }
  return map;
}

function writeIfChanged(path, contents) {
  if (existsSync(path) && readFileSync(path, "utf8") === contents) return false;
  mkdirSync(dirname(path), { recursive: true });
  writeFileSync(path, contents);
  return true;
}

function generate() {
  const categoryMap = loadManifestCategories();
  if (!existsSync(SKILLS_DIR)) {
    console.error(`skills/ not found at ${SKILLS_DIR}`);
    process.exit(1);
  }
  const skills = readdirSync(SKILLS_DIR).filter(n => statSync(join(SKILLS_DIR, n)).isDirectory()).sort();

  let written = 0;
  let unchanged = 0;
  for (const name of skills) {
    const skillFile = join(SKILLS_DIR, name, "SKILL.md");
    if (!existsSync(skillFile)) continue;
    const text = readFileSync(skillFile, "utf8");
    const fm = parseFrontmatter(text);
    if (!fm.ok || !fm.frontmatter.name || !fm.frontmatter.description) {
      console.warn(`SKIP ${name}: missing or invalid frontmatter`);
      continue;
    }
    const category = categoryMap.get(name) || "task";
    const docFrontmatter = [
      "---",
      `title: ${escapeYamlString(fm.frontmatter.name)}`,
      `description: ${escapeYamlString(fm.frontmatter.description)}`,
      `skill_name: ${fm.frontmatter.name}`,
      `category: ${category}`,
      "---",
      "",
    ].join("\n");
    const body = fm.body.replace(/\s*$/, "") + "\n";
    const out = docFrontmatter + body;
    const dest = join(DOCS_REF_DIR, `skill-${name}.md`);
    if (writeIfChanged(dest, out)) {
      written++;
    } else {
      unchanged++;
    }
  }
  console.log(`docs:skills regenerated: ${written} written, ${unchanged} unchanged`);
}

generate();
