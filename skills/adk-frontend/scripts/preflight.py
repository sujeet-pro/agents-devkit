#!/usr/bin/env python3
"""ADK Frontend preflight: detect the frontend technology stack from package.json."""

import json
import os
import sys
from pathlib import Path


def find_package_json(scope: str, max_depth: int = 3) -> Path | None:
    """Walk up from scope directory to find the nearest package.json."""
    current = Path(scope).resolve()
    for _ in range(max_depth + 1):
        candidate = current / "package.json"
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            break
        current = parent
    return None


def detect_stack(scope: str = ".") -> dict:
    """Detect frontend technology stack from package.json."""
    result = {
        "found": False,
        "stack": [],
        "framework": None,
        "bundler": None,
        "cssFramework": None,
        "typescript": False,
        "references": [],
        "packageJsonPath": None,
    }

    pkg_path = find_package_json(scope)
    if pkg_path is None:
        # Check for index.html as fallback
        index_html = Path(scope).resolve() / "index.html"
        if index_html.is_file():
            result["found"] = True
            result["stack"] = ["html", "css", "js"]
            result["references"] = [
                "html-guidelines.md",
                "css-guidelines.md",
                "javascript-guidelines.md",
            ]
            return result
        return result

    result["found"] = True
    result["packageJsonPath"] = str(pkg_path)

    try:
        with open(pkg_path) as f:
            pkg = json.load(f)
    except (json.JSONDecodeError, OSError):
        result["stack"] = ["html", "css", "js"]
        result["references"] = [
            "html-guidelines.md",
            "css-guidelines.md",
            "javascript-guidelines.md",
        ]
        return result

    all_deps = {}
    all_deps.update(pkg.get("dependencies", {}))
    all_deps.update(pkg.get("devDependencies", {}))
    dep_names = set(all_deps.keys())

    # Always include baseline for frontend projects
    stack = ["html", "css", "js"]
    references = [
        "html-guidelines.md",
        "css-guidelines.md",
        "javascript-guidelines.md",
    ]

    # TypeScript detection
    if "typescript" in dep_names or (pkg_path.parent / "tsconfig.json").is_file():
        result["typescript"] = True

    # Framework detection (ordered by specificity)
    if "next" in dep_names:
        result["framework"] = "nextjs"
        stack.append("react")
        stack.append("nextjs")
        references.append("react-guidelines.md")
        references.append("nextjs-guidelines.md")
    elif "react" in dep_names:
        result["framework"] = "react"
        stack.append("react")
        references.append("react-guidelines.md")
    elif "vue" in dep_names:
        result["framework"] = "vue"
        # Vue references TBD
    elif "svelte" in dep_names or "@sveltejs/kit" in dep_names:
        result["framework"] = "svelte"
    elif "@angular/core" in dep_names:
        result["framework"] = "angular"
    elif "astro" in dep_names:
        result["framework"] = "astro"

    # Bundler detection
    if "vite" in dep_names:
        result["bundler"] = "vite"
    elif "webpack" in dep_names or "webpack-cli" in dep_names:
        result["bundler"] = "webpack"
    elif "parcel" in dep_names:
        result["bundler"] = "parcel"
    elif "next" in dep_names:
        result["bundler"] = "next-builtin"
    elif "esbuild" in dep_names:
        result["bundler"] = "esbuild"

    # CSS framework detection
    if "tailwindcss" in dep_names:
        result["cssFramework"] = "tailwind"
    elif "@chakra-ui/react" in dep_names:
        result["cssFramework"] = "chakra-ui"
    elif "@mui/material" in dep_names:
        result["cssFramework"] = "mui"
    elif "styled-components" in dep_names:
        result["cssFramework"] = "styled-components"
    elif "@emotion/react" in dep_names:
        result["cssFramework"] = "emotion"

    result["stack"] = stack
    result["references"] = references
    return result


def main():
    scope = sys.argv[1] if len(sys.argv) > 1 else "."

    # Handle --stack override
    forced_stack = None
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--stack" and i + 1 < len(sys.argv):
            forced_stack = sys.argv[i + 1]
            break
        if arg.startswith("--stack="):
            forced_stack = arg.split("=", 1)[1]
            break

    if forced_stack and forced_stack != "auto":
        techs = [t.strip() for t in forced_stack.split(",")]
        ref_map = {
            "html": "html-guidelines.md",
            "css": "css-guidelines.md",
            "js": "javascript-guidelines.md",
            "react": "react-guidelines.md",
            "nextjs": "nextjs-guidelines.md",
        }
        references = [ref_map[t] for t in techs if t in ref_map]
        result = {
            "found": True,
            "stack": techs,
            "framework": "nextjs" if "nextjs" in techs else ("react" if "react" in techs else None),
            "bundler": None,
            "cssFramework": None,
            "typescript": False,
            "references": references,
            "packageJsonPath": None,
            "forced": True,
        }
    else:
        result = detect_stack(scope)

    json.dump(result, sys.stdout, indent=2)
    print()

    if not result["found"]:
        print("WARNING: No frontend project detected. Skill will not auto-load.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
