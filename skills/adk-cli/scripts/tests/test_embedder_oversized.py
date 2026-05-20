"""Tests for the oversized-input short-circuit in embedder.embed_batch
(improvement #8 — wasted retry budget on chunks that ollama always rejects).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def embedder_mod():
    lib = Path(__file__).resolve().parent.parent.parent.parent.parent / "scripts" / "lib" / "code_index"
    sys.path.insert(0, str(lib))
    import embedder
    return embedder


def test_is_oversized_400_matches_known_hints(embedder_mod):
    for msg in (
        "400 Client Error: input length exceeds maximum (5567 > 4096)",
        "Bad Request: input too long",
        "context length exceeded",
        "Error: exceeds maximum number of tokens",
        "too many tokens for this model",
    ):
        assert embedder_mod._is_oversized_400(Exception(msg)) is True, msg


def test_is_oversized_400_ignores_unrelated(embedder_mod):
    for msg in (
        "Connection refused",
        "500 Internal Server Error",
        "timeout",
        "model not found",
    ):
        assert embedder_mod._is_oversized_400(Exception(msg)) is False, msg


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
