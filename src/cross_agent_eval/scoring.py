from __future__ import annotations

import dataclasses
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "0.3"
VERDICTS = {"strong", "useful", "mixed", "weak", "invalid"}
LANE_VERDICTS = {"shipped", "validated", "drafted", "blocked", "failed"}
TEST_STATUSES = {"pass", "fail", "not_run", "not_applicable"}
QA_STATUSES = {"pass", "fail", "not_applicable", "not_attempted"}
LINT_STATUSES = {"pass", "fail", "mixed", "not_run", "not_applicable"}
SHA_RE = re.compile(r"^[0-9a-f]{7,40}$")
REMOTE_RE = re.compile(r"^(https://github.com/[^\s]+|git@github.com:[^\s]+)$")

SCORE_CAPS = {
    "runnable_commands": 20,
    "tests_with_assertions": 20,
    "commit_push_evidence": 20,
    "deploy_or_live_qa": 15,
    "handoff_lint_signal": 10,
    "external_review_delta": 10,
    "failure_signal_present": 5,
}

REQUIRED_TOP = [
    "schema_version",
    "session_id",
    "session_name",
    "date",
    "agents",
    "guardrails",
    "lanes",
    "failure_signals",
    "overall_verdict",
]
REQUIRED_LANE = [
    "lane_id",
    "name",
    "artifact_paths",
    "commands_run",
    "tests",
    "git",
    "deploy_or_live_qa",
    "handoff_lint",
    "external_review_delta",
    "verdict",
]


class ValidationError(ValueError):
    """Raised when a scorecard fails validation in library use."""


@dataclasses.dataclass(frozen=True)
class ScoreResult:
    valid: bool
    errors: list[str]
    computed_scores: dict[str, int]
    claimed_scores: dict[str, Any]
    summary: dict[str, Any]

    @property
    def total_points(self) -> int:
        return self.computed_scores["total_points"]


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text())


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=10)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return 999, f"{type(exc).__name__}: {exc}"


def _verify_remote_head(remote_url: str, expected_sha: str) -> tuple[bool, str]:
    """Verify that a claimed SHA is reachable from the remote's HEAD ref.

    This is intentionally opt-in because it shells out and may touch the network.
    The default scorer remains deterministic/offline, while cron/CI can add
    `--verify-remote` to stop scorecards from passing on a self-reported
    `remote_sha_verified: true` boolean.
    """
    code, out = _run(["git", "ls-remote", remote_url, "HEAD"])
    if code != 0:
        return False, f"git ls-remote failed: {out[:300]}"
    actual_sha = out.split()[0] if out.split() else ""
    if not actual_sha:
        return False, "git ls-remote returned no HEAD SHA"
    if actual_sha != expected_sha:
        return False, f"remote HEAD {actual_sha} != claimed {expected_sha}"
    return True, f"remote HEAD verified: {actual_sha}"


def count_files(path: Path) -> int:
    if path.is_file():
        return 1
    if not path.is_dir():
        return 0
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules", "__pycache__", ".pytest_cache", ".venv", "venv"}]
        total += len(files)
    return total


