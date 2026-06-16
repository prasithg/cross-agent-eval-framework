from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .scoring import load_json, score_scorecard


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and strictly score cross-agent work-session scorecards.")
    parser.add_argument("scorecards", nargs="+", help="Scorecard JSON files to evaluate")
    parser.add_argument("--strict", action="store_true", default=False, help="Enforce evidence consistency rules")
    parser.add_argument("--no-legacy-v02", action="store_true", help="Reject legacy schema_version 0.2 files")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON only")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = []
    exit_code = 0
    for raw_path in args.scorecards:
        path = Path(raw_path)
        data = load_json(path)
        result = score_scorecard(data, strict=args.strict, allow_v02=not args.no_legacy_v02)
        payload = {
            "file": str(path),
            "valid": result.valid,
            "errors": result.errors,
            "computed_scores": result.computed_scores,
            "claimed_scores": result.claimed_scores,
            "summary": result.summary,
        }
        results.append(payload)
        if not result.valid:
            exit_code = 1
    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, sort_keys=True))
    else:
        for payload in results:
            status = "PASS" if payload["valid"] else "FAIL"
            print(f"{status} {payload['file']}")
            print(f"  computed: {payload['computed_scores']['total_points']}/100")
            if payload["claimed_scores"]:
                print(f"  claimed:  {payload['claimed_scores'].get('total_points')}/100")
            for error in payload["errors"]:
                print(f"  error: {error}")
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
