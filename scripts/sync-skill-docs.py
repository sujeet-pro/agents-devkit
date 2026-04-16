#!/usr/bin/env python3
"""
Sync skill reference pages and guide pages from current SKILL.md files.

This is intentionally local to this repository and focuses on:
- docs/reference/skill-*.md
- docs/reference/skills/README.md
- docs/guide/{code-reviews,development,documentation,diagrams,research-planning,
  audits-quality,project-management,setup-config}/README.md
"""

from __future__ import annotations

import re
import sys
import textwrap
from collections import OrderedDict
from pathlib import Path

from skill_catalog import infer_area_from_name, iter_published_skill_dirs


ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
REFERENCE_DIR = ROOT / "docs" / "reference"
GUIDE_DIR = ROOT / "docs" / "guide"

sys.path.insert(0, str(ROOT / "templates" / "skill" / "scripts"))
from preflight import parse_frontmatter  # noqa: E402


TAG_RE = re.compile(r"\[([^\]]+)\]")
FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?", re.DOTALL)

GUIDE_FRONTMATTER = {
    "code-reviews": {
        "title": "Code Reviews",
        "description": "Review PRs, fix comments, and self-review local changes before merge",
        "order": 1,
    },
    "development": {
        "title": "Development",
        "description": "Build features, refactor code, migrate frameworks, and package completed work cleanly",
        "order": 2,
    },
    "documentation": {
        "title": "Documentation",
        "description": "Create, update, review, template, and publish engineering documentation",
        "order": 3,
    },
    "diagrams": {
        "title": "Visuals & Design",
        "description": "Create diagrams, charts, and interface design direction with the right artifact type",
        "order": 4,
    },
    "research-planning": {
        "title": "Research & Planning",
        "description": "Research topics, close ambiguity, create implementation plans, and write specifications",
        "order": 5,
    },
    "audits-quality": {
        "title": "Audits & Quality",
        "description": "Run repository audits, live site audits, and explicit testing workflows",
        "order": 6,
    },
}


REFERENCE_GROUPS = [
    ("Planning & Research", ["adk-brainstorm", "adk-plan", "adk-research"]),
    ("Development & Delivery", ["adk-build", "adk-refactor", "adk-migrate", "adk-commit"]),
    ("Review", ["adk-review-pr", "adk-review-local-changes", "adk-address-review-feedback", "adk-review-docs"]),
    ("Documentation", ["adk-write-docs"]),
    ("Visuals & Design", ["adk-diagram", "adk-chart", "adk-design"]),
    ("Audits & Testing", ["adk-audit-repo", "adk-audit-site", "adk-test"]),
]

GUIDE_SKILL_GROUPS = {
    "code-reviews": ["adk-review-pr", "adk-review-local-changes", "adk-address-review-feedback"],
    "development": ["adk-build", "adk-refactor", "adk-migrate", "adk-commit"],
    "documentation": ["adk-write-docs", "adk-review-docs"],
    "diagrams": ["adk-diagram", "adk-chart", "adk-design"],
    "research-planning": ["adk-brainstorm", "adk-plan", "adk-research", "adk-spec"],
    "audits-quality": ["adk-audit-repo", "adk-audit-site", "adk-test"],
}

STATIC_REFERENCE_PAGES = {
    "skill-INSPIRATION-MAP.md",
    "skill-LANDSCAPE.md",
    "skill-CATEGORY-ROUTING.md",
    "skill-MIGRATION-MAP.md",
}


HOW_IT_WORKS_SECTIONS = [
    "Shared Skills",
    "Helper Skill Resolution",
    "Preflight",
    "Preflight & MCP Resolution",
    "Workflow",
    "Common Phases",
    "Execution",
    "Refactoring Process",
    "Action Workflows",
    "Focus Area Resolution",
    "Guideline Loading",
    "Format Detection",
    "Template System",
    "Research Agents",
    "Research Rules",
    "Available Operations",
    "Operation References",
    "Managed Resources",
    "Workspace Conventions",
    "What Gets Configured",
    "Plugin Validation",
    "Usage",
]

MODES_AND_VARIATIONS_SECTIONS = [
    "Behavior Variations",
    "Actions",
    "Document Type Aliases",
    "Families",
    "Family Selection Guide",
    "Routing",
    "Routing Logic",
    "Mode Detection",
    "Stage Selection",
    "Source Detection",
    "Type Auto-Detection",
    "Depth",
    "Required Team",
    "Required Teams",
    "Sub-Skills",
]

OUTPUT_SECTIONS = [
    "Output Format",
    "Output",
    "What It Provides",
]

INTEGRATION_SECTIONS = [
    "Invoked By",
    "Downstream Skills",
    "Sub-Skills",
]

RELATED_SECTIONS = [
    "Adjacent Skills",
]


def strip_frontmatter(text: str) -> str:
    return FRONTMATTER_RE.sub("", text, count=1)


def parse_h2_sections(body: str) -> OrderedDict[str, str]:
    matches = list(re.finditer(r"^## (.+)$", body, flags=re.MULTILINE))
    sections: OrderedDict[str, str] = OrderedDict()
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections[title] = body[start:end].strip()
    return sections


def parse_h3_sections(section_text: str) -> OrderedDict[str, str]:
    matches = list(re.finditer(r"^### (.+)$", section_text, flags=re.MULTILINE))
    sections: OrderedDict[str, str] = OrderedDict()
    for i, match in enumerate(matches):
        title = match.group(1).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(section_text)
        sections[title] = section_text[start:end].strip()
    return sections


def clean_description(raw: str) -> str:
    cleaned = re.sub(r"^adk\s*-\s*(\[[^\]]+\]\s*)*", "", raw).strip()
    cleaned = cleaned.rstrip(".")
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def extract_tags(raw: str) -> list[str]:
    return [tag.strip() for tag in TAG_RE.findall(raw)]


def extract_area(raw: str) -> str:
    tags = extract_tags(raw)
    if len(tags) >= 2:
        return tags[1]
    return ""


def boolish(value: object) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() == "true"


def derive_category(tier: str, tags: list[str]) -> str:
    if "connector" in tags:
        return "connector"
    if tier == "helper":
        return "guideline"
    if tier == "orchestrator" or "routing" in tags:
        return "routing"
    return "task"


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def first_paragraph_after_h1(body: str) -> str:
    match = re.search(r"^# .+\n(.*?)(?=^## |\Z)", body, flags=re.DOTALL | re.MULTILINE)
    if not match:
        return ""
    block = normalize_whitespace(match.group(1))
    paragraphs = [p.strip() for p in block.split("\n\n") if p.strip()]
    return paragraphs[0] if paragraphs else ""


def first_sentence(text: str) -> str:
    text = normalize_whitespace(text)
    if not text:
        return ""
    pieces = re.split(r"(?<=[.!?])\s+", text)
    return pieces[0].strip() if pieces else text


def first_markdown_table(text: str) -> str:
    lines = text.splitlines()
    table: list[str] = []
    in_table = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|"):
            table.append(stripped)
            in_table = True
            continue
        if in_table:
            break
    if len(table) >= 2:
        return "\n".join(table)
    return ""