def _validate_shape(data: dict[str, Any], *, allow_v02: bool) -> list[str]:
    errors: list[str] = []
    for key in REQUIRED_TOP:
        if key not in data:
            errors.append(f"missing top-level field: {key}")
    version = data.get("schema_version")
    if version != SCHEMA_VERSION and not (allow_v02 and version == "0.2"):
        errors.append(f"schema_version must be '{SCHEMA_VERSION}'" + (" or legacy '0.2'" if allow_v02 else ""))
    if not _is_nonempty_string(data.get("session_id")):
        errors.append("session_id must be a non-empty string")
    if not _is_nonempty_string(data.get("session_name")):
        errors.append("session_name must be a non-empty string")
    if not isinstance(data.get("date"), str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", data.get("date", "")):
        errors.append("date must be YYYY-MM-DD")
    if not isinstance(data.get("agents"), list) or not data.get("agents"):
        errors.append("agents must be a non-empty list")
    if data.get("overall_verdict") not in VERDICTS:
        errors.append(f"overall_verdict must be one of {sorted(VERDICTS)}")
    lanes = data.get("lanes")
    if not isinstance(lanes, list) or not lanes:
        errors.append("lanes must be a non-empty list")
        return errors
    for i, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            errors.append(f"lane {i} is not an object")
            continue
        for key in REQUIRED_LANE:
            if key not in lane:
                errors.append(f"lane {i} missing field: {key}")
        if not isinstance(lane.get("artifact_paths"), list):
            errors.append(f"lane {i}.artifact_paths must be a list")
        if not isinstance(lane.get("commands_run"), list):
            errors.append(f"lane {i}.commands_run must be a list")
        tests = lane.get("tests")
        if not isinstance(tests, dict):
            errors.append(f"lane {i}.tests must be an object")
        else:
            if tests.get("status") not in TEST_STATUSES:
                errors.append(f"lane {i}.tests.status invalid")
            if not isinstance(tests.get("assertion_count"), int) or tests.get("assertion_count", -1) < 0:
                errors.append(f"lane {i}.tests.assertion_count must be a non-negative integer")
        git = lane.get("git")
        if not isinstance(git, dict):
            errors.append(f"lane {i}.git must be an object")
        else:
            if git.get("remote_url") is not None and not REMOTE_RE.match(str(git.get("remote_url"))):
                errors.append(f"lane {i}.git.remote_url must be a GitHub HTTPS/SSH URL or null")
            if git.get("head_sha") is not None and not SHA_RE.match(str(git.get("head_sha"))):
                errors.append(f"lane {i}.git.head_sha must look like a git SHA or null")
            if not isinstance(git.get("remote_sha_verified"), bool):
                errors.append(f"lane {i}.git.remote_sha_verified must be boolean")
        qa = lane.get("deploy_or_live_qa")
        if not isinstance(qa, dict):
            errors.append(f"lane {i}.deploy_or_live_qa must be an object")
        elif qa.get("status") not in QA_STATUSES:
            errors.append(f"lane {i}.deploy_or_live_qa.status invalid")
        handoff = lane.get("handoff_lint")
        if not isinstance(handoff, dict):
            errors.append(f"lane {i}.handoff_lint must be an object")
        elif handoff.get("status") not in LINT_STATUSES:
            errors.append(f"lane {i}.handoff_lint.status invalid")
        if lane.get("verdict") not in LANE_VERDICTS:
            errors.append(f"lane {i}.verdict invalid")
    return errors


def validate_scorecard(
    data: dict[str, Any], *, strict: bool = True, allow_v02: bool = True, verify_remote: bool = False
) -> list[str]:
    """Return validation errors. Empty list means valid.

    `strict=True` enforces evidence consistency, not just schema shape.
    `allow_v02=True` accepts imported Night2 v0.2 examples but still computes strict scores.
    `verify_remote=True` additionally runs `git ls-remote` for lanes that claim
    remote SHA verification. Use it in CI/cron when network is available.
    """
    errors = _validate_shape(data, allow_v02=allow_v02)
    if errors and not strict:
        return errors

    scores = data.get("objective_scores", {}) if isinstance(data.get("objective_scores"), dict) else {}
    computed = compute_scores(data)
    if scores:
        for key, cap in SCORE_CAPS.items():
            value = scores.get(key)
            if not isinstance(value, int) or value < 0 or value > cap:
                errors.append(f"objective_scores.{key} must be integer in [0,{cap}]")
        if scores.get("max_points") not in (None, 100):
            errors.append("objective_scores.max_points must equal 100")
        if scores.get("total_points") is not None and scores.get("total_points") != sum(scores.get(k, 0) for k in SCORE_CAPS):
            errors.append("claimed objective_scores.total_points does not equal claimed subtotal")

    if not strict:
        return errors

    failures = _as_list(data.get("failure_signals"))
    if data.get("overall_verdict") == "strong" and not failures:
        errors.append("strong verdict requires at least one failure signal / negative control")
    if data.get("overall_verdict") == "strong" and computed["failure_signal_present"] == 0:
        errors.append("strong verdict requires a concrete negative-control/failure signal")

    for i, lane in enumerate(_as_list(data.get("lanes"))):
        if not isinstance(lane, dict):
            continue
        git = lane.get("git", {}) if isinstance(lane.get("git"), dict) else {}
        qa = lane.get("deploy_or_live_qa", {}) if isinstance(lane.get("deploy_or_live_qa"), dict) else {}
        tests = lane.get("tests", {}) if isinstance(lane.get("tests"), dict) else {}
        if lane.get("verdict") == "shipped":
            if not (git.get("repo_path") and git.get("remote_url") and git.get("head_sha") and git.get("remote_sha_verified")):
                errors.append(f"lane {i} verdict=shipped requires repo_path, remote_url, head_sha, and remote_sha_verified=true")
            if tests.get("status") != "pass" or tests.get("assertion_count", 0) <= 0:
                errors.append(f"lane {i} verdict=shipped requires passing tests with assertions")
            if qa.get("status") not in {"pass", "not_applicable"}:
                errors.append(f"lane {i} verdict=shipped cannot have failed/not_attempted live QA")
            evidence = str(qa.get("evidence", "")).lower()
            if qa.get("status") == "not_applicable" and not any(term in evidence for term in ["cli", "package", "library", "no web", "not a web"]):
                errors.append(f"lane {i} not_applicable QA must explain package/CLI/non-web reason")
        if git.get("remote_sha_verified") and not (git.get("remote_url") and git.get("head_sha")):
            errors.append(f"lane {i} cannot claim remote_sha_verified without remote_url and head_sha")
        if verify_remote and git.get("remote_sha_verified") and git.get("remote_url") and git.get("head_sha"):
            ok, detail = _verify_remote_head(str(git["remote_url"]), str(git["head_sha"]))
            if not ok:
                errors.append(f"lane {i} remote verification failed: {detail}")

    if scores and scores.get("total_points", computed["total_points"]) > computed["total_points"]:
        errors.append(f"claimed total_points {scores.get('total_points')} exceeds computed strict total {computed['total_points']}")
    return errors


def compute_scores(data: dict[str, Any]) -> dict[str, int]:
    lanes = [lane for lane in _as_list(data.get("lanes")) if isinstance(lane, dict)]
    command_count = sum(len(_as_list(lane.get("commands_run"))) for lane in lanes)
    runnable_commands = min(20, command_count * 4)

    assertion_count = 0
    tested_lanes = 0
    for lane in lanes:
        tests = lane.get("tests", {}) if isinstance(lane.get("tests"), dict) else {}
        if tests.get("status") == "pass":
            assertion_count += int(tests.get("assertion_count", 0) or 0)
            tested_lanes += 1
    tests_with_assertions = min(20, tested_lanes * 4 + assertion_count)

    remote_verified_lanes = 0
    for lane in lanes:
        git = lane.get("git", {}) if isinstance(lane.get("git"), dict) else {}
        if git.get("repo_path") and git.get("remote_url") and git.get("head_sha") and git.get("remote_sha_verified"):
            remote_verified_lanes += 1
    commit_push_evidence = min(20, remote_verified_lanes * 5)

    qa_points = 0
    for lane in lanes:
        qa = lane.get("deploy_or_live_qa", {}) if isinstance(lane.get("deploy_or_live_qa"), dict) else {}
        evidence = str(qa.get("evidence", "")).strip().lower()
        if qa.get("status") == "pass" and len(evidence) >= 20:
            qa_points += 5
        elif qa.get("status") == "not_applicable" and any(term in evidence for term in ["cli", "package", "library", "no web", "not a web"]):
            qa_points += 2
    deploy_or_live_qa = min(15, qa_points)

    handoff_signal = 0
    for lane in lanes:
        handoff = lane.get("handoff_lint", {}) if isinstance(lane.get("handoff_lint"), dict) else {}
        if handoff.get("status") in {"pass", "mixed", "fail"} and _is_nonempty_string(handoff.get("evidence")):
            handoff_signal += 5 if handoff.get("status") in {"mixed", "fail"} else 4
    handoff_lint_signal = min(10, handoff_signal)

    review_count = sum(1 for lane in lanes if _is_nonempty_string(lane.get("external_review_delta")))
    external_review_delta = min(10, review_count * 3)

    failure_text = "\n".join(str(x).lower() for x in _as_list(data.get("failure_signals")))
    has_negative_signal = any(term in failure_text for term in ["fail", "failure", "negative", "blocked", "broken", "regression", "intentional"])
    failure_signal_present = 5 if has_negative_signal else 0

    subtotal = {
        "runnable_commands": runnable_commands,
        "tests_with_assertions": tests_with_assertions,
        "commit_push_evidence": commit_push_evidence,
        "deploy_or_live_qa": deploy_or_live_qa,
        "handoff_lint_signal": handoff_lint_signal,
        "external_review_delta": external_review_delta,
        "failure_signal_present": failure_signal_present,
    }
    return {**subtotal, "total_points": sum(subtotal.values()), "max_points": 100}


def summarize(data: dict[str, Any]) -> dict[str, Any]:
    lanes_summary: list[dict[str, Any]] = []
    total_files = 0
    git_repos = 0
    missing_paths: list[str] = []
    remote_verified = 0
    for lane in _as_list(data.get("lanes")):
        if not isinstance(lane, dict):
            continue
        lane_files = 0
        existing_paths = 0
        for raw in _as_list(lane.get("artifact_paths")):
            p = Path(str(raw)).expanduser()
            if p.exists():
                existing_paths += 1
                lane_files += count_files(p)
            else:
                missing_paths.append(str(p))
        total_files += lane_files
        git_info = lane.get("git", {}) if isinstance(lane.get("git"), dict) else {}
        repo = git_info.get("repo_path")
        git_status = "not_applicable"
        actual_head = None
        remote_status = "not_checked"
        if repo:
            repo_path = Path(str(repo)).expanduser()
            if (repo_path / ".git").exists():
                git_repos += 1
                code, out = _run(["git", "rev-parse", "HEAD"], cwd=str(repo_path))
                actual_head = out.splitlines()[0] if code == 0 and out else None
                code, out = _run(["git", "status", "--short"], cwd=str(repo_path))
                git_status = "clean" if code == 0 and not out else f"dirty_or_unknown: {out[:200]}"
                if git_info.get("remote_sha_verified"):
                    remote_verified += 1
                    remote_status = "claimed_verified"
            else:
                git_status = "repo_path_missing_git"
        lanes_summary.append(
            {
                "lane_id": lane.get("lane_id"),
                "name": lane.get("name"),
                "artifact_files_counted": lane_files,
                "existing_artifact_paths": existing_paths,
                "commands_recorded": len(_as_list(lane.get("commands_run"))),
                "assertion_count": (lane.get("tests") or {}).get("assertion_count") if isinstance(lane.get("tests"), dict) else None,
                "git_status": git_status,
                "remote_status": remote_status,
                "actual_head": actual_head,
                "verdict": lane.get("verdict"),
            }
        )
    return {
        "session_id": data.get("session_id"),
        "session_name": data.get("session_name"),
        "computed_score": f"{compute_scores(data)['total_points']}/100",
        "claimed_score": f"{data.get('objective_scores', {}).get('total_points')}/100" if isinstance(data.get("objective_scores"), dict) else None,
        "overall_verdict": data.get("overall_verdict"),
        "lanes": lanes_summary,
        "totals": {
            "lanes": len(lanes_summary),
            "artifact_files_counted": total_files,
            "git_repos_detected": git_repos,
            "remote_sha_verified_claims": remote_verified,
            "failure_signals": len(_as_list(data.get("failure_signals"))),
            "missing_paths": missing_paths,
        },
    }


def score_scorecard(
    data: dict[str, Any], *, strict: bool = True, allow_v02: bool = True, verify_remote: bool = False
) -> ScoreResult:
    errors = validate_scorecard(data, strict=strict, allow_v02=allow_v02, verify_remote=verify_remote)
    return ScoreResult(
        valid=not errors,
        errors=errors,
        computed_scores=compute_scores(data),
        claimed_scores=data.get("objective_scores", {}) if isinstance(data.get("objective_scores"), dict) else {},
        summary=summarize(data),
    )
