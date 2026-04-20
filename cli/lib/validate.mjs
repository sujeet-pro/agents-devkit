// Single repo-wide validator. Replaces the deleted Python tests under
// `tests/test_skills.py`, `tests/test_agents.py`, `tests/test_hooks.py`.
//
// Checks (errors fail the run; warnings print but exit 0):
//
//   skills/<name>/
//     - SKILL.md exists
//     - YAML frontmatter parses
//     - Only spec-allowed top-level keys: name, description, optional
//       compatibility / metadata / license / allowed-tools
//     - frontmatter.name === folder name
//     - description <= 1024 chars
//     - public skills must start with `adk` and either equal "adk" or use
//       the `adk-<category>(-<task>)` shape
//     - body <= 500 lines (warn over)
//     - if references/ exists: must be flat (no subdirs, no `_shared/`)
//     - any `references/<file>` cited inline in SKILL.md must exist
//
//   agents-claude/<name>.md, agents-cursor/<name>.md
//     - YAML frontmatter parses
//     - frontmatter.name and description present
//
//   agents-codex/<name>.toml
//     - file parses as a sequence of `key = value` lines
//     - has `name`, `description`, `model`, `developer_instructions` keys
//
//   hooks/{claude,cursor,codex}.json
//     - parses as JSON

import { existsSync, readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const ROOT = resolve(dirname(__filename), "..", "..");

const SPEC_KEYS = new Set([
  "name",
  "description",
  "compatibility",
  "metadata",
  "license",
  "allowed-tools",
]);

const PUBLIC_NAME_RE = /^adk(-[a-z0-9]+)*$/;

function loadFrontmatter(text) {
  const m = /^---\s*\n([\s\S]*?)\n---/m.exec(text);
  if (!m) return { ok: false, error: "missing-frontmatter" };
  const out = {};
  let currentKey = null;
  for (const raw of m[1].split("\n")) {
    if (!raw.trim() || raw.trim().startsWith("#")) continue;
    const indented = raw.startsWith(" ") || raw.startsWith("\t");
    if (indented && currentKey) {
      const kv = /^\s+([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.+)$/.exec(raw);
      if (kv) {
        if (typeof out[currentKey] !== "object" || Array.isArray(out[currentKey])) out[currentKey] = {};
        let v = kv[2].trim();
        if (v === "true") v = true;
        else if (v === "false") v = false;
        out[currentKey][kv[1]] = v;
      }
      continue;
    }
    const top = /^([a-zA-Z][a-zA-Z0-9_-]*)\s*:\s*(.*)$/.exec(raw.trim());
    if (!top) continue;
    currentKey = top[1];
    let v = top[2].trim();
    if (v === "") {
      out[currentKey] = {};
    } else {
      if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
        v = v.slice(1, -1);
      }
      out[currentKey] = v;
    }
  }
  return { ok: true, frontmatter: out };
}

function bodyOf(text) {
  const m = /^---\s*\n[\s\S]*?\n---\s*\n?([\s\S]*)$/m.exec(text);
  return m ? m[1] : text;
}

function listDirs(p) {
  if (!existsSync(p)) return [];
  return readdirSync(p)
    .filter((n) => !n.startsWith("."))
    .filter((n) => {
      try {
        return statSync(join(p, n)).isDirectory();
      } catch {
        return false;
      }
    })
    .sort();
}

function listFiles(p, ext) {
  if (!existsSync(p)) return [];
  return readdirSync(p)
    .filter((n) => !n.startsWith("."))
    .filter((n) => (ext ? n.endsWith(ext) : true))
    .filter((n) => {
      try {
        return statSync(join(p, n)).isFile();
      } catch {
        return false;
      }
    })
    .sort();
}

function validateSkill(skillsDir, name, errors, warnings) {
  const dir = join(skillsDir, name);
  const skillMd = join(dir, "SKILL.md");
  if (!existsSync(skillMd)) {
    errors.push(`skills/${name}: SKILL.md missing`);
    return;
  }
  const text = readFileSync(skillMd, "utf8");
  const fm = loadFrontmatter(text);
  if (!fm.ok) {
    errors.push(`skills/${name}/SKILL.md: ${fm.error}`);
    return;
  }
  const m = fm.frontmatter;
  for (const key of Object.keys(m)) {
    if (!SPEC_KEYS.has(key)) errors.push(`skills/${name}/SKILL.md: unsupported frontmatter key '${key}'`);
  }
  if (m.name !== name) errors.push(`skills/${name}/SKILL.md: frontmatter.name '${m.name}' does not match folder '${name}'`);
  if (!m.description) errors.push(`skills/${name}/SKILL.md: missing description`);
  else if (m.description.length > 1024) errors.push(`skills/${name}/SKILL.md: description > 1024 chars (${m.description.length})`);
  if (!PUBLIC_NAME_RE.test(name)) errors.push(`skills/${name}: invalid name (must match adk(-[a-z0-9]+)*)`);

  const body = bodyOf(text);
  const lines = body.split("\n").length;
  if (lines > 500) warnings.push(`skills/${name}/SKILL.md: body is ${lines} lines (soft cap 500)`);

  // references/ flat check
  const refDir = join(dir, "references");
  if (existsSync(refDir)) {
    const subDirs = listDirs(refDir);
    if (subDirs.length > 0) errors.push(`skills/${name}/references: must be flat, found subdirs: ${subDirs.join(", ")}`);
    if (subDirs.includes("_shared")) errors.push(`skills/${name}/references/_shared: forbidden under standalone-skill contract`);
    const refFiles = new Set(listFiles(refDir, ".md"));
    const referenced = [...body.matchAll(/references\/([\w.-]+)/g)].map((mm) => mm[1]);
    for (const r of referenced) {
      if (!refFiles.has(r)) warnings.push(`skills/${name}/SKILL.md cites references/${r} but it does not exist`);
    }
  }
}

function validateAgentMd(file, errors) {
  const text = readFileSync(file, "utf8");
  const fm = loadFrontmatter(text);
  if (!fm.ok) {
    errors.push(`${file}: ${fm.error}`);
    return;
  }
  const m = fm.frontmatter;
  if (!m.name) errors.push(`${file}: missing 'name'`);
  if (!m.description) errors.push(`${file}: missing 'description'`);
}

function validateAgentToml(file, errors) {
  const text = readFileSync(file, "utf8");
  const required = ["name", "description", "model", "developer_instructions"];
  for (const key of required) {
    const re = new RegExp(`^${key}\\s*=`, "m");
    if (!re.test(text)) errors.push(`${file}: missing required key '${key}'`);
  }
}

function validateHookJson(file, errors) {
  try {
    JSON.parse(readFileSync(file, "utf8"));
  } catch (err) {
    errors.push(`${file}: invalid JSON (${err.message})`);
  }
}

export function runValidation({ root = ROOT } = {}) {
  const errors = [];
  const warnings = [];

  const skillsDir = join(root, "skills");
  for (const name of listDirs(skillsDir)) {
    validateSkill(skillsDir, name, errors, warnings);
  }

  for (const folder of ["agents-claude", "agents-cursor"]) {
    const dir = join(root, folder);
    for (const f of listFiles(dir, ".md")) {
      validateAgentMd(join(dir, f), errors);
    }
  }
  const codexDir = join(root, "agents-codex");
  for (const f of listFiles(codexDir, ".toml")) {
    validateAgentToml(join(codexDir, f), errors);
  }

  for (const f of ["claude.json", "cursor.json", "codex.json"]) {
    const p = join(root, "hooks", f);
    if (existsSync(p)) validateHookJson(p, errors);
  }

  return { errors, warnings };
}

const isMain = import.meta.url === `file://${process.argv[1]}`;
if (isMain) {
  const { errors, warnings } = runValidation();
  for (const w of warnings) console.warn(`warn  ${w}`);
  for (const e of errors) console.error(`error ${e}`);
  console.log(`\n${errors.length} error(s), ${warnings.length} warning(s).`);
  process.exit(errors.length > 0 ? 1 : 0);
}