def parse_markdown_table(table: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in table.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        return []
    headers = [cell.strip() for cell in lines[0].strip("|").split("|")]
    rows: list[dict[str, str]] = []
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        rows.append({headers[i]: cells[i] for i in range(len(headers))})
    return rows


def extract_example_lines(text: str) -> list[str]:
    lines: list[str] = []
    for block in re.findall(r"```(?:\w+)?\n(.*?)```", text, flags=re.DOTALL):
        for line in block.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            if "/adk:" not in stripped and not re.match(r"adk-[a-z0-9-]+(?:\s|$)", stripped):
                continue
            if stripped not in lines:
                lines.append(stripped)
    return lines


def infer_argument_hint(parameter_rows: list[dict[str, str]], example_lines: list[str]) -> str:
    for line in example_lines:
        placeholders = re.findall(r"<[^>]+>", line)
        if placeholders:
            unique = [normalize_placeholder(item) for item in placeholders[:2]]
            return " ".join(dict.fromkeys(unique))
    positionals: list[str] = []
    for row in parameter_rows:
        param = row.get("Parameter", "").strip().strip("`")
        if not param or not (param.startswith("<") or param.startswith("[")):
            continue
        positionals.append(normalize_placeholder(param))
        if len(positionals) == 2:
            break
    return " ".join(positionals)


def normalize_placeholder(token: str) -> str:
    raw = token.strip().strip("`")
    if raw.startswith("[") and raw.endswith("]"):
        raw = f"<{raw[1:-1]}>"
    lowered = raw.lower()
    if any(part in lowered for part in ("task", "description", "topic", "query", "goal")):
        return "<prompt-text>"
    if "pr-url" in lowered or ("pr" in lowered and "url" in lowered):
        return "<pr-url>"
    if "url" in lowered:
        return "<url>"
    if "path" in lowered:
        return "<path>"
    if "branch" in lowered:
        return "<branch-name>"
    if "source" in lowered:
        return "<source>"
    if "target" in lowered:
        return "<target>"
    if "action" in lowered:
        return "<action>"
    if "name" in lowered:
        return "<name>"
    if "session" in lowered:
        return "<session-name>"
    if raw.startswith("<") and raw.endswith(">"):
        return raw
    return "<prompt-text>"


def placeholders_from_argument_hint(argument_hint: str) -> list[str]:
    if not argument_hint:
        return []
    tokens: list[str] = []
    for match in re.finditer(r"<[^>]+>", argument_hint):
        token = normalize_placeholder(match.group(0))
        if token not in tokens:
            tokens.append(token)
        if len(tokens) == 2:
            break
    return tokens


def base_placeholder_command(skill: dict) -> str:
    positionals: list[str] = []
    for row in skill["parameter_rows"]:
        param = row.get("Parameter", "").strip()
        param = param.strip("`")
        if not param or param.startswith("--"):
            continue
        description = row.get("Description", "").lower()
        if param.startswith("[") and "omitted" in description:
            continue
        positionals.append(normalize_placeholder(param))
        if len(positionals) == 2:
            break
    if not positionals:
        positionals = placeholders_from_argument_hint(skill.get("argument_hint", ""))
    command = skill["slug"]
    if positionals:
        command += " " + " ".join(positionals)
    return command


def flag_names(skill: dict) -> set[str]:
    flags = set()
    for row in skill["parameter_rows"]:
        param = row.get("Parameter", "").strip().strip("`")
        if param.startswith("--"):
            flags.add(param)
    return flags


def selector_flags() -> tuple[str, ...]:
    return (
        "--mode",
        "--action",
        "--focus",
        "--pattern",
        "--type",
        "--engine",
        "--layout",
        "--family",
        "--strategy",
        "--tool",
        "--server",
        "--scope",
        "--spec",
        "--plan",
        "--roles",
        "--models",
        "--output",
    )


def output_flags() -> tuple[str, ...]:
    return (
        "--verbosity",
        "--format",
        "--render",
        "--save",
        "--publish",
        "--auto",
        "--check-only",
        "--skip-update",
        "--deep",
    )


def build_examples_section(skill: dict) -> str:
    lines = skill["example_lines"]
    base = base_placeholder_command(skill)
    groups: list[tuple[str, str, list[str]]] = []
    flags = flag_names(skill)

    start_lines: list[str] = []
    if skill["user_invocable"] or base != skill["slug"]:
        start_lines.append(base)
    for line in lines:
        if not any(flag in line for flag in selector_flags() + output_flags()):
            if line not in start_lines:
                start_lines.append(line)
        if len(start_lines) >= 2:
            break
    if len(start_lines) == 1:
        if "--mode" in flags:
            start_lines.append(f"{base} --mode debug" if "<prompt-text>" in base else f"{skill['slug']} --mode debug")
        elif "--engine" in flags:
            start_lines.append(f"{base} --engine mermaid" if "<prompt-text>" in base else f"{skill['slug']} --engine mermaid <prompt-text>")
    if not start_lines and lines:
        start_lines = lines[:2]
    groups.append(
        (
            "Start With The Default Path",
            "Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.",
            start_lines,
        )
    )

    selector_lines = [line for line in lines if any(flag in line for flag in selector_flags())][:4]
    if not selector_lines:
        if "--engine" in flags:
            selector_lines.append(f"{skill['slug']} --engine mermaid <prompt-text>")
        elif "--mode" in flags and "<prompt-text>" in base:
            selector_lines.append(base.replace("<prompt-text>", "--mode debug <prompt-text>"))
        elif "--scope" in flags and "<prompt-text>" in base:
            selector_lines.append(base.replace("<prompt-text>", "--scope <path> <prompt-text>"))
    if selector_lines:
        groups.append(
            (
                "Force Or Narrow Behavior",
                "Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.",
                selector_lines,
            )
        )

    output_lines_list = [line for line in lines if any(flag in line for flag in output_flags())][:4]
    if not output_lines_list:
        if "--render" in flags and "--format" in flags:
            output_lines_list.append(f"{skill['slug']} --render --format png <prompt-text>")
        elif "--verbosity" in flags and base:
            output_lines_list.append(f"{base} --verbosity detailed")
        elif "--auto" in flags and base:
            output_lines_list.append(f"{base} --auto")
    if output_lines_list:
        groups.append(
            (
                "Change Output Or Execution Style",
                "These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.",
                output_lines_list,
            )
        )

    rendered: list[str] = ["The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.\n"]
    seen_groups: set[tuple[str, ...]] = set()
    for title, description, group_lines in groups:
        deduped: list[str] = []
        for line in group_lines:
            if line not in deduped:
                deduped.append(line)
        if not deduped:
            continue
        group_key = tuple(deduped)
        if group_key in seen_groups:
            continue
        seen_groups.add(group_key)
        rendered.append(f"### {title}\n")
        rendered.append(description + "\n")
        rendered.append("```text\n" + "\n".join(deduped) + "\n```")
    return "\n".join(rendered).strip()


def render_frontmatter(title: str, description: str, skill_name: str, category: str, tier: str, user_invocable: bool) -> str:
    return "\n".join(
        [
            "---",
            f"title: {title!r}",
            f"description: {description!r}",
            f"skill_name: {skill_name}",
            f"category: {category}",
            f"workflow_tier: {tier}",
            f"user_invocable: {'true' if user_invocable else 'false'}",
            "---",
        ]
    )


def opening_paragraph(skill: dict) -> str:
    intro = normalize_whitespace(skill["intro"])
    intro_lower = intro.lower()
    purpose = normalize_whitespace(intro or skill["clean_description"]).rstrip(".")
    purpose = re.sub(r"^(use this when|use when|use to)\s+", "", purpose, flags=re.IGNORECASE)
    purpose = re.sub(r"^helper skill\s+", "", purpose, flags=re.IGNORECASE)
    purpose = purpose[:1].lower() + purpose[1:] if purpose else ""

    if intro and not intro_lower.startswith(("use when ", "use this when ", "use to ")):
        first = intro if intro.endswith(".") else intro + "."
    elif skill["category"] == "routing":
        focus = (skill.get("area") or skill["slug"]).replace("-", " ")
        first = f"Use `{skill['name']}` when you want DevKit to route {focus} work to the right downstream skill."
    elif skill["category"] == "connector":
        first = f"`{skill['name']}` centralizes platform-specific operations so higher-level skills do not need to own authentication, transport choice, and fallback logic themselves."
    elif skill["category"] == "guideline":
        if skill["slug"] == "workflow":
            first = "`workflow` is the shared contract that defines the standard workflow shapes other skills rely on."
        else:
            first = f"`{skill['name']}` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it."
    else:
        leading_word = purpose.split()[0] if purpose else ""
        if leading_word.endswith("ing"):
            first = f"Use `{skill['name']}` when {purpose}."
        elif purpose:
            first = f"Use `{skill['name']}` to {purpose}."
        else:
            first = f"Use `{skill['name']}` when you want the dedicated `{skill['name']}` workflow."
    trait = ""
    if "review-only" in intro_lower or "do not modify" in intro_lower:
        trait = "It is intentionally read-only, so the deliverable is a report, recommendation set, or published artifact rather than a repository edit."
    elif "idempotent" in intro_lower:
        trait = "Its behavior is intentionally idempotent, which makes it safe to re-run as the environment or surrounding artifacts change."
    elif skill["category"] == "routing":
        trait = "Its job is classification and parameter forwarding, not doing the downstream work itself."
    elif skill["category"] == "connector":
        trait = "The calling skill owns the user-facing workflow; this connector owns authentication checks, transport choice, and operation boundaries."
    elif skill["category"] == "guideline":
        trait = "Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract."
    else:
        trait = "In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short."

    return f"{first} {trait}"


def overview_section(skill: dict) -> str:
    paras: list[str] = []
    family = skill["family"]
    tier = skill["tier"]
    category = skill["category"]
    layer_sentence = f"`{skill['name']}` belongs to the `{category}` layer"
    if tier:
        layer_sentence += f" and is declared at the `{tier}` tier"
    if family:
        layer_sentence += f" with the `{family}` workflow family"
    layer_sentence += "."
    paras.append(
        layer_sentence
        + " That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill."
    )
    if category in {"task", "routing"}:
        paras.append(
            "The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable."
        )
    elif category == "guideline":
        paras.append(
            "The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic."
        )
    else:
        paras.append(
            "Connector skills deliberately centralize platform-specific behavior. That keeps authentication, fallback order, and operation families in one place so higher-level task skills can focus on review, documentation, or implementation logic instead of API plumbing."
        )
    return "\n\n".join(paras)


def parameter_notes(skill: dict) -> str:
    flags = flag_names(skill)
    notes: list[str] = []
    if any(
        row.get("Parameter", "").strip().strip("`") and not row.get("Parameter", "").strip().strip("`").startswith("--")
        for row in skill["parameter_rows"]
    ):
        notes.append(
            "The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description."
        )
    note_map = [
        ("--mode", "`--mode` overrides keyword detection and sends the skill straight to a specific stage or behavioral branch."),
        ("--action", "`--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it."),
        ("--focus", "`--focus` changes what the skill optimizes for and often changes which child agents, checks, or review dimensions are loaded."),
        ("--scope", "`--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository."),
        ("--pattern", "`--pattern` is the fastest way to tell a transformation skill what kind of change you want instead of relying on intent inference."),
        ("--type", "`--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters."),
        ("--engine", "`--engine` bypasses routing and sends the request to one specific diagram backend."),
        ("--verbosity", "`--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale."),
        ("--auto", "`--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions."),
        ("--render", "`--render` changes the deliverable from source-only generation to source plus rendered assets."),
        ("--format", "`--format` controls the artifact shape, which can also change embedding rules or publishing behavior."),
        ("--save", "`--save` makes the skill write a durable artifact instead of returning everything inline."),
        ("--publish", "`--publish` adds a delivery step after generation so the result ends up in an external document destination."),
        ("--help", "`--help` prints the embedded reference and exits without running the workflow."),
    ]
    for flag, note in note_map:
        if flag in flags:
            notes.append(note)
    if not notes:
        return ""
    return "### Parameter Notes\n\n" + "\n".join(f"- {note}" for note in notes)


def how_it_works_intro(skill: dict) -> str:
    if skill["category"] == "connector":
        return (
            "Connector behavior starts with preflight. The skill validates authentication, tooling, or MCP access first, then routes the requested operation through the preferred transport and fallback path defined in `SKILL.md`.\n\n"
            "That split matters for developers because task skills depend on this page to understand what is guaranteed before a networked action happens and what should happen when auth or transport is unavailable."
        )
    if skill["category"] == "guideline":
        return (
            "Helper skills do not usually own the top-level conversation. The calling skill decides when to load them, passes just enough context to resolve the right rules or references, and then consumes the returned guidance inside its own execution flow.\n\n"
            "The important developer contract is therefore: when the helper is loaded, what context it reads, what rules or artifacts it returns, and how that changes the calling skill's behavior."
        )
    if skill["category"] == "routing":
        return (
            "Routing begins by resolving intent. Explicit override flags take priority; otherwise the detection rules below choose a downstream skill, stage, or engine based on the prompt and repository context.\n\n"
            "Once the route is fixed, the router keeps parameter forwarding narrow and predictable so the downstream skill receives the same important selectors the user provided."
        )
    return (
        "Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.\n\n"
        "The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow."
    )


def modes_intro(skill: dict) -> str:
    if skill["category"] == "guideline":
        return "Most helpers do not have end-user modes in the same sense as task skills, but they still vary by scope, invoking context, selected family, or fallback behavior.\n"
    if skill["category"] == "connector":
        return "The important variations here are usually transport choice, operation family, or platform-specific fallback behavior rather than a user-visible workflow mode.\n"
    return "Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.\n"


def output_intro(skill: dict) -> str:
    if skill["category"] == "connector":
        return "Connectors typically return platform data or perform side effects for the calling skill. They do not usually define the final human-facing narrative on their own.\n"
    if skill["category"] == "guideline":
        return "Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.\n"
    return "Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.\n"


def render_named_sections(skill: dict, names: list[str], consumed: set[str]) -> list[str]:
    rendered: list[str] = []
    for name in names:
        if name in consumed:
            continue
        content = skill["h2_sections"].get(name, "").strip()
        if not content:
            continue
        rendered.append(f"### {name}\n\n{content}")
        consumed.add(name)
    return rendered


def build_reference_page(skill: dict) -> str:
    consumed: set[str] = {"Help", "Parameters", "Examples"}
    parts: list[str] = [
        render_frontmatter(
            title=skill["name"],
            description=skill["clean_description"] or skill["name"],
            skill_name=skill["name"],
            category=skill["category"],
            tier=skill["tier"],
            user_invocable=skill["user_invocable"],
        ),
        f"# {skill['name']}",
        opening_paragraph(skill),
        "## Overview",
        overview_section(skill),
        "## Parameters",
    ]

    if skill["parameters_table"]:
        parts.append(skill["parameters_table"])
        notes = parameter_notes(skill)
        if notes:
            parts.append(notes)
    else:
        if skill["category"] == "connector":
            parts.append("This connector does not define a standalone user-facing parameter table. The calling skill decides the operation and passes the relevant context through the connector contract.")
        elif skill["category"] == "guideline":
            parts.append("This helper does not expose a broad user-facing parameter surface beyond the narrow controls in `SKILL.md`. In practice, task skills load it indirectly and supply the context it needs.")
        else:
            parts.append("No parameter table is currently defined in `SKILL.md` for this skill.")

    how_sections = render_named_sections(skill, HOW_IT_WORKS_SECTIONS, consumed)
    if how_sections:
        parts.extend(["## How It Works", how_it_works_intro(skill), *how_sections])

    mode_sections = render_named_sections(skill, MODES_AND_VARIATIONS_SECTIONS, consumed)
    if skill["help_h3"].get("Behavior Variations"):
        if "Behavior Variations" not in consumed:
            mode_sections.insert(0, f"### Behavior Variations\n\n{skill['help_h3']['Behavior Variations']}")
            consumed.add("Behavior Variations")
    if skill["help_h3"].get("Actions"):
        if "Actions" not in consumed:
            mode_sections.insert(0, f"### Actions\n\n{skill['help_h3']['Actions']}")
            consumed.add("Actions")
    if mode_sections:
        parts.extend(["## Modes & Variations", modes_intro(skill), *mode_sections])

    output_sections = render_named_sections(skill, OUTPUT_SECTIONS, consumed)
    if output_sections:
        parts.extend(["## Output", output_intro(skill), *output_sections])
    else:
        parts.extend(["## Output", output_intro(skill)])

    integration_sections = render_named_sections(skill, INTEGRATION_SECTIONS, consumed)
    if integration_sections:
        parts.extend(["## Integration", *integration_sections])

    related_sections = render_named_sections(skill, RELATED_SECTIONS, consumed)
    if related_sections:
        parts.extend(["## Related Skills", *related_sections])

    remaining_sections = []
    for title, content in skill["h2_sections"].items():
        if title in consumed:
            continue
        remaining_sections.append(f"### {title}\n\n{content}")
        consumed.add(title)
    if remaining_sections:
        parts.extend(["## Additional Reference", *remaining_sections])

    parts.extend(["## Examples", build_examples_section(skill)])
    return "\n\n".join(part for part in parts if part).rstrip() + "\n"


def infer_tier_label(skill: dict) -> str:
    if skill["category"] == "routing":
        return "router"
    return skill["tier"] or skill["category"]


def build_skill_index(skills: dict[str, dict]) -> str:
    sections: list[str] = [
        "---",
        'title: "Skill Reference"',
        'description: "Complete reference for ADK skills — parameters, workflow contracts, and examples sourced from current SKILL.md files"',
        "order: 1",
        "---",
        "",
        "# Skill Reference",
        "",
        "Every page in this section is derived from the live `SKILL.md` file for that skill. Use the individual reference pages when you want the exact flag surface, workflow contract, helper-skill composition, and output expectations for the current repository state.",
        "",
        "## Strategy and Governance",
        "",
        "- [Skill Landscape and Gap Analysis](../skill-LANDSCAPE.md)",
        "- [Skill Inspiration Map](../skill-INSPIRATION-MAP.md)",
        "- [Category Routing Map](../skill-CATEGORY-ROUTING.md)",
        "- [Skill Migration Map](../skill-MIGRATION-MAP.md)",
        "",
        "## Common Parameters",
        "",
        "Many user-invocable skills expose some combination of the following controls:",
        "",
        "| Parameter | What it usually does |",
        "|-----------|----------------------|",
        "| `--help` | Print the embedded skill reference and stop |",
        "| `--scope` | Limit analysis or execution to one path, surface, or target area |",
        "| `--focus` | Keep the primary review, audit, or design lens explicit |",
        "| `--action` | Choose a lifecycle action such as create, update, review, or publish |",
        "",
    ]

    for title, slugs in REFERENCE_GROUPS:
        rows = [skills[slug] for slug in slugs if slug in skills]
        if not rows:
            continue
        sections.extend(
            [
                f"## {title}",
                "",
                "| Skill | Tier | Description | Reference |",
                "|-------|------|-------------|-----------|",
            ]
        )
        for skill in rows:
            sections.append(
                f"| [`{skill['name']}`](../skill-{skill['slug']}.md) | {infer_tier_label(skill)} | {skill['clean_description']} | [Details ->](../skill-{skill['slug']}.md) |"
            )
        sections.append("")

    sections.extend(
        [
            "## Self-Sufficient Pattern",
            "",
            "Task skills are designed to stay usable even in partial installations. They prefer shared helper skills when those helpers are available, but the inline fallback summaries inside each `SKILL.md` preserve the critical rules for workflow, communication, formatting, and validation.",
            "",
        ]
    )
    return "\n".join(sections).rstrip() + "\n"


def find_skill_command(command: str) -> str:
    match = re.search(r"(?:/adk:)?([a-z0-9-]+)", command)
    if not match:
        raise ValueError(f"Could not determine skill for command: {command}")
    return match.group(1)


def validate_commands(skills: dict[str, dict], commands: list[str]) -> None:
    for command in commands:
        slug = find_skill_command(command)
        if slug not in skills:
            raise ValueError(f"Guide command references unknown skill `{slug}`: {command}")
        available_flags = flag_names(skills[slug])
        for flag in re.findall(r"--[a-z0-9-]+", command):
            if flag not in available_flags:
                raise ValueError(f"Guide command uses unsupported flag `{flag}` for `{slug}`: {command}")


def code_block(lines: list[str]) -> str:
    return "```text\n" + "\n".join(lines) + "\n```"


def render_guide(slug: str, skills: dict[str, dict]) -> str:
    fm = GUIDE_FRONTMATTER[slug]
    guide_skills = [skills[name] for name in GUIDE_SKILL_GROUPS.get(slug, []) if name in skills]
    quick_start = ""
    examples: list[str] = []
    if guide_skills:
        first_skill = guide_skills[0]
        quick_start = f"> **Quick start:** `/{first_skill['name']}` is the simplest entrypoint for this category."
        for skill in guide_skills[:4]:
            invocation = f"/{skill['name']}"
            if skill["argument_hint"]:
                invocation += f" {skill['argument_hint']}"
            examples.append(invocation)

    table_lines = [
        "| Skill | Purpose | Reference |",
        "| --- | --- | --- |",
    ]
    for skill in guide_skills:
        table_lines.append(
            f"| `/{skill['name']}` | {skill['clean_description']} | [Details](../../reference/skill-{skill['slug']}.md) |"
        )

    body_parts = [
        f"# {fm['title']}",
        "",
        fm["description"] + ".",
        "",
        quick_start,
        "",
        "## Included Skills",
        "",
        "\n".join(table_lines),
    ]
    if examples:
        body_parts.extend(
            [
                "",
                "## Example Invocations",
                "",
                code_block(examples),
            ]
        )
    body_parts.extend(
        [
            "",
            "## How To Use This Guide",
            "",
            "Start with the skill whose primary job matches the outcome you want. Use the linked reference page for the exact flag surface, workflow contract, and validation expectations.",
        ]
    )
    body = "\n".join(part for part in body_parts if part is not None)
    frontmatter = "\n".join(
        [
            "---",
            f"title: {fm['title']}",
            f"description: {fm['description']}",
            f"order: {fm['order']}",
            "---",
        ]
    )
    return frontmatter + "\n\n" + body.rstrip() + "\n"


def render_code_reviews_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:code-review <prompt-text>",
        "/adk:code-review-pr <pr-url>",
        "/adk:code-review-pr <pr-url> --focus security",
        "/adk:code-review-pr <pr-url> --mode interactive",
        "/adk:code-review-pr <pr-url> --publish",
        "/adk:code-review-pr <pr-url> --skip-repo",
        "/adk:code-review-pr --context <url>",
        "/adk:code-review-pr",
        "/adk:code-review-pr <branch-name>",
        "/adk:code-review-pr --fix",
        "/adk:code-review-pr <pr-url> --cross",
        "/adk:code-review-fix <pr-url>",
        "/adk:code-review-fix <pr-url> --filter blocker",
        "/adk:code-review-fix <pr-url> --dry-run",
        "/adk:code-review-fix <pr-url> --auto",
        "/adk:code-review-repo",
        "/adk:code-review-repo <path>",
        "/adk:code-review-repo --focus architecture",
        "/adk:code-review-repo --output json",
        "/adk:code-review-pr <pr-url> --action describe",
        "/adk:code-review-pr <pr-url> --action finalize",
        "/adk:code-review-pr <pr-url> --action status",
    ]
    validate_commands(skills, commands)
    return f"""# Code Reviews

ADK gives you two ways to start a review: use the `code-review` router when you want it to pick the right path, or jump straight to the specific review skill when you already know the target.

> **Quick start:** `/adk:code-review <prompt-text>` lets the router decide whether you need a PR review, a local review, or a repository-wide pass.

## Scenarios

- [Review A Pull Request](#review-a-pull-request)
- [Review Local Changes](#review-local-changes)
- [Fix Review Comments](#fix-review-comments)
- [Review An Entire Repository](#review-an-entire-repository)
- [Describe Or Finalize A PR](#describe-or-finalize-a-pr)

---

## Review A Pull Request

Use `code-review-pr` when you already have a GitHub or Bitbucket PR URL. Start with the plain URL, then add flags only when you want to narrow the review or change how the findings are handled.

{code_block([
    "/adk:code-review-pr <pr-url>",
    "/adk:code-review-pr https://github.com/org/repo/pull/42",
    "/adk:code-review-pr <pr-url> --focus security",
    "/adk:code-review-pr <pr-url> --mode interactive",
    "/adk:code-review-pr <pr-url> --publish",
    "/adk:code-review-pr <pr-url> --skip-repo",
    "/adk:code-review-pr <pr-url> --context <url>",
])}

Use `--focus` when you want the review weighted toward one concern, `--mode interactive` when you want to triage findings before posting them, and `--publish` when the comments should go back to the PR instead of staying local.

---

## Review Local Changes

You can use the same skill before a PR exists. With no target it reviews your staged and unstaged work; with a branch name it compares that branch against its base.

{code_block([
    "/adk:code-review-pr",
    "/adk:code-review-pr <branch-name>",
    "/adk:code-review-pr feature/auth-v2",
    "/adk:code-review-pr --fix",
    "/adk:code-review-pr <pr-url> --cross",
])}

Use `--fix` for self-review when you want the skill to apply straightforward fixes locally. Use `--cross` on high-stakes changes when you want the multi-model peer-review path before you ship.

---

## Fix Review Comments

When reviewers have already left feedback on a PR, switch to `code-review-fix`. It reads unresolved comments, categorizes them, and helps you apply fixes or push back with evidence.

{code_block([
    "/adk:code-review-fix <pr-url>",
    "/adk:code-review-fix https://github.com/org/repo/pull/42",
    "/adk:code-review-fix <pr-url> --filter blocker",
    "/adk:code-review-fix <pr-url> --dry-run",
    "/adk:code-review-fix <pr-url> --auto",
])}

`--filter` is the quickest way to narrow the queue. `--dry-run` is useful when you want a plan before touching code, and `--auto` is for cases where you want the workflow to process everything it can without extra approvals.

---

## Review An Entire Repository

Use `code-review-repo` when the target is the codebase itself rather than a diff. This is the right entry point for architecture, consistency, testing, documentation, or technical-debt reviews.

{code_block([
    "/adk:code-review-repo",
    "/adk:code-review-repo <path>",
    "/adk:code-review-repo src/backend/",
    "/adk:code-review-repo --focus architecture",
    "/adk:code-review-repo --output json",
])}

Point it at a directory when you only want one package or subsystem, and use `--focus` when you want the report weighted toward one review dimension.

---

## Describe Or Finalize A PR

`code-review-pr` also owns the PR-management actions that happen after the review itself: writing a description, checking merge readiness, and reporting current status.

{code_block([
    "/adk:code-review-pr <pr-url> --action describe",
    "/adk:code-review-pr <pr-url> --action finalize",
    "/adk:code-review-pr <pr-url> --action status",
])}

Use `--action describe` when the diff needs a clean title and summary, `--action finalize` before merge, and `--action status` when you want a quick readiness read without changing anything.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the review path | `code-review` | `<prompt-text>` |
| Review a PR | `code-review-pr` | `<pr-url>`, `--focus`, `--publish` |
| Review local changes | `code-review-pr` | no target, `<branch-name>`, `--fix` |
| Fix reviewer comments | `code-review-fix` | `<pr-url>`, `--filter`, `--dry-run` |
| Review a repository | `code-review-repo` | `<path>`, `--focus`, `--output` |
| Generate a PR description or finalize | `code-review-pr` | `<pr-url>`, `--action` |

## Related Skills

- **[`audit`](/reference/skill-audit/)** for deeper security, performance, dependency, or codebase audits.
- **[`dev-build`](/reference/skill-dev-build/)** when a review finding turns into real implementation work.
- **[`dev-commit`](/reference/skill-dev-commit/)** when you are ready to package the result into a commit or PR description.
"""


