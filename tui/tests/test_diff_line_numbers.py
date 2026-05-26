"""Tests for the DiffPane custom renderer.

Validates:
- Line-number gutters reflect ``@@ -A,B +C,D @@`` headers.
- Non-contiguous hunks are separated by a ``…`` gap marker.
- Additions / deletions / context lines carry the expected color tokens.
"""
from __future__ import annotations

from tui.widgets.diff_pane import _build_diff_text


_SAMPLE = """diff --git a/foo.py b/foo.py
index abc..def 100644
--- a/foo.py
+++ b/foo.py
@@ -10,3 +10,4 @@ def f(x):
 context-a
-old-line
+new-line
+extra-new
@@ -50,2 +51,2 @@ class C:
 context-b
-bye
+ciao""".splitlines()


def test_line_numbers_align_with_hunk_headers() -> None:
    text = _build_diff_text(_SAMPLE)
    rendered = text.plain
    # First hunk starts at old=10, new=10.
    assert "10" in rendered
    # Second hunk's new-side starts at 51.
    assert "51" in rendered


def test_gap_marker_appears_between_non_contiguous_hunks() -> None:
    text = _build_diff_text(_SAMPLE)
    rendered = text.plain
    # The ``…`` separator is emitted before the second hunk header.
    # The first hunk should NOT trigger a separator.
    assert "…" in rendered, "gap marker missing between hunks"
    # The separator's right gutter says `…` too.
    rule_count = rendered.count("…")
    assert rule_count >= 2, f"expected at least 2 ellipses (gutter+content), got {rule_count}"


def test_additions_render_in_green() -> None:
    text = _build_diff_text(_SAMPLE)
    # Look at the spans applied to the addition lines.
    green_spans = [
        s for s in text.spans
        if "green" in (str(s.style) or "")
    ]
    assert green_spans, "expected at least one span styled green for additions"


def test_deletions_render_in_red() -> None:
    text = _build_diff_text(_SAMPLE)
    red_spans = [
        s for s in text.spans
        if "red" in (str(s.style) or "")
    ]
    assert red_spans, "expected at least one span styled red for deletions"


def test_file_header_renders_in_bold_cyan() -> None:
    text = _build_diff_text(_SAMPLE)
    cyan_spans = [
        s for s in text.spans
        if "cyan" in (str(s.style) or "")
    ]
    assert cyan_spans, "expected file-header spans styled cyan"


def test_no_gap_marker_when_only_one_hunk() -> None:
    one_hunk = [
        "diff --git a/x b/x",
        "@@ -1,2 +1,2 @@",
        "-a",
        "+b",
    ]
    text = _build_diff_text(one_hunk)
    rendered = text.plain
    # ``…`` is the gap marker — must NOT appear when there's only one hunk
    # (no preceding hunk to gap from).
    assert "…" not in rendered
