"""§6.y.1 review reply + §6.z auto-approve gate tests."""
from __future__ import annotations

from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import slack_helpers


# ----- §6.y.1 render_review_reply ------------------------------------------

def test_render_three_section_shape_approve():
    text = slack_helpers.render_review_reply(
        host="bitbucket", owner="lastbrand", repo="ecomm-ssr",
        pr_number=5559, pr_url="https://bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5559",
        head_sha="f6a31aae8c9d", author_login=None,
        status="approved", summary_tldr="analytics-only hotfix, tests cover both paths",
        bullets=["Posted 3 appreciations", "0 inline issues"],
    )
    lines = text.split("\n")
    # Line 1: emoji + verdict + tldr
    assert lines[0].startswith("✅ *Approved* —")
    assert "analytics-only hotfix" in lines[0]
    # Line 2: identity + status + head + author
    assert "📌" in lines[1]
    assert "`lastbrand/ecomm-ssr#5559`" in lines[1]
    assert "status `approved`" in lines[1]
    assert "head `f6a31aae8c9d`" in lines[1]
    # Bullets
    assert any("Posted 3 appreciations" in ln for ln in lines[2:])
    assert any("0 inline issues" in ln for ln in lines[2:])
    # URL bullet always present
    assert any("🔗" in ln and "bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5559" in ln
               for ln in lines)


def test_render_uses_plain_at_login_when_no_mapping(tmp_path, monkeypatch):
    """No mapping for the github login → falls back to @login (not <@U…>)."""
    monkeypatch.setenv("ADK_HOME", str(tmp_path))
    text = slack_helpers.render_review_reply(
        host="github", owner="acme", repo="foo", pr_number=42,
        pr_url="https://github.com/acme/foo/pull/42", head_sha="abc",
        author_login="some-unknown-user", status="comments",
        summary_tldr="2 should-have findings", bullets=[],
    )
    assert "@some-unknown-user" in text
    assert "<@U" not in text


def test_render_uses_slack_user_id_when_mapping_exists(tmp_path, monkeypatch):
    """Mapping present in core.yaml → uses <@U…> notation."""
    cfg_dir = tmp_path / ".agents-devkit" / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "core.yaml").write_text(
        "user_mappings:\n"
        "  github_to_slack:\n"
        "    sujeet-pro: U123ABC\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("ADK_HOME", str(tmp_path / ".agents-devkit"))
    text = slack_helpers.render_review_reply(
        host="github", owner="acme", repo="foo", pr_number=1,
        pr_url="https://github.com/acme/foo/pull/1", head_sha="abc",
        author_login="sujeet-pro", status="approved",
        summary_tldr="green", bullets=[],
    )
    assert "<@U123ABC>" in text
    assert "@sujeet-pro" not in text  # plain form is suppressed when mapping wins


def test_render_truncates_line_1_at_100_chars():
    long = "x" * 200
    text = slack_helpers.render_review_reply(
        host="github", owner="acme", repo="foo", pr_number=1,
        pr_url="https://github.com/acme/foo/pull/1", head_sha=None,
        author_login=None, status="approved",
        summary_tldr=long, bullets=[],
    )
    line1 = text.split("\n")[0]
    assert len(line1) <= 100
    assert line1.endswith("…")


def test_render_caps_bullets_at_6():
    text = slack_helpers.render_review_reply(
        host="github", owner="acme", repo="foo", pr_number=1,
        pr_url="https://github.com/acme/foo/pull/1", head_sha=None,
        author_login=None, status="comments", summary_tldr="x",
        bullets=[f"finding {i}" for i in range(20)],
    )
    bullet_lines = [ln for ln in text.split("\n") if ln.startswith("•")]
    # 6 caller bullets + 1 URL bullet = 7 total
    assert len(bullet_lines) == 7


def test_render_bullet_truncated_at_80():
    long = "x" * 200
    text = slack_helpers.render_review_reply(
        host="github", owner="acme", repo="foo", pr_number=1,
        pr_url="https://github.com/acme/foo/pull/1", head_sha=None,
        author_login=None, status="comments", summary_tldr="x",
        bullets=[long],
    )
    bullet_lines = [ln for ln in text.split("\n") if ln.startswith("•")]
    long_bullet = bullet_lines[0]
    # • + space + 77 chars + … = 80 + the "• " prefix
    assert len(long_bullet) <= 82  # account for "• " prefix


# ----- §6.z auto-approve gate ----------------------------------------------

def test_approve_ready_on_zero_findings():
    ok, reason = slack_helpers.compute_approve_ready(
        findings=[], existing_comment_actions=[], pr_state="OPEN",
    )
    assert ok is True
    assert reason is None


def test_approve_ready_with_appreciations_only():
    findings = [
        {"severity": "appreciation", "title": "great tests"},
        {"severity": "appreciation", "title": "clear naming"},
    ]
    ok, _ = slack_helpers.compute_approve_ready(findings=findings, pr_state="OPEN")
    assert ok is True


def test_blocked_by_should_have():
    findings = [{"severity": "should-have", "title": "validate input"}]
    ok, reason = slack_helpers.compute_approve_ready(findings=findings, pr_state="OPEN")
    assert ok is False
    assert "should-have" in reason


def test_blocked_by_blocker():
    findings = [{"severity": "blocker"}, {"severity": "may-have"}]
    ok, reason = slack_helpers.compute_approve_ready(findings=findings, pr_state="OPEN")
    assert ok is False


def test_not_blocked_by_may_have_only():
    findings = [
        {"severity": "may-have"}, {"severity": "nitpick"},
        {"severity": "question"}, {"severity": "appreciation"},
    ]
    ok, _ = slack_helpers.compute_approve_ready(findings=findings, pr_state="OPEN")
    assert ok is True


def test_blocked_by_no_approve_flag():
    ok, reason = slack_helpers.compute_approve_ready(
        findings=[], no_approve_flag=True, pr_state="OPEN",
    )
    assert ok is False
    assert "no-approve" in reason


def test_blocked_by_terminal_pr_state():
    ok, reason = slack_helpers.compute_approve_ready(
        findings=[], pr_state="MERGED",
    )
    assert ok is False
    assert "MERGED" in reason


def test_fresh_reopens_block_approve():
    """Bot reopened a prior thread because of a NEW finding → block."""
    actions = [{"decision": "reopen"}]
    ok, reason = slack_helpers.compute_approve_ready(
        findings=[], existing_comment_actions=actions, pr_state="OPEN",
    )
    assert ok is False
    assert "reopened" in reason


def test_offline_aligned_reopens_do_not_block():
    """A reopen with offline_alignment_detected=True is a passthrough — NOT a fresh finding."""
    actions = [{"decision": "reopen", "offline_alignment_detected": True}]
    ok, _ = slack_helpers.compute_approve_ready(
        findings=[], existing_comment_actions=actions, pr_state="OPEN",
    )
    assert ok is True