def render_development_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:dev <prompt-text>",
        "/adk:dev-build <prompt-text>",
        "/adk:dev-build --mode enhance <prompt-text>",
        "/adk:dev-build --spec <path> <prompt-text>",
        "/adk:dev-build --plan <path> <prompt-text>",
        "/adk:dev-build --scope <path> <prompt-text>",
        "/adk:dev-build --branch <name> <prompt-text>",
        "/adk:dev-build --mode quick <prompt-text>",
        "/adk:dev-build --mode worktree <prompt-text>",
        "/adk:dev-build --mode debug <prompt-text>",
        "/adk:dev-build --fix <prompt-text>",
        "/adk:dev-build --mode tdd <prompt-text>",
        "/adk:dev-build --tdd <prompt-text>",
        "/adk:dev-build --mode verify <prompt-text>",
        "/adk:dev-refactor <prompt-text>",
        "/adk:dev-refactor --pattern extract <prompt-text>",
        "/adk:dev-refactor --scope <path> <prompt-text>",
        "/adk:dev-migrate <source> to <target>",
        "/adk:dev-migrate --scope <path> <source> to <target>",
        "/adk:dev-migrate --dry-run <source> to <target>",
        "/adk:dev-commit",
    ]
    validate_commands(skills, commands)
    return f"""# Development

Use the `dev` router when you want ADK to decide which development workflow fits the request, or jump directly to the specialized skill when you already know whether the job is implementation, debugging, refactoring, migration, or wrap-up.

> **Quick start:** `/adk:dev <prompt-text>` routes the request to the right development skill and keeps the workflow small when the task is small.

## Scenarios

- [Build Or Extend Something](#build-or-extend-something)
- [Debug Or Verify](#debug-or-verify)
- [Refactor Safely](#refactor-safely)
- [Migrate Dependencies Or Frameworks](#migrate-dependencies-or-frameworks)
- [Wrap Up Your Changes](#wrap-up-your-changes)

---

## Build Or Extend Something

Start with `dev-build` for new features, extensions to existing behavior, quick fixes, or isolated experiments. The skill can read a spec or plan file when you already have one.

{code_block([
    "/adk:dev-build <prompt-text>",
    "/adk:dev-build implement user authentication with OAuth2",
    "/adk:dev-build --mode enhance <prompt-text>",
    "/adk:dev-build --spec <path> <prompt-text>",
    "/adk:dev-build --plan <path> <prompt-text>",
    "/adk:dev-build --scope <path> <prompt-text>",
    "/adk:dev-build --branch <name> <prompt-text>",
    "/adk:dev-build --mode quick <prompt-text>",
    "/adk:dev-build --mode worktree <prompt-text>",
])}

Use `--mode enhance` when you are extending something that already exists, `--scope` when you want to keep the blast radius tight, and `--mode worktree` when you want the experiment isolated in a separate git worktree.

---

## Debug Or Verify

Use debug mode when the main job is diagnosis, and verify mode when the implementation is already done and you only want confidence checks.

{code_block([
    "/adk:dev-build --mode debug <prompt-text>",
    "/adk:dev-build --mode debug the login form crashes on empty email",
    "/adk:dev-build --fix <prompt-text>",
    "/adk:dev-build --mode tdd <prompt-text>",
    "/adk:dev-build --tdd <prompt-text>",
    "/adk:dev-build --mode verify <prompt-text>",
])}

`--fix` keeps you in the debugging workflow but lets the skill implement the fix once the root cause is understood. `--tdd` is just the convenient alias for the TDD mode when you want tests first.

---

## Refactor Safely

Reach for `dev-refactor` when the job is a behavior-preserving transformation rather than new product behavior.

{code_block([
    "/adk:dev-refactor <prompt-text>",
    "/adk:dev-refactor --pattern extract <prompt-text>",
    "/adk:dev-refactor --pattern rename <prompt-text>",
    "/adk:dev-refactor --pattern restructure <prompt-text>",
    "/adk:dev-refactor --scope <path> <prompt-text>",
])}

The pattern flag is the main selector here: use it when you want the skill to skip inference and go directly to extraction, rename, restructure, simplify, or modernization work.

---

## Migrate Dependencies Or Frameworks

Use `dev-migrate` when the core question is “how do we move from one version, package, or framework to another without breaking the system?”

{code_block([
    "/adk:dev-migrate <source> to <target>",
    "/adk:dev-migrate react@17 to react@19",
    "/adk:dev-migrate --scope <path> <source> to <target>",
    "/adk:dev-migrate --dry-run <source> to <target>",
])}

Start with `--dry-run` when you want the breakage analysis and migration path before any code changes happen.

---

## Wrap Up Your Changes

After implementation, refactoring, or migration work is done, use `dev-commit` to package the result cleanly.

{code_block([
    "/adk:dev-commit",
])}

This is the wrap-up skill for staging, commit-message generation, and PR-description generation when you have finished the development work itself.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK pick the development path | `dev` | `<prompt-text>` |
| Build or extend behavior | `dev-build` | `<prompt-text>`, `--mode`, `--spec`, `--plan`, `--scope` |
| Debug or verify | `dev-build` | `--mode debug`, `--fix`, `--mode verify` |
| Refactor | `dev-refactor` | `<prompt-text>`, `--pattern`, `--scope` |
| Migrate packages or frameworks | `dev-migrate` | `<source> to <target>`, `--scope`, `--dry-run` |
| Commit and summarize | `dev-commit` | no required flags |

## Related Skills

- **[`plan`](/reference/skill-plan/)** when you want the plan first and the code second.
- **[`spec`](/reference/skill-spec/)** when the missing artifact is a requirements document rather than code.
- **[`code-review-pr`](/reference/skill-code-review-pr/)** when you want to self-review the result before or after a PR is opened.
"""


