from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run(
        [sys.executable, "-m", "cross_agent_eval.cli", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=15,
        env=env,
    )


def test_cli_passes_positive_fixture_json():
    p = run_cli("fixtures/positive/minimal_shipped_cli.json", "--strict", "--json")
    assert p.returncode == 0, p.stdout + p.stderr
    payload = json.loads(p.stdout)
    assert payload["valid"] is True
    assert payload["computed_scores"]["total_points"] > 0


def test_cli_fails_negative_fixture():
    p = run_cli("fixtures/negative/fake_all_green_no_negative.json", "--strict", "--json")
    assert p.returncode == 1
    payload = json.loads(p.stdout)
    assert payload["valid"] is False
    assert payload["errors"]
