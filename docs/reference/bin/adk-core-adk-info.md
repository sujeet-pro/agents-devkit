---
title: 'adk-core:adk-info'
description: 'Helper binary adk-info from adk-core.'
plugin: 'adk-core'
binary: 'adk-info'
source: 'plugins/adk-core/bin/adk-info'
group: 'core-bin'
order: 401
---
# adk-core:adk-info

## Source

`plugins/adk-core/bin/adk-info`

## Contents

```text
#!/usr/bin/env node
/**
 * adk-info — read & merge ~/.config/adk/*.md into structured JSON for skills to consume.
 *
 * Usage:
 *   adk-info                   # dump merged config as JSON
 *   adk-info <topic>           # dump one topic as JSON
 *   adk-info <topic> <key>     # dump one key as JSON
 *   adk-info --check           # validate every file's schema; exit non-zero on errors
 *   adk-info --missing         # list keys that skills want but aren't set
 *   adk-info --resolve-env     # also expand ${ENV_VAR} placeholders (default: don't print secrets)
 *
 * Files: ~/.config/adk/<topic>.md
 *   Each file is markdown with a YAML front-matter block at the top:
 *     ---
 *     key: value
 *     nested:
 *       sub: value
 *     ---
 *     (free-form notes after)
 *
 *   Values may use ${ENV_VAR} placeholders. Without --resolve-env, the literal
 *   placeholder is returned (for safe display). With --resolve-env, the env value
 *   is substituted; if the env var is unset, the field is reported as "<unset>".
 *
 * Privacy:
 *   - Without --resolve-env, this script NEVER prints env-var values (they may be secrets).
 *   - The `info.md` `name` and `email` fields are plaintext (intentional).
 */

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");

const CONFIG_DIR = process.env.ADK_CONFIG_DIR || path.join(os.homedir(), ".config", "adk");

const args = process.argv.slice(2);
const flags = new Set(args.filter((a) => a.startsWith("--")));
const positional = args.filter((a) => !a.startsWith("--"));
const RESOLVE_ENV = flags.has("--resolve-env");
const CHECK = flags.has("--check");
const MISSING = flags.has("--missing");

const REQUIRED_FIELDS = {
  info: ["name", "email"],
  repos: ["repos"],
};

const RECOMMENDED_FIELDS = {
  info: ["role", "default_editor"],
  repos: ["defaults.base_branch"],
  github: ["default_org", "merge_method"],
  datadog: ["site", "default_env", "default_window"],
  mixpanel: ["project_id"],
  statsig: ["project", "default_environment"],
  snowflake: ["account", "default_warehouse", "default_role"],
  slack: ["incident_channel"],
  review: ["severity_bar"],
  docs: ["default_confluence_space", "default_gdrive_folder_id"],
};

function parseFrontmatter(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return {};
  return parseYaml(m[1]);
}

function parseYaml(src) {
  // Minimal YAML parser supporting the schemas in plan/01-meta-info.md:
  //   scalars, nested maps (2-space indent), inline arrays [a, b, c],
  //   and one-level lists of maps under a key (- key: value).
  const lines = src.split(/\r?\n/);
  const root = {};
  const stack = [{ indent: -1, obj: root }];

  function setOnTop(key, value) {
    const top = stack[stack.length - 1].obj;
    if (Array.isArray(top)) {
      // top is an array; the last element is the map we are filling.
      const last = top[top.length - 1];
      last[key] = value;
    } else {
      top[key] = value;
    }
  }

  function topObj() {
    const top = stack[stack.length - 1].obj;
    if (Array.isArray(top)) return top[top.length - 1];
    return top;
  }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    if (!raw.trim() || raw.trim().startsWith("#")) continue;
    const indent = raw.match(/^ */)[0].length;
    const line = raw.slice(indent);

    while (stack.length > 1 && stack[stack.length - 1].indent >= indent) stack.pop();

    // List item: "- key: value" or "- value"
    if (line.startsWith("- ")) {
      const item = line.slice(2);
      const top = stack[stack.length - 1].obj;
      if (!Array.isArray(top)) {
        // Convert: the previous mapping had a key whose value should be a list.
        // We mark by replacing with an array on the parent.
        const parentEntry = stack[stack.length - 2];
        const parent = parentEntry ? parentEntry.obj : root;
        // The most recently set key on `parent` should become an array.
        const keys = Object.keys(parent);
        const lastKey = keys[keys.length - 1];
        parent[lastKey] = [];
        stack[stack.length - 1] = { indent: stack[stack.length - 1].indent, obj: parent[lastKey] };
      }
      const arr = stack[stack.length - 1].obj;
      const m = item.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
      if (m && (m[2] === "" || !m[2])) {
        const obj = {};
        arr.push(obj);
        stack.push({ indent, obj });
        const next = m[1];
        // peek subsequent lines: maybe "- foo:\n    bar: ..."
        // we just push and wait for the next iteration
        obj[next] = ""; // placeholder; will be overwritten by deeper entries if any
      } else if (m) {
        const obj = { [m[1]]: parseScalar(m[2]) };
        arr.push(obj);
        // following deeper-indented lines belong to this map
        stack.push({ indent, obj });
      } else {
        arr.push(parseScalar(item));
      }
      continue;
    }

    const m = line.match(/^([a-zA-Z0-9_-]+):\s*(.*)$/);
    if (!m) continue;
    const [, key, val] = m;
    if (val === "" || val === undefined) {
      // Could be a nested map OR a list — peek next non-empty line
      let j = i + 1;
      while (j < lines.length && !lines[j].trim()) j++;
      const peek = lines[j] || "";
      const peekIndent = peek.match(/^ */)[0].length;
      if (peek.slice(peekIndent).startsWith("- ") && peekIndent > indent) {
        setOnTop(key, []);
        stack.push({ indent, obj: topObj()[key] });
      } else if (peekIndent > indent && peek.slice(peekIndent).match(/^[a-zA-Z0-9_-]+:/)) {
        const obj = {};
        setOnTop(key, obj);
        stack.push({ indent, obj });
      } else if (val === "|" || val === ">") {
        // block scalar — collect deeper-indented lines
        let blk = [];
        let k = i + 1;
        let blkIndent = -1;
        while (k < lines.length) {
          const r = lines[k];
          if (!r.trim()) { blk.push(""); k++; continue; }
          const ri = r.match(/^ */)[0].length;
          if (blkIndent === -1) blkIndent = ri;
          if (ri < blkIndent || ri <= indent) break;
          blk.push(r.slice(blkIndent));
          k++;
        }
        setOnTop(key, blk.join("\n").replace(/\s+$/, ""));
        i = k - 1;
      } else {
        setOnTop(key, "");
      }
    } else if (val.startsWith("[") && val.endsWith("]")) {
      const inner = val.slice(1, -1).trim();
      const arr = inner ? inner.split(",").map((s) => parseScalar(s.trim())) : [];
      setOnTop(key, arr);
    } else {
      setOnTop(key, parseScalar(val));
    }
  }

  return root;
}

function parseScalar(s) {
  if (s === undefined || s === null) return "";
  s = String(s).trim();
  if (s === "") return "";
  if (s === "true") return true;
  if (s === "false") return false;
  if (s === "null") return null;
  if (/^-?\d+$/.test(s)) return Number(s);
  if (/^-?\d+\.\d+$/.test(s)) return Number(s);
  // strip wrapping quotes
  if ((s.startsWith('"') && s.endsWith('"')) || (s.startsWith("'") && s.endsWith("'"))) {
    return s.slice(1, -1);
  }
  return s;
}

function resolveEnv(value) {
  if (Array.isArray(value)) return value.map(resolveEnv);
  if (value && typeof value === "object") {
    const out = {};
    for (const k of Object.keys(value)) out[k] = resolveEnv(value[k]);
    return out;
  }
  if (typeof value !== "string") return value;
  return value.replace(/\$\{([A-Za-z_][A-Za-z0-9_]*)\}/g, (_, name) => {
    const v = process.env[name];
    return v === undefined ? "<unset>" : v;
  });
}

function listFiles() {
  if (!fs.existsSync(CONFIG_DIR)) return [];
  return fs
    .readdirSync(CONFIG_DIR)
    .filter((f) => f.endsWith(".md"))
    .map((f) => ({ topic: f.replace(/\.md$/, ""), path: path.join(CONFIG_DIR, f) }));
}

function loadAll() {
  const out = {};
  for (const { topic, path: p } of listFiles()) {
    try {
      out[topic] = parseFrontmatter(fs.readFileSync(p, "utf8"));
    } catch (e) {
      out[topic] = { __error: String(e) };
    }
  }
  return out;
}

function getAt(obj, dotted) {
  return dotted.split(".").reduce((acc, k) => (acc == null ? acc : acc[k]), obj);
}

function check() {
  const data = loadAll();
  const errs = [];
  const present = new Set(Object.keys(data));
  for (const required of ["info", "repos"]) {
    if (!present.has(required)) errs.push(`missing topic: ${required}.md`);
  }
  for (const [topic, fields] of Object.entries(REQUIRED_FIELDS)) {
    if (!present.has(topic)) continue;
    for (const f of fields) {
      if (getAt(data[topic], f) == null || getAt(data[topic], f) === "") {
        errs.push(`${topic}.md: required field '${f}' missing or empty`);
      }
    }
  }
  for (const [topic, body] of Object.entries(data)) {
    if (body && body.__error) errs.push(`${topic}.md: parse error: ${body.__error}`);
  }
  // Secret-in-plaintext check: any value matching a likely token shape that ISN'T a ${VAR}
  const tokenLike = /(github_pat_|sk-|gho_|ghp_|console-)/;
  function walk(obj, prefix) {
    if (obj == null) return;
    if (typeof obj === "string") {
      if (tokenLike.test(obj) && !obj.includes("${")) errs.push(`${prefix}: looks like a raw secret; use \${ENV_VAR} placeholder instead`);
      return;
    }
    if (Array.isArray(obj)) return obj.forEach((v, i) => walk(v, `${prefix}[${i}]`));
    if (typeof obj === "object") for (const k of Object.keys(obj)) walk(obj[k], `${prefix}.${k}`);
  }
  for (const [topic, body] of Object.entries(data)) walk(body, topic);
  return errs;
}

function missingReport() {
  const data = loadAll();
  const out = [];
  for (const [topic, fields] of Object.entries(RECOMMENDED_FIELDS)) {
    if (!data[topic]) {
      out.push({ topic, status: "missing-file" });
      continue;
    }
    const missing = fields.filter((f) => getAt(data[topic], f) == null || getAt(data[topic], f) === "");
    if (missing.length) out.push({ topic, status: "missing-fields", fields: missing });
  }
  return out;
}

function main() {
  if (CHECK) {
    const errs = check();
    if (errs.length) {
      for (const e of errs) console.error(`ERROR: ${e}`);
      process.exit(1);
    }
    console.log(JSON.stringify({ ok: true }));
    return;
  }
  if (MISSING) {
    console.log(JSON.stringify(missingReport(), null, 2));
    return;
  }
  let data = loadAll();
  if (RESOLVE_ENV) data = resolveEnv(data);
  if (positional.length === 0) {
    console.log(JSON.stringify(data, null, 2));
    return;
  }
  const topic = positional[0];
  if (!data[topic]) {
    console.error(`ERROR: topic '${topic}' not found in ${CONFIG_DIR}`);
    process.exit(1);
  }
  if (positional.length === 1) {
    console.log(JSON.stringify(data[topic], null, 2));
    return;
  }
  const key = positional[1];
  const value = getAt(data[topic], key);
  if (value === undefined) {
    console.error(`ERROR: key '${key}' not found in ${topic}.md`);
    process.exit(1);
  }
  console.log(JSON.stringify(value, null, 2));
}

main();
```