def render_documentation_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:docs <prompt-text>",
        "/adk:docs-crud <action> <path>",
        "/adk:docs-crud create <path> --type adr",
        "/adk:docs-crud update <path>",
        "/adk:docs-crud improve <path>",
        "/adk:docs-crud comment-reply <path>",
        "/adk:docs-write --type adr <prompt-text>",
        "/adk:docs-write --type runbook <prompt-text>",
        "/adk:docs-write --audience executives --type system-design <prompt-text>",
        "/adk:docs-write --publish both --publish-space <name> --publish-parent <name> --type adr <prompt-text>",
        "/adk:docs-write --output-dir <path> --type system-design <prompt-text>",
        "/adk:docs-review <path>",
        "/adk:docs-review <path> --focus accuracy",
        "/adk:docs-review <path> --mode interactive",
        "/adk:docs-repo",
        "/adk:docs-repo --init",
        "/adk:docs-repo --scope package <name>",
        "/adk:docs-repo --format pagesmith",
        "/adk:docs-confluence read <url>",
        "/adk:docs-confluence write <path> --space <name> --parent <name>",
        "/adk:docs-confluence sync <url>",
    ]
    validate_commands(skills, commands)
    return f"""# Documentation

Start with the `docs` router when you want ADK to choose the documentation workflow, then move to the specific skill once you know whether the job is page lifecycle work, formal document authoring, review, repository docs, or Confluence sync.

> **Quick start:** `/adk:docs <prompt-text>` is the simplest way to tell ADK what documentation outcome you want and let it choose the right skill.

## Scenarios

- [Create Or Update A Page](#create-or-update-a-page)
- [Write A Formal Engineering Document](#write-a-formal-engineering-document)
- [Review Documentation Quality](#review-documentation-quality)
- [Generate Repository Documentation](#generate-repository-documentation)
- [Work With Confluence](#work-with-confluence)

---

## Create Or Update A Page

Use `docs-crud` when the job is the lifecycle of one page or one document target: create it, refresh it, improve it, or reply to comments on it.

{code_block([
    "/adk:docs-crud <action> <path>",
    "/adk:docs-crud create <path> --type adr",
    "/adk:docs-crud create docs/decisions/caching-strategy.md --type adr",
    "/adk:docs-crud update <path>",
    "/adk:docs-crud improve <path>",
    "/adk:docs-crud comment-reply <path>",
])}

Use `--type` when you want one of the built-in document skeletons. Use `update` when the source-of-truth has changed, `improve` when the content is mostly right but not easy enough to read, and `comment-reply` when the review queue is the real input.

---

## Write A Formal Engineering Document

Use `docs-write` when the output needs to be a durable engineering artifact such as an ADR, RFC, runbook, system design, or similar formal document.

{code_block([
    "/adk:docs-write --type adr <prompt-text>",
    "/adk:docs-write --type runbook <prompt-text>",
    "/adk:docs-write --audience executives --type system-design <prompt-text>",
    "/adk:docs-write --publish both --publish-space <name> --publish-parent <name> --type adr <prompt-text>",
    "/adk:docs-write --output-dir <path> --type system-design <prompt-text>",
])}

`--type` controls the document family, `--audience` helps ADK tune depth and tone, and the publish flags are for cases where the destination is Confluence rather than a local markdown file.

---

## Review Documentation Quality

Use `docs-review` when you want findings first instead of edits first.

{code_block([
    "/adk:docs-review <path>",
    "/adk:docs-review ./docs/api-reference.md",
    "/adk:docs-review <path> --focus accuracy",
    "/adk:docs-review <path> --mode interactive",
])}

Start with the plain file or directory path, then add `--focus` when you care most about one dimension such as accuracy or completeness. Interactive mode is the best fit when you want to triage findings as you go.

---

## Generate Repository Documentation

Use `docs-repo` when the target is the repository as a whole rather than one page.

{code_block([
    "/adk:docs-repo",
    "/adk:docs-repo --init",
    "/adk:docs-repo --scope package <name>",
    "/adk:docs-repo --format pagesmith",
])}

`--init` bootstraps the doc structure, `--scope` narrows generation to a package, and `--format` lets you choose the target doc system.

---

## Work With Confluence

Use `docs-confluence` when the source or destination is Confluence and you want a skill that understands that platform directly.

{code_block([
    "/adk:docs-confluence read <url>",
    "/adk:docs-confluence write <path> --space <name> --parent <name>",
    "/adk:docs-confluence sync <url>",
])}

This is the right path when the local markdown flow is not enough and the important part of the job is platform-aware publishing or synchronization.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the documentation path | `docs` | `<prompt-text>` |
| Create, update, improve, or reply on one page | `docs-crud` | `<action>`, `<path>`, `--type` |
| Write a formal engineering document | `docs-write` | `--type`, `--audience`, `--publish`, `--output-dir` |
| Review docs without editing | `docs-review` | `<path>`, `--focus`, `--mode` |
| Generate repo docs | `docs-repo` | `--init`, `--scope`, `--format` |
| Read, write, or sync Confluence content | `docs-confluence` | `read|write|sync`, `--space`, `--parent` |

## Related Skills

- **[`spec`](/reference/skill-spec/)** when the missing artifact is a formal specification rather than general documentation.
- **[`diagram`](/reference/skill-diagram/)** when the document needs diagrams as part of the explanation.
- **[`research`](/reference/skill-research/)** when the document needs cited source material before it can be written well.
"""


