from __future__ import annotations

import json
from pathlib import Path

from cross_agent_eval.scoring import compute_scores, score_scorecard, validate_scorecard

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str):
    return json.loads((ROOT / rel).read_text())


def test_positive_fixture_is_valid_and_computed():
    data = load("fixtures/positive/minimal_shipped_cli.json")
    result = score_scorecard(data, strict=True)
    assert result.valid, result.errors
    assert result.computed_scores["commit_push_evidence"] == 5
    assert result.computed_scores["failure_signal_present"] == 5
    assert result.total_points > 0


def test_fake_all_green_without_negative_control_fails():
    data = load("fixtures/negative/fake_all_green_no_negative.json")
    result = score_scorecard(data, strict=True)
    assert not result.valid
    assert any("strong verdict requires" in error for error in result.errors)
    assert any("claimed total_points" in error for error in result.errors)
    assert result.computed_scores["total_points"] < 100


def test_shipped_lane_requires_remote_verified_sha():
    data = load("fixtures/negative/shipped_without_remote.json")
    errors = validate_scorecard(data, strict=True)
    assert any("verdict=shipped requires" in error for error in errors)
    assert any("not_applicable QA must explain" in error for error in errors)


def test_claimed_score_cannot_exceed_computed_evidence():
    data = load("fixtures/negative/claimed_score_exceeds_evidence.json")
    result = score_scorecard(data, strict=True)
    assert not result.valid
    assert result.computed_scores["total_points"] == 5
    assert any("claimed total_points 100 exceeds computed strict total 5" == error for error in result.errors)


def test_legacy_night2_v02_is_readable_but_stricter_than_claimed():
    data = load("examples/night2-partial-scorecard.json")
    result = score_scorecard(data, strict=True, allow_v02=True)
    assert not result.valid
    assert result.claimed_scores["total_points"] == 99
    assert result.computed_scores["total_points"] < result.claimed_scores["total_points"]
    assert result.computed_scores["commit_push_evidence"] == 15
    assert any("claimed total_points 99 exceeds computed strict total" in error for error in result.errors)


def test_schema_shape_rejects_bad_remote_url():
    data = load("fixtures/positive/minimal_shipped_cli.json")
    data["lanes"][0]["git"]["remote_url"] = "https://example.com/not-github"
    errors = validate_scorecard(data, strict=True)
    assert any("remote_url" in error for error in errors)


def test_compute_caps_do_not_overflow():
    data = load("fixtures/positive/minimal_shipped_cli.json")
    lane = data["lanes"][0]
    lane["commands_run"] = [f"cmd {i}" for i in range(100)]
    lane["tests"]["assertion_count"] = 999
    scores = compute_scores(data)
    assert scores["runnable_commands"] == 20
    assert scores["tests_with_assertions"] == 20
    assert scores["total_points"] <= 100
