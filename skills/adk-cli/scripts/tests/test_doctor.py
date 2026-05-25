"""Smoke tests for doctor.py — the registry returns the right shape and the
plain-text renderer handles each status without crashing.
"""
from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

import doctor


def test_all_checks_returns_well_formed_results():
    results = doctor.all_checks()
    assert results, "doctor should run at least one check"
    for r in results:
        assert set(r.keys()) >= {"status", "label", "detail"}
        assert r["status"] in (doctor.PASS, doctor.WARN, doctor.FAIL), r
        assert isinstance(r["label"], str) and r["label"]


def test_plain_render_includes_every_label():
    fake_results = [
        {"status": doctor.PASS, "label": "alpha", "detail": "ok"},
        {"status": doctor.WARN, "label": "beta",  "detail": "missing"},
        {"status": doctor.FAIL, "label": "gamma", "detail": "broken"},
    ]
    buf = io.StringIO()
    with redirect_stdout(buf):
        doctor._render_plain(fake_results)
    out = buf.getvalue()
    for r in fake_results:
        assert r["label"] in out
        assert r["status"].upper() in out


def test_main_returns_1_on_failure(monkeypatch):
    monkeypatch.setattr(doctor, "all_checks", lambda: [
        {"status": doctor.FAIL, "label": "x", "detail": ""},
    ])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = doctor.main(["--json"])
    assert rc == 1


def test_main_returns_0_on_pass(monkeypatch):
    monkeypatch.setattr(doctor, "all_checks", lambda: [
        {"status": doctor.PASS, "label": "x", "detail": ""},
    ])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = doctor.main(["--json"])
    assert rc == 0


def test_main_returns_1_on_warn_with_strict(monkeypatch):
    monkeypatch.setattr(doctor, "all_checks", lambda: [
        {"status": doctor.WARN, "label": "x", "detail": ""},
    ])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = doctor.main(["--strict", "--json"])
    assert rc == 1


def test_completion_checks_include_zsh_file(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    results = doctor.completion_checks()
    labels = {r["label"] for r in results}
    assert "zsh completion file" in labels
    assert "zsh completion registered" in labels


def test_main_completion_uses_completion_checks(monkeypatch):
    monkeypatch.setattr(doctor, "completion_checks", lambda: [
        {"status": doctor.PASS, "label": "completion-only", "detail": ""},
    ])
    monkeypatch.setattr(doctor, "all_checks", lambda: [
        {"status": doctor.FAIL, "label": "full-check", "detail": ""},
    ])
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = doctor.main(["--completion", "--json"])
    assert rc == 0
    assert "completion-only" in buf.getvalue()
    assert "full-check" not in buf.getvalue()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