def render_diagrams_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:diagram <prompt-text>",
        "/adk:diagram --engine mermaid <prompt-text>",
        "/adk:diagram --engine excalidraw <prompt-text>",
        "/adk:diagram-mermaid <prompt-text>",
        "/adk:diagram-mermaid --type sequence <prompt-text>",
        "/adk:diagram-mermaid --type er <prompt-text>",
        "/adk:diagram-excalidraw <prompt-text>",
        "/adk:diagram-excalidraw --palette aws <prompt-text>",
        "/adk:diagram-drawio <prompt-text>",
        "/adk:diagram-graphviz <prompt-text>",
        "/adk:diagram-graphviz --layout dot <prompt-text>",
        "/adk:diagram-mermaid --render --format png <prompt-text>",
        "/adk:diagram-excalidraw --theme dark <prompt-text>",
    ]
    validate_commands(skills, commands)
    return f"""# Diagrams

Use the `diagram` router when you know what you want to explain but not which rendering engine fits best. If you already know the engine, call the engine-specific skill directly.

> **Quick start:** `/adk:diagram <prompt-text>` lets the router choose the engine from the diagram type, the prompt, and the existing assets in the repository.

## Scenarios

- [Let The Router Choose](#let-the-router-choose)
- [Mermaid For Text-First Diagrams](#mermaid-for-text-first-diagrams)
- [Excalidraw For Hand-Drawn Overviews](#excalidraw-for-hand-drawn-overviews)
- [Drawio For Precise Layouts](#drawio-for-precise-layouts)
- [Graphviz For Strict Graphs](#graphviz-for-strict-graphs)
- [Render And Theme Output](#render-and-theme-output)

---

## Let The Router Choose

Start here when you have a diagram request but not a preferred engine.

{code_block([
    "/adk:diagram <prompt-text>",
    "/adk:diagram system context for the payments platform",
    "/adk:diagram --engine mermaid <prompt-text>",
    "/adk:diagram --engine excalidraw <prompt-text>",
])}

Use `--engine` only when you want to bypass routing and force a specific backend.

---

## Mermaid For Text-First Diagrams

Mermaid is the most natural fit for flowcharts, sequence diagrams, state diagrams, ER diagrams, timelines, and other text-native diagram types.

{code_block([
    "/adk:diagram-mermaid <prompt-text>",
    "/adk:diagram-mermaid --type sequence <prompt-text>",
    "/adk:diagram-mermaid --type sequence OAuth2 authorization code flow",
    "/adk:diagram-mermaid --type er <prompt-text>",
])}

When the diagram needs to live comfortably in markdown or be easy to diff in Git, Mermaid is usually the best choice.

---

## Excalidraw For Hand-Drawn Overviews

Use Excalidraw when the goal is an approachable architecture sketch or a whiteboard-style explanation.

{code_block([
    "/adk:diagram-excalidraw <prompt-text>",
    "/adk:diagram-excalidraw system architecture overview with frontend, API, and database",
    "/adk:diagram-excalidraw --palette aws <prompt-text>",
])}

The palette flag is useful when you want the output to visually match a cloud or platform context.

---

## Drawio For Precise Layouts

Use draw.io when exact positioning, rich icon sets, BPMN, or infrastructure layouts matter more than raw text diffs.

{code_block([
    "/adk:diagram-drawio <prompt-text>",
    "/adk:diagram-drawio network topology with firewalls and load balancers",
])}

This is the best fit for enterprise architecture diagrams and cloud/network topology where shapes and placement do a lot of the explanatory work.

---

## Graphviz For Strict Graphs

Use Graphviz when the important part is the graph structure itself: dependency maps, call graphs, import graphs, and other strictly laid out relationships.

{code_block([
    "/adk:diagram-graphviz <prompt-text>",
    "/adk:diagram-graphviz module dependency graph",
    "/adk:diagram-graphviz --layout dot <prompt-text>",
])}

The layout flag lets you steer the graph algorithm when you need a specific hierarchy or visual balance.

---

## Render And Theme Output

All engines can produce rendered assets when you need SVG or PNG output rather than source alone.

{code_block([
    "/adk:diagram-mermaid --render --format png <prompt-text>",
    "/adk:diagram-excalidraw --theme dark <prompt-text>",
])}

Use `--render` when the deliverable is the image asset itself, and use `--theme` when you want a specific light, dark, or dual-theme output.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Let ADK choose the engine | `diagram` | `<prompt-text>`, `--engine`, `--type` |
| Text-first flow, sequence, state, ER, or timeline | `diagram-mermaid` | `<prompt-text>`, `--type`, `--render`, `--format` |
| Hand-drawn architecture overview | `diagram-excalidraw` | `<prompt-text>`, `--palette`, `--theme` |
| Precise enterprise or network layout | `diagram-drawio` | `<prompt-text>` |
| Dependency or call graph | `diagram-graphviz` | `<prompt-text>`, `--layout` |

## Related Skills

- **[`docs-write`](/reference/skill-docs-write/)** when the diagram is part of a larger document.
- **[`spec`](/reference/skill-spec/)** when the diagram is a supporting artifact for a durable technical specification.
- **[`design`](/reference/skill-design/)** when the task is product or UI design rather than technical system visualization.
"""


