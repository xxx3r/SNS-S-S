"""Human-proposed trio research relay must not replace provenance or standing authority."""

from pathlib import Path

from automation.orchestration import render_bootstrap_prompt

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_trio_bootloaders_preserve_question_but_reverify_current_authority():
    common = "recover unresolved scientific questions from accepted results"
    for loop_id in ("daily-governance-triage", "daily-research-operator", "post-game-research"):
        prompt = render_bootstrap_prompt(loop_id)
        assert "CURRENT_MAIN_SHA" in prompt
        assert "default-branch HEAD" in prompt
        assert "as unverified" in prompt
        assert common in prompt
        assert "never as standing authority" in prompt
        assert "discarding repository SHA" not in prompt


def test_relay_uses_existing_receipts_instead_of_new_approval_hops():
    law = read("AGENTS.md")
    assert "Do not create a new governance ledger" in law
    assert "A quest-local NEEDS_SCIENTIFIC_DECISION" in law
    assert "Never open a PR solely to mark the previous lifecycle-only" in law
    assert "full open-issue/PR" in law


def test_roles_share_relay_but_retain_distinct_authority():
    pre = read("automation/contracts/daily-governance-triage.v2.md")
    daily = read("automation/contracts/daily-research-operator.v2.md")
    post = read("automation/contracts/post-game-research.v2.md")
    weekly = read("automation/contracts/weekly-evidence-synthesis.v2.md")
    assert "Do not make another PR just to correct" in pre
    assert "at least one *distinct* active quest" in daily
    assert "zero accepted science" in post
    assert "already-executed protocol" in weekly
    for text in (pre, daily, post):
        assert "validate-standing-request" in text


def test_stable_science_stops_are_explicitly_preserved():
    plan = read("docs/research/trio_research_relay_repair_2026-11-06.md")
    for name in ("sealed SYNTH holdout", "PR #140", "PR #132", "November 15"):
        assert name in plan
