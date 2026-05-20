#!/usr/bin/env python3
"""chunker.py — AST chunker (tree-sitter primary, heuristic fallback).

Walks <worktree>, emits one row per chunk to a JSONL output. The output
schema is contract-stable; other scripts (embedder.py, query_index.py)
consume it as-is.

Per-chunk: (id, file, line_start, line_end, parent_symbol, language, kind, content, snippet_hash).

Methodology:
  - Primary: tree-sitter via tree-sitter-language-pack. AST-aware boundaries
    for ts/tsx/js/jsx/py/go/java/rust/ruby/markdown/json/yaml/bash/css/scss/html.
    Emits one chunk per top-level declaration + one chunk per method inside a class.
    Pre-declaration content (imports, top-of-file) becomes a `<module>` chunk.
  - Fallback: the previous regex-based chunker, used per-file when tree-sitter
    raises or when the language has no grammar.
  - Hard cap enforcement: any node whose body exceeds `--max-tokens` (default
    1500, est. as len(text)//4) is split at its child AST boundaries; if even
    those are oversized, a final line-window split kicks in.

Usage:
  python3 chunker.py --worktree <path> --out chunks.jsonl
                     [--files-list <path>] [--include <glob>]... [--exclude <glob>]...
                     [--max-tokens 1500] [--min-tokens 50] [--method tree-sitter|heuristic]
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterator, Optional

sys.path.insert(0, str(Path(__file__).parent))
from _lib_common import sha1_hex, get_logger, get_cfg  # noqa: E402


# ---------------- language detection ----------------

LANG_BY_EXT = {
    ".ts": "ts", ".cts": "ts", ".mts": "ts",
    ".tsx": "tsx",
    ".js": "js", ".cjs": "js", ".mjs": "js",
    ".jsx": "jsx",
    ".py": "py",
    ".go": "go",
    ".java": "java",
    ".rs": "rs",
    ".rb": "rb",
    ".md": "md", ".mdx": "md",
    ".json": "json", ".json5": "json",
    ".yaml": "yaml", ".yml": "yaml",
    ".sh": "bash", ".bash": "bash",
    ".css": "css",
    ".scss": "scss", ".sass": "scss",
    ".html": "html", ".htm": "html",
}

# Map our short codes to tree-sitter-language-pack parser names.
TS_PARSER_NAME = {
    "ts": "typescript", "tsx": "tsx",
    "js": "javascript", "jsx": "javascript",
    "py": "python",
    "go": "go",
    "java": "java",
    "rs": "rust",
    "rb": "ruby",
    "md": "markdown",
    "json": "json",
    "yaml": "yaml",
    "bash": "bash",
    "css": "css",
    "scss": "scss",
    "html": "html",
}

# Per-language node types that we emit as their own chunks. A chunk is a
# self-contained unit a reader would expect to retrieve atomically.
CHUNKABLE_NODES: dict[str, set[str]] = {
    "typescript": {
        "function_declaration", "method_definition", "method_signature",
        "class_declaration", "interface_declaration", "type_alias_declaration",
        "enum_declaration", "function_signature",
        "abstract_class_declaration", "abstract_method_signature",
        # Top-level `export const foo = ...` (covers arrow functions assigned to const)
        "lexical_declaration", "variable_declaration",
        "export_statement",  # wraps many of the above
    },
    "tsx": {
        "function_declaration", "method_definition", "method_signature",
        "class_declaration", "interface_declaration", "type_alias_declaration",
        "enum_declaration", "function_signature",
        "abstract_class_declaration", "abstract_method_signature",
        "lexical_declaration", "variable_declaration",
        "export_statement",
    },
    "javascript": {
        "function_declaration", "method_definition", "class_declaration",
        "lexical_declaration", "variable_declaration",
        "export_statement",
    },
    "python": {
        "function_definition", "async_function_definition",
        "class_definition", "decorated_definition",
    },
    "go": {
        "function_declaration", "method_declaration",
        "type_declaration", "const_declaration", "var_declaration",
    },
    "java": {
        "class_declaration", "interface_declaration", "enum_declaration",
        "method_declaration", "constructor_declaration",
        "annotation_type_declaration",
    },
    "rust": {
        "function_item", "struct_item", "enum_item", "trait_item",
        "impl_item", "mod_item", "type_item", "macro_definition",
    },
    "ruby": {
        "class", "module", "method", "singleton_method",
    },
    "markdown": {
        # We special-case markdown: emit one chunk per section under an ATX heading.
    },
    "json": set(),  # whole file
    "yaml": set(),  # whole file
    "bash": {"function_definition"},
    "css": {"rule_set", "at_rule"},
    "scss": {"rule_set", "at_rule", "mixin_statement", "function_statement"},
    "html": set(),  # whole file
}

# A token is roughly 4 chars (ASCII code).
def _approx_tokens(s: str) -> int:
    return max(1, len(s) // 4)


DEFAULT_EXCLUDES = [
    "node_modules/**", "dist/**", "build/**", ".next/**", "out/**",
    "vendor/**", "target/**", "__pycache__/**", "*.min.js", "*.min.css",
    ".git/**", ".temp/**", "coverage/**", "*.lock", "*.lockb",
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "Cargo.lock",
    "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg", "*.ico",
    "*.pdf", "*.zip", "*.tar", "*.gz", "*.mp4", "*.wasm",
]


@dataclass
class Chunk:
    id: str
    file: str
    line_start: int
    line_end: int
    parent_symbol: str
    language: str
    kind: str
    content: str
    snippet_hash: str


def make_chunk(file: str, lines: list[str], start: int, end: int, parent: str,
               lang: str, kind: str) -> Chunk:
    body = "\n".join(lines[start - 1:end])
    snippet_hash = sha1_hex(body)
    cid = sha1_hex(f"{file}|{start}|{snippet_hash}")
    return Chunk(
        id=cid, file=file, line_start=start, line_end=end,
        parent_symbol=parent or "<module>", language=lang, kind=kind,
        content=body, snippet_hash=snippet_hash,
    )


# ---------------- tree-sitter path ----------------

# tree-sitter-language-pack 1.8.x exposes a Rust-binding API where node
# attributes are method calls (`node.kind()`, not `node.type`). The accessors
# below shield the rest of the chunker from that detail.

_PARSER_CACHE: dict[str, object] = {}


def _get_parser(ts_lang: str):
    if ts_lang in _PARSER_CACHE:
        return _PARSER_CACHE[ts_lang]
    from tree_sitter_language_pack import get_parser  # lazy
    p = get_parser(ts_lang)
    _PARSER_CACHE[ts_lang] = p
    return p


def _kind(node) -> str:
    k = node.kind
    return k() if callable(k) else k


def _start_line(node) -> int:
    sp = node.start_position
    sp = sp() if callable(sp) else sp
    return sp.row + 1


def _end_line(node) -> int:
    ep = node.end_position
    ep = ep() if callable(ep) else ep
    return ep.row + 1


def _byte_range(node) -> tuple[int, int]:
    br = node.byte_range
    br = br() if callable(br) else br
    return br.start, br.end


def _children(node):
    cc = node.child_count
    n = cc() if callable(cc) else cc
    return [node.child(i) for i in range(n)]


def _is_chunkable(node, lang_key: str) -> bool:
    return _kind(node) in CHUNKABLE_NODES.get(lang_key, set())


def _node_name(node, src_bytes: bytes) -> Optional[str]:
    """Extract the symbol name from an AST node, trying common shapes."""
    # 1. The 'name' field works for function / class / type / method declarations.
    name = node.child_by_field_name("name")
    if name is not None:
        s, e = _byte_range(name)
        return src_bytes[s:e].decode("utf-8", errors="replace")
    # 2. For export_statement / decorated_definition / async_function_definition wrappers,
    # peek into the first declaration child.
    for child in _children(node):
        if _kind(child) in (
            "function_declaration", "class_declaration", "interface_declaration",
            "type_alias_declaration", "enum_declaration", "lexical_declaration",
            "variable_declaration", "function_definition", "class_definition",
            "method_declaration", "async_function_definition",
        ):
            inner = _node_name(child, src_bytes)
            if inner:
                return inner
    # 3. lexical_declaration / variable_declaration → declarator → name.
    if _kind(node) in ("lexical_declaration", "variable_declaration"):
        for child in _children(node):
            if _kind(child) == "variable_declarator":
                n = child.child_by_field_name("name")
                if n is not None:
                    s, e = _byte_range(n)
                    return src_bytes[s:e].decode("utf-8", errors="replace")
    return None


def _split_oversized_by_lines(
    file_str: str, lines: list[str], start: int, end: int,
    parent: str, lang: str, kind: str, max_chars: int,
) -> list[Chunk]:
    """Sliding-window split. Picks a window so that each chunk stays under
    max_chars. If lines themselves exceed max_chars (minified files), the
    final emitted chunk for that line will still exceed the cap — there's
    no syntactic boundary smaller than a line. That's surfaced as a warning
    in the embedder rather than silently emitting an oversized chunk."""
    body = "\n".join(lines[start - 1:end])
    if len(body) <= max_chars:
        return [make_chunk(file_str, lines, start, end, parent, lang, kind)]
    out: list[Chunk] = []
    i = start
    # Greedy: pack lines until the next line would push us over the cap.
    while i <= end:
        cur_chars = 0
        j = i
        while j <= end:
            line_len = len(lines[j - 1]) + 1  # +1 for the join newline
            if cur_chars + line_len > max_chars and j > i:
                break
            cur_chars += line_len
            j += 1
        out.append(make_chunk(file_str, lines, i, j - 1, parent, lang, kind))
        i = j
    return out


def _chunk_node(
    node, src_bytes: bytes, lines: list[str], file_str: str, lang_short: str, lang_key: str,
    max_chars: int, parent_name: Optional[str] = None,
) -> list[Chunk]:
    """Emit chunks for one chunkable AST node. Recurses into class bodies
    so each method becomes its own chunk."""
    start_line = _start_line(node)
    end_line = _end_line(node)
    name = _node_name(node, src_bytes) or parent_name or "<module>"
    kind = _kind(node)
    body = "\n".join(lines[start_line - 1:end_line])

    container_types = {
        "class_declaration", "abstract_class_declaration",
        "interface_declaration", "class_definition",
        "impl_item", "trait_item", "mod_item",
        "class", "module",
    }
    if kind in container_types:
        method_chunks: list[Chunk] = []
        body_node = node.child_by_field_name("body") or node
        for child in _children(body_node):
            if _is_chunkable(child, lang_key):
                method_chunks.extend(
                    _chunk_node(child, src_bytes, lines, file_str, lang_short, lang_key,
                                max_chars, parent_name=name)
                )
        if method_chunks:
            shell_end = min(end_line, method_chunks[0].line_start - 1)
            if shell_end >= start_line:
                shell_body = "\n".join(lines[start_line - 1:shell_end])
                if len(shell_body) > max_chars:
                    return (
                        _split_oversized_by_lines(file_str, lines, start_line, shell_end,
                                                  name, lang_short, kind, max_chars)
                        + method_chunks
                    )
                return [make_chunk(file_str, lines, start_line, shell_end, name, lang_short, kind)] + method_chunks

    if len(body) <= max_chars:
        return [make_chunk(file_str, lines, start_line, end_line, name, lang_short, kind)]

    # Oversized: split at direct children, then line-window as last resort.
    child_chunks: list[Chunk] = []
    for child in _children(node):
        cs, ce = _start_line(child), _end_line(child)
        cbody = "\n".join(lines[cs - 1:ce])
        if not cbody.strip():
            continue
        ck = _kind(child)
        if len(cbody) <= max_chars:
            child_chunks.append(make_chunk(file_str, lines, cs, ce, name, lang_short, ck))
        else:
            child_chunks.extend(
                _split_oversized_by_lines(file_str, lines, cs, ce, name, lang_short, ck, max_chars)
            )
    if child_chunks:
        return child_chunks
    return _split_oversized_by_lines(file_str, lines, start_line, end_line, name, lang_short, kind, max_chars)


def chunk_code_treesitter(path_rel: str, lang_short: str, content: str,
                          max_chars: int, min_chars: int) -> list[Chunk]:
    """Tree-sitter chunker for a single file. Raises on parse failure;
    caller decides whether to fall back."""
    lang_key = TS_PARSER_NAME.get(lang_short)
    if not lang_key:
        raise ValueError(f"no tree-sitter parser mapping for lang={lang_short}")
    parser = _get_parser(lang_key)
    src_bytes = content.encode("utf-8")
    # tree-sitter-language-pack 1.8 expects str input to .parse(), but byte
    # offsets in the returned tree refer to the UTF-8 encoding — so we keep
    # both representations.
    tree = parser.parse(content)
    root = tree.root_node()
    lines = content.splitlines()
    if not lines:
        return []

    chunks: list[Chunk] = []

    top_level: list = []
    for child in _children(root):
        if _is_chunkable(child, lang_key):
            top_level.append(child)
        elif _kind(child) in ("export_statement", "decorated_definition"):
            # Emit the wrapper if it contains a chunkable inner.
            for inner in _children(child):
                if _is_chunkable(inner, lang_key):
                    top_level.append(child)
                    break

    if not top_level:
        # No structured chunks. Treat the whole file as one chunk (split if oversized).
        return _split_oversized_by_lines(path_rel, lines, 1, len(lines), "<module>",
                                         lang_short, "top-level", max_chars)

    # Module-level prefix (imports, top-of-file constants up to the first declaration).
    first_start = _start_line(top_level[0])
    if first_start > 1:
        prefix_body = "\n".join(lines[:first_start - 1])
        if prefix_body.strip():
            if len(prefix_body) <= max_chars:
                chunks.append(make_chunk(path_rel, lines, 1, first_start - 1, "<module>",
                                         lang_short, "top-level"))
            else:
                chunks.extend(_split_oversized_by_lines(path_rel, lines, 1, first_start - 1,
                                                       "<module>", lang_short, "top-level", max_chars))

    for node in top_level:
        chunks.extend(_chunk_node(node, src_bytes, lines, path_rel, lang_short, lang_key, max_chars))

    # Fold tiny chunks ONLY when they are siblings of the same parent symbol
    # AND immediately adjacent in the source. This catches split halves of an
    # oversized declaration; it does NOT merge unrelated declarations across
    # gaps (the old behavior swallowed entire files into the first chunk).
    if min_chars > 0:
        chunks = _fold_tiny_adjacent(chunks, lines, min_chars)
    return chunks


def _fold_tiny_adjacent(chunks: list[Chunk], lines: list[str], min_chars: int) -> list[Chunk]:
    pruned: list[Chunk] = []
    for c in chunks:
        if (
            len(c.content) < min_chars
            and pruned
            and pruned[-1].parent_symbol == c.parent_symbol
            and c.line_start - pruned[-1].line_end <= 2  # immediately adjacent (allow blank line)
        ):
            prev = pruned[-1]
            merged_lines = lines[prev.line_start - 1:c.line_end]
            new_content = "\n".join(merged_lines)
            new_hash = sha1_hex(new_content)
            pruned[-1] = Chunk(
                id=sha1_hex(f"{prev.file}|{prev.line_start}|{new_hash}"),
                file=prev.file,
                line_start=prev.line_start, line_end=c.line_end,
                parent_symbol=prev.parent_symbol, language=prev.language,
                kind=prev.kind, content=new_content, snippet_hash=new_hash,
            )
        else:
            pruned.append(c)
    return pruned


# ---------------- markdown chunker (heading-based, both paths use it) ----------------

def chunk_markdown(path_rel: str, content: str, max_chars: int) -> list[Chunk]:
    lines = content.splitlines()
    n = len(lines)
    if n == 0:
        return []
    starts = [i + 1 for i, l in enumerate(lines) if re.match(r"^#{1,2}\s+", l)]
    if not starts:
        if len(content) <= max_chars:
            return [make_chunk(path_rel, lines, 1, n, "<doc>", "md", "doc")]
        return _split_oversized_by_lines(path_rel, lines, 1, n, "<doc>", "md", "doc", max_chars)
    if starts[0] > 1:
        starts.insert(0, 1)
    chunks: list[Chunk] = []
    for idx, s in enumerate(starts):
        e = (starts[idx + 1] - 1) if idx + 1 < len(starts) else n
        first = lines[s - 1].lstrip("#").strip()
        body = "\n".join(lines[s - 1:e])
        if len(body) <= max_chars:
            chunks.append(make_chunk(path_rel, lines, s, e, first or "<doc>", "md", "doc"))
        else:
            chunks.extend(_split_oversized_by_lines(path_rel, lines, s, e, first or "<doc>", "md", "doc", max_chars))
    return chunks


# ---------------- heuristic fallback (preserved from prior chunker) ----------------

LANG_PATTERNS: dict[str, list[tuple[str, re.Pattern[str]]]] = {
    "ts": [
        ("class",     re.compile(r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)")),
        ("interface", re.compile(r"^\s*(?:export\s+)?interface\s+(\w+)")),
        ("type",      re.compile(r"^\s*(?:export\s+)?type\s+(\w+)\s*=")),
        ("function",  re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)")),
        ("function",  re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*[:=][^=]*?=\s*(?:async\s*)?\(")),
        ("function",  re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")),
        ("const",     re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=")),
        ("enum",      re.compile(r"^\s*(?:export\s+)?(?:const\s+)?enum\s+(\w+)")),
    ],
    "js": [
        ("class",    re.compile(r"^\s*(?:export\s+default\s+)?class\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>")),
        ("const",    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=")),
    ],
    "py": [
        ("class",    re.compile(r"^\s*class\s+(\w+)")),
        ("function", re.compile(r"^\s*(?:async\s+)?def\s+(\w+)")),
    ],
    "go": [
        ("function", re.compile(r"^\s*func\s+(?:\(\s*\w+\s+\*?\w+\s*\)\s*)?(\w+)\s*\(")),
        ("type",     re.compile(r"^\s*type\s+(\w+)\s+(?:struct|interface|func)")),
    ],
    "java": [
        ("class",     re.compile(r"^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?class\s+(\w+)")),
        ("interface", re.compile(r"^\s*(?:public|private|protected)?\s*interface\s+(\w+)")),
        ("method",    re.compile(r"^\s*(?:public|private|protected)\s+(?:static\s+)?(?:final\s+)?[\w<>\[\],\s]+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{")),
    ],
    "rs": [
        ("function", re.compile(r"^\s*(?:pub\s+(?:\([^)]*\)\s+)?)?(?:async\s+)?fn\s+(\w+)")),
        ("struct",   re.compile(r"^\s*(?:pub\s+)?struct\s+(\w+)")),
    ],
    "rb": [
        ("class",    re.compile(r"^\s*class\s+(\w+)")),
        ("function", re.compile(r"^\s*def\s+(?:self\.)?(\w+)")),
    ],
}


def _detect_indent_block_end(lines: list[str], start: int) -> int:
    n = len(lines)
    if start > n:
        return n
    first = lines[start - 1]
    base_indent = len(first) - len(first.lstrip())
    for i in range(start, n):
        line = lines[i]
        if not line.strip():
            continue
        cur_indent = len(line) - len(line.lstrip())
        if cur_indent <= base_indent and i > start - 1:
            return i
    return n


def _detect_brace_block_end(lines: list[str], start: int) -> int:
    n = len(lines)
    depth = 0
    seen_open = False
    for i in range(start - 1, n):
        line = lines[i]
        for ch in line:
            if ch == "{":
                depth += 1
                seen_open = True
            elif ch == "}":
                depth -= 1
                if seen_open and depth == 0:
                    return i + 1
    return n


def chunk_code_heuristic(path_rel: str, lang: str, content: str,
                         max_chars: int, min_chars: int) -> list[Chunk]:
    lines = content.splitlines()
    n = len(lines)
    if n == 0:
        return []
    # Markdown uses heading-based — handled separately by chunk_markdown.
    # Map js/jsx → js, ts/tsx → ts for heuristic patterns
    pat_lang = {"jsx": "js", "tsx": "ts"}.get(lang, lang)
    patterns = LANG_PATTERNS.get(pat_lang, [])
    matches: list[tuple[int, str, str]] = []
    if patterns:
        for i, line in enumerate(lines, start=1):
            for kind, pat in patterns:
                m = pat.search(line)
                if m and m.lastindex:
                    matches.append((i, kind, m.group(1)))
                    break
    chunks: list[Chunk] = []
    if not matches:
        return _split_oversized_by_lines(path_rel, lines, 1, n, "<module>", lang, "chunk", max_chars)

    if matches[0][0] > 1:
        e = matches[0][0] - 1
        if e >= 1:
            chunks.append(make_chunk(path_rel, lines, 1, e, "<module>", lang, "top-level"))

    for idx, (line_no, kind, name) in enumerate(matches):
        end = (matches[idx + 1][0] - 1) if idx + 1 < len(matches) else n
        if lang in ("py", "rb"):
            end = min(end, _detect_indent_block_end(lines, line_no))
        elif lang in ("ts", "tsx", "js", "jsx", "go", "java", "rs"):
            be = _detect_brace_block_end(lines, line_no)
            end = min(end, be if be >= line_no else end)
        body = "\n".join(lines[line_no - 1:end])
        if len(body) <= max_chars:
            chunks.append(make_chunk(path_rel, lines, line_no, end, name, lang, kind))
        else:
            chunks.extend(_split_oversized_by_lines(path_rel, lines, line_no, end, name, lang, kind, max_chars))

    if min_chars > 0:
        chunks = _fold_tiny_adjacent(chunks, lines, min_chars)
    return chunks


# ---------------- walker / dispatch ----------------

def matched(path: Path, root: Path, includes: list[str], excludes: list[str]) -> bool:
    rel = str(path.relative_to(root))
    for pat in excludes:
        if fnmatch.fnmatch(rel, pat):
            return False
    if not includes:
        return True
    return any(fnmatch.fnmatch(rel, pat) for pat in includes)


def walk(root: Path, includes: list[str], excludes: list[str]) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        keep = []
        for d in dirnames:
            rel = str((Path(dirpath) / d).relative_to(root))
            if not any(fnmatch.fnmatch(rel + "/", pat.replace("**", "*")) for pat in excludes):
                keep.append(d)
        dirnames[:] = keep
        for fn in filenames:
            p = Path(dirpath) / fn
            if matched(p, root, includes, excludes):
                yield p


def iter_files_list(root: Path, files_list_path: Path) -> Iterator[Path]:
    text = files_list_path.read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        rel = line.strip()
        if not rel:
            continue
        p = (root / rel).resolve()
        try:
            p.relative_to(root)
        except ValueError:
            continue
        if p.exists() and p.is_file():
            yield p


def chunk_file(path: Path, root: Path, method: str,
               max_chars: int, min_chars: int, log) -> tuple[list[Chunk], str]:
    """Return (chunks, used_method). used_method ∈ {tree-sitter, heuristic, none}."""
    ext = path.suffix.lower()
    lang = LANG_BY_EXT.get(ext)
    if not lang:
        return [], "none"
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return [], "none"
    if not content.strip():
        return [], "none"
    rel = str(path.relative_to(root))

    # Markdown uses the heading splitter regardless of method.
    if lang == "md":
        try:
            return chunk_markdown(rel, content, max_chars), method or "markdown"
        except Exception as e:
            log.warning("md chunker failed on %s: %s", rel, e)
            return [], "none"

    if method == "tree-sitter":
        try:
            return chunk_code_treesitter(rel, lang, content, max_chars, min_chars), "tree-sitter"
        except Exception as e:
            log.info("tree-sitter failed on %s (%s); falling back to heuristic", rel, e)
    # Heuristic fallback (also the path for method=heuristic).
    try:
        return chunk_code_heuristic(rel, lang, content, max_chars, min_chars), "heuristic"
    except Exception as e:
        log.warning("heuristic chunker failed on %s: %s", rel, e)
        return [], "none"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--worktree", required=True)
    ap.add_argument("--out", required=True, help="JSONL output path")
    ap.add_argument("--include", action="append", default=[])
    ap.add_argument("--exclude", action="append", default=[])
    ap.add_argument("--files-list", default=None)
    ap.add_argument("--limit-files", type=int, default=0)
    ap.add_argument("--method", choices=("tree-sitter", "heuristic"), default=None,
                    help="override the configured chunker method")
    ap.add_argument("--max-tokens", type=int, default=None)
    ap.add_argument("--min-tokens", type=int, default=None)
    args = ap.parse_args()

    method = args.method or get_cfg("chunker.method", default="tree-sitter")
    max_tokens = args.max_tokens or get_cfg("chunker.max_tokens", default=1500)
    min_tokens = args.min_tokens or get_cfg("chunker.min_tokens", default=50)
    max_chars = max_tokens * 4
    min_chars = min_tokens * 4

    root = Path(args.worktree).resolve()
    log = get_logger("chunker")
    excludes = DEFAULT_EXCLUDES + (args.exclude or [])

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    method_counts = {"tree-sitter": 0, "heuristic": 0, "markdown": 0, "none": 0}
    n_files = 0
    n_chunks = 0

    if args.files_list:
        file_iter = iter_files_list(root, Path(args.files_list))
    else:
        file_iter = walk(root, args.include, excludes)

    with out.open("w", encoding="utf-8") as fh:
        for path in file_iter:
            chunks, used = chunk_file(path, root, method, max_chars, min_chars, log)
            method_counts[used] = method_counts.get(used, 0) + 1
            if not chunks:
                continue
            for c in chunks:
                fh.write(json.dumps(asdict(c), ensure_ascii=False) + "\n")
                n_chunks += 1
            n_files += 1
            if args.limit_files and n_files >= args.limit_files:
                break

    print(json.dumps({
        "files": n_files,
        "chunks": n_chunks,
        "out": str(out),
        "method_counts": method_counts,
        "method": method,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