def render_research_planning_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:research <prompt-text>",
        "/adk:research <prompt-text> --deep",
        "/adk:research <prompt-text> --save <path>",
        "/adk:plan --mode brainstorm <prompt-text>",
        "/adk:plan --mode write <prompt-text>",
        "/adk:plan --mode write --spec <path> <prompt-text>",
        "/adk:plan --mode execute --plan <path>",
        "/adk:plan --mode track --plan <path>",
        "/adk:spec --mode write <prompt-text>",
        "/adk:spec --mode write --depth thorough <prompt-text>",
        "/adk:spec --mode analyze <path>",
        "/adk:spec --mode checklist <path>",
        "/adk:spec --mode constitution --action create <prompt-text>",
    ]
    validate_commands(skills, commands)
    return f"""# Research & Planning

These skills work best as a chain: use `research` when you need evidence, `spec` when you need a durable requirements artifact, and `plan` when you know the direction and want an executable sequence of work.

> **Quick start:** when you are still exploring the problem, begin with `/adk:research <prompt-text>`. When the direction is already clear, jump straight to `/adk:plan --mode write <prompt-text>`.

## Scenarios

- [Research A Topic](#research-a-topic)
- [Turn Research Into A Plan](#turn-research-into-a-plan)
- [Execute Or Track A Plan](#execute-or-track-a-plan)
- [Write Or Analyze A Specification](#write-or-analyze-a-specification)
- [Create Governance Rules](#create-governance-rules)

---

## Research A Topic

Use `research` when the job is understanding, comparing, or gathering source-backed evidence.

{code_block([
    "/adk:research <prompt-text>",
    "/adk:research Next.js App Router migration patterns",
    "/adk:research <prompt-text> --deep",
    "/adk:research <prompt-text> --save <path>",
])}

`--deep` is the right upgrade when you need broader evidence, risk analysis, and synthesis. `--save` is useful when the research should become input for later skills.

---

## Turn Research Into A Plan

Use `plan` when you want ADK to convert the current understanding into a sequence of steps.

{code_block([
    "/adk:plan --mode brainstorm <prompt-text>",
    "/adk:plan --mode write <prompt-text>",
    "/adk:plan --mode write --spec <path> <prompt-text>",
])}

Brainstorm mode helps when the approach itself is still open. Write mode is for turning a chosen direction into a concrete implementation plan. Add `--spec` when a formal spec already exists and should constrain the plan.

---

## Execute Or Track A Plan

Once the plan exists, stay in the `plan` skill for execution and progress tracking.

{code_block([
    "/adk:plan --mode execute --plan <path>",
    "/adk:plan --mode track --plan <path>",
])}

Use execute mode when the work is approved and ready to run. Use track mode when you want an up-to-date read on progress, blockers, and remaining work without re-planning from scratch.

---

## Write Or Analyze A Specification

Use `spec` when the missing artifact is a durable requirements document or a formal analysis of an existing spec.

{code_block([
    "/adk:spec --mode write <prompt-text>",
    "/adk:spec --mode write --depth thorough <prompt-text>",
    "/adk:spec --mode analyze <path>",
    "/adk:spec --mode checklist <path>",
])}

Write mode creates the specification, analyze mode audits an existing one, and checklist mode turns the requirements into a quality checklist you can use as a validation gate.

---

## Create Governance Rules

Use constitution mode when the output should be a durable set of principles or quality gates for later work.

{code_block([
    "/adk:spec --mode constitution --action create <prompt-text>",
])}

This is useful when a team needs explicit non-negotiables that future planning, implementation, and review workflows should honor.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Research and compare options | `research` | `<prompt-text>`, `--deep`, `--save` |
| Brainstorm or write a plan | `plan` | `--mode brainstorm`, `--mode write`, `--spec` |
| Execute or track a plan | `plan` | `--mode execute`, `--mode track`, `--plan` |
| Write a new specification | `spec` | `--mode write`, `--depth` |
| Analyze or checklist an existing spec | `spec` | `--mode analyze`, `--mode checklist`, `<path>` |
| Define governance or quality gates | `spec` | `--mode constitution`, `--action` |

## Related Skills

- **[`dev-build`](/reference/skill-dev-build/)** when the plan is ready to turn into implementation.
- **[`docs-write`](/reference/skill-docs-write/)** when the research or spec should be published as a polished document.
- **[`audit`](/reference/skill-audit/)** when you want to check existing code against the standards or intent you just documented.
"""


def render_audits_quality_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:audit <prompt-text>",
        "/adk:audit --focus security",
        "/adk:audit --focus performance",
        "/adk:audit --focus dependency",
        "/adk:audit --focus codebase --scope <path>",
        "/adk:audit --format pr",
        "/adk:audit --publish",
        "/adk:test <path>",
        "/adk:test <path> --scope <path>",
        "/adk:test <path> --mode auto-approve",
    ]
    validate_commands(skills, commands)
    return f"""# Audits & Quality

Use `audit` when you want findings and prioritization without modifying code. Use `test` when the job is walking through acceptance checks against a plan, spec, or deliverable.

> **Quick start:** `/adk:audit <prompt-text>` is the easiest way to ask for a quality pass without deciding the focus up front.

## Scenarios

- [Run A Focused Audit](#run-a-focused-audit)
- [Scope Or Publish The Result](#scope-or-publish-the-result)
- [Run User Acceptance Testing](#run-user-acceptance-testing)

---

## Run A Focused Audit

`audit` can stay broad or narrow itself to one dimension. Start broad when you are not sure what matters most, then switch to a focus flag once you know the lens you want.

{code_block([
    "/adk:audit <prompt-text>",
    "/adk:audit review this service for quality and security issues",
    "/adk:audit --focus security",
    "/adk:audit --focus performance",
    "/adk:audit --focus dependency",
    "/adk:audit --focus codebase --scope <path>",
])}

Use `--focus security` for auth and data-handling risk, `--focus performance` for latency or memory concerns, `--focus dependency` for package risk, and `--focus codebase` for broader structural quality.

---

## Scope Or Publish The Result

The same audit can be packaged differently depending on what the output needs to do next.

{code_block([
    "/adk:audit --format pr",
    "/adk:audit --publish",
])}

Use `--format pr` when the findings should read like a remediation checklist and `--publish` when the audit needs to land in a document destination instead of staying in the conversation.

---

## Run User Acceptance Testing

Use `test` when you want ADK to turn a spec, plan, or other source document into guided acceptance testing.

{code_block([
    "/adk:test <path>",
    "/adk:test ./docs/specs/auth-spec.md",
    "/adk:test <path> --scope <path>",
    "/adk:test <path> --mode auto-approve",
])}

This is the right path when you want a structured walkthrough of expectations rather than a code audit.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Broad or focused audit | `audit` | `<prompt-text>`, `--focus`, `--scope` |
| PR-style remediation checklist | `audit` | `--format pr` |
| Publish the audit artifact | `audit` | `--publish` |
| Acceptance testing from a spec or plan | `test` | `<path>`, `--scope`, `--mode` |

## Related Skills

- **[`code-review-repo`](/reference/skill-code-review-repo/)** when you want a holistic repository review with improvement planning.
- **[`dev-build`](/reference/skill-dev-build/)** when an audit finding turns into implementation work.
- **[`plan`](/reference/skill-plan/)** when the audit results need to become sequenced remediation work.
"""


def render_project_management_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:project <prompt-text>",
        "/adk:project --mode init <prompt-text>",
        "/adk:project --mode milestone --action create <prompt-text>",
        "/adk:project --mode milestone --action track",
        "/adk:project --mode milestone --action audit",
        "/adk:project --mode idea <prompt-text>",
        "/adk:project --mode idea --action review",
        "/adk:handoff --mode handoff",
        "/adk:handoff --mode handoff --note <prompt-text>",
        "/adk:handoff --mode handoff --action resume",
        "/adk:handoff --mode handoff --action resume --session <session-name>",
        "/adk:handoff --mode context-thread --action create --name <name>",
        "/adk:handoff --mode context-thread --action update --name <name> --note <prompt-text>",
        "/adk:team <prompt-text>",
        "/adk:team --mode multi --strategy merge <prompt-text>",
        "/adk:team --mode multi --strategy vote <prompt-text>",
        "/adk:team --mode team --roles <name> <prompt-text>",
        "/adk:team --mode multi --timeout 120 <prompt-text>",
    ]
    validate_commands(skills, commands)
    return f"""# Project Management

The project-management skills help when the work is bigger than a single code change: starting new efforts, shaping milestones, parking ideas, preserving context between sessions, or coordinating parallel agent work.

> **Quick start:** `/adk:project <prompt-text>` is the best starting point when you want to bootstrap a project or shape roadmap work.

## Scenarios

- [Start Or Shape A Project](#start-or-shape-a-project)
- [Manage Milestones And Ideas](#manage-milestones-and-ideas)
- [Hand Off Or Resume Work](#hand-off-or-resume-work)
- [Coordinate Agent Teams](#coordinate-agent-teams)

---

## Start Or Shape A Project

Use `project` when the output should be a project artifact: a bootstrap plan, an initialized project direction, a roadmap milestone, or an idea captured for later work.

{code_block([
    "/adk:project <prompt-text>",
    "/adk:project bootstrap a new CLI tool for managing dotfiles",
    "/adk:project --mode init <prompt-text>",
])}

The plain invocation is usually enough because the skill can infer whether you are starting a project or talking about the roadmap.

---

## Manage Milestones And Ideas

Use the explicit project modes when you already know whether the work is milestone management or idea capture.

{code_block([
    "/adk:project --mode milestone --action create <prompt-text>",
    "/adk:project --mode milestone --action track",
    "/adk:project --mode milestone --action audit",
    "/adk:project --mode idea <prompt-text>",
    "/adk:project --mode idea --action review",
])}

Milestone mode is for roadmap work that already belongs to the execution track. Idea mode is for backlog parking-lot work that is not ready for specs or plans yet.

---

## Hand Off Or Resume Work

Use `handoff` when continuity is the main problem rather than the task itself.

{code_block([
    "/adk:handoff --mode handoff",
    "/adk:handoff --mode handoff --note <prompt-text>",
    "/adk:handoff --mode handoff --action resume",
    "/adk:handoff --mode handoff --action resume --session <session-name>",
    "/adk:handoff --mode context-thread --action create --name <name>",
    "/adk:handoff --mode context-thread --action update --name <name> --note <prompt-text>",
])}

Use handoff mode for pause/resume between sessions, and context-thread mode when you want a named stream of persistent project context that can be updated over time.

---

## Coordinate Agent Teams

Use `team` when the work itself should be parallelized across multiple models or multiple specialized agents.

{code_block([
    "/adk:team <prompt-text>",
    "/adk:team --mode multi --strategy merge <prompt-text>",
    "/adk:team --mode multi --strategy vote <prompt-text>",
    "/adk:team --mode team --roles <name> <prompt-text>",
    "/adk:team --mode multi --timeout 120 <prompt-text>",
])}

Multi mode compares or merges multiple model runs of the same task. Team mode is for explicit role-based decomposition when different agents should own different slices of the work.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Bootstrap or shape a project | `project` | `<prompt-text>`, `--mode init` |
| Manage milestones or capture ideas | `project` | `--mode milestone`, `--mode idea`, `--action` |
| Pause, resume, or preserve context | `handoff` | `--mode`, `--action`, `--note`, `--session` |
| Compare models or dispatch agent teams | `team` | `<prompt-text>`, `--mode`, `--strategy`, `--roles`, `--timeout` |

## Related Skills

- **[`plan`](/reference/skill-plan/)** when a milestone or idea becomes concrete execution work.
- **[`spec`](/reference/skill-spec/)** when the next artifact should be a durable requirements document.
- **[`dev-build`](/reference/skill-dev-build/)** when planning is done and implementation should start.
"""


def render_setup_config_guide(skills: dict[str, dict]) -> str:
    commands = [
        "/adk:setup",
        "/adk:setup --type tools",
        "/adk:setup --type mcps",
        "/adk:setup --type hooks",
        "/adk:setup --type config",
        "/adk:setup --check-only",
        "/adk:setup --tool gh",
        "/adk:setup --server github",
        "/adk:setup --ide cursor",
        "/adk:setup --skip-update",
    ]
    validate_commands(skills, commands)
    return f"""# Setup & Configuration

Use `setup` when the important job is making the DevKit environment healthy: tools installed, MCP servers configured, hooks in place, and default routing set correctly.

> **Quick start:** `/adk:setup` performs the full setup path and is safe to re-run because the skill is idempotent.

## Scenarios

- [Run Full Setup](#run-full-setup)
- [Check Status Without Changing Anything](#check-status-without-changing-anything)
- [Install One Class Of Dependency](#install-one-class-of-dependency)
- [Target One Tool Or MCP Server](#target-one-tool-or-mcp-server)
- [Know Which Tokens Matter](#know-which-tokens-matter)

---

## Run Full Setup

Run the full setup when you want tools, MCPs, hooks, and routing defaults handled together.

{code_block([
    "/adk:setup",
    "/adk:setup --type tools",
    "/adk:setup --type mcps",
    "/adk:setup --type hooks",
    "/adk:setup --type config",
])}

Use the type flag when you already know you only want one slice of the setup surface instead of the full pass.

---

## Check Status Without Changing Anything

Use check-only mode when you want an inventory first.

{code_block([
    "/adk:setup --check-only",
    "/adk:setup --skip-update",
])}

`--check-only` avoids changes entirely. `--skip-update` still installs missing items, but it will not upgrade anything that is already present.

---

## Install One Class Of Dependency

Sometimes the environment is mostly healthy and only one area needs work.

{code_block([
    "/adk:setup --type tools",
    "/adk:setup --type mcps",
])}

Tool setup is for CLI binaries like `gh`, `diagramkit`, and `pagesmith`. MCP setup is for platform connectivity such as GitHub, Bitbucket, Confluence, and Google Drive.

---

## Target One Tool Or MCP Server

When the issue is very specific, narrow the command to one target.

{code_block([
    "/adk:setup --tool gh",
    "/adk:setup --server github",
    "/adk:setup --ide cursor",
])}

Use `--tool` for one CLI dependency, `--server` for one MCP definition, and `--ide` when the MCP configuration should be written for a specific AI client.

---

## Know Which Tokens Matter

The `setup` skill reads or syncs these environment variables from `~/.zshenv` when MCP configuration requires them:

| Integration | Variables |
|-------------|-----------|
| GitHub MCP | `GITHUB_PAT` |
| Bitbucket MCP | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence MCP | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive MCP | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

GitHub CLI authentication is still handled through `gh auth login`, but the GitHub MCP configuration path uses `GITHUB_PAT`.

---

## Which Parameters To Use?

| Scenario | Parameters |
|----------|-----------|
| Full setup | no flags, or `--type all` |
| Check health without changing anything | `--check-only` |
| Tools only | `--type tools` or `--tool <name>` |
| MCPs only | `--type mcps` or `--server <name>` |
| Target one IDE for MCP config | `--ide <name>` |
| Install missing but do not upgrade | `--skip-update` |

## Related Skills

- **[`preflight-check`](/reference/skill-preflight-check/)** for per-skill dependency validation at runtime.
- **[`project`](/reference/skill-project/)** when the next problem is bootstrapping project work rather than bootstrapping the environment.
"""


def build_skill_object(skill_dir: Path) -> dict:
    text = skill_dir.joinpath("SKILL.md").read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(str(skill_dir))
    body = strip_frontmatter(text)
    raw_description = str(frontmatter.get("description", ""))
    tier = str(frontmatter.get("workflow-tier", ""))
    tags = extract_tags(raw_description)
    h2_sections = parse_h2_sections(body)
    help_content = h2_sections.get("Help", "")
    help_sections = parse_h3_sections(help_content)
    parameters_source = h2_sections.get("Parameters", "") or help_sections.get("Parameters", "") or help_content
    parameters_table = first_markdown_table(parameters_source)
    examples_source = h2_sections.get("Examples", "") or help_sections.get("Examples", "") or help_content
    parameter_rows = parse_markdown_table(parameters_table)
    example_lines = extract_example_lines(examples_source)
    return {
        "slug": skill_dir.name,
        "name": str(frontmatter.get("name", skill_dir.name)),
        "raw_description": raw_description,
        "clean_description": clean_description(raw_description),
        "tier": tier,
        "family": str(frontmatter.get("workflow-family", "")),
        "maturity": str(frontmatter.get("maturity", "stable")),
        "user_invocable": boolish(frontmatter.get("user-invocable")),
        "tags": tags,
        "area": extract_area(raw_description) or infer_area_from_name(str(frontmatter.get("name", skill_dir.name))),
        "category": derive_category(tier, tags),
        "intro": first_paragraph_after_h1(body),
        "h2_sections": h2_sections,
        "help_h3": help_sections,
        "parameters_table": parameters_table,
        "parameter_rows": parameter_rows,
        "example_lines": example_lines,
        "argument_hint": infer_argument_hint(parameter_rows, example_lines),
    }


def cleanup_stale_reference_pages(skills: dict[str, dict]) -> None:
    keep = {f"skill-{skill['slug']}.md" for skill in skills.values()} | STATIC_REFERENCE_PAGES
    for path in REFERENCE_DIR.glob("skill-*.md"):
        if path.name not in keep:
            path.unlink()


def cleanup_stale_guide_pages() -> None:
    keep = set(GUIDE_FRONTMATTER)
    if not GUIDE_DIR.exists():
        return
    for path in GUIDE_DIR.iterdir():
        if not path.is_dir():
            continue
        readme = path / "README.md"
        if readme.exists() and path.name not in keep:
            readme.unlink()


def main() -> None:
    skill_dirs = iter_published_skill_dirs()
    if not skill_dirs:
        raise SystemExit("No published adk-* skills found.")
    skills = {
        skill_dir.name: build_skill_object(skill_dir)
        for skill_dir in skill_dirs
    }

    for skill in skills.values():
        reference_path = REFERENCE_DIR / f"skill-{skill['slug']}.md"
        reference_path.parent.mkdir(parents=True, exist_ok=True)
        reference_path.write_text(build_reference_page(skill), encoding="utf-8")

    (REFERENCE_DIR / "skills" / "README.md").write_text(build_skill_index(skills), encoding="utf-8")

    for slug in GUIDE_FRONTMATTER:
        guide_path = GUIDE_DIR / slug / "README.md"
        guide_path.parent.mkdir(parents=True, exist_ok=True)
        guide_path.write_text(render_guide(slug, skills), encoding="utf-8")

    cleanup_stale_reference_pages(skills)
    cleanup_stale_guide_pages()

    print(f"Updated {len(skills)} skill reference pages")
    print("Updated docs/reference/skills/README.md")
    print(f"Updated {len(GUIDE_FRONTMATTER)} guide pages")


if __name__ == "__main__":
    main()
