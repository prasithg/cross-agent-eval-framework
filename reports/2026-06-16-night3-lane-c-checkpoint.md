# Night3 Lane C Checkpoint — Cross-Agent Eval Framework v0.3

**Verdict:** converted the Night2 flattering local packet into a real, repo-ready test artifact.

## What changed

- Created repo-safe package at `/Users/prasithgovin/Development/open-source/cross-agent-eval-framework`.
- Imported Night2 source packet from `/Users/prasithgovin/Dropbox/Agent-Exchange/30_PROJECTS/monster-work-session-night2/eval-framework-v0.2`.
- Added installable Python package + CLI: `cross-agent-score`.
- Added stricter v0.3 schema and scorer. It computes points from evidence instead of trusting claimed totals.
- Added negative fixtures so fake all-green progress fails:
  - `fixtures/negative/fake_all_green_no_negative.json`
  - `fixtures/negative/shipped_without_remote.json`
  - `fixtures/negative/claimed_score_exceeds_evidence.json`
- Added tests for schema shape, computed scoring caps, CLI behavior, legacy Night2 scoring, and negative-control failures.

## Key result

Night2 claimed **99/100**. Under the stricter scorer, the same imported scorecard computes **87/100** and fails strict validation because the claimed total exceeds evidence-backed scoring.

That is the intended behavior. This is no longer a hype packet; it can now reject inflated summaries.

## Exact validation commands run

```bash
/Users/prasithgovin/.hermes/hermes-agent/venv/bin/python3.11 -m venv .venv311
. .venv311/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e . pytest
python -m pytest -q
cross-agent-score fixtures/positive/minimal_shipped_cli.json --strict --json
cross-agent-score fixtures/negative/fake_all_green_no_negative.json --strict --json
cross-agent-score fixtures/negative/shipped_without_remote.json --strict --json
cross-agent-score examples/night2-partial-scorecard.json --strict --json
```

## Exact outputs summary

Full output saved at:

`reports/2026-06-16-night3-lane-c-validation-output.txt`

Important lines:

```text
.........                                                                [100%]
positive fixture: valid=true, computed total=40/100
fake all-green negative fixture: valid=false, computed total=9/100
shipped-without-remote negative fixture: valid=false
Night2 v0.2 imported scorecard: valid=false, claimed=99/100, computed=87/100
```

## Why this matters for Pras

This turns the eval lane into a pressure tool. A future monster-night report cannot just say “green, shipped, strong.” It has to show:

- commands actually ran;
- tests had assertions;
- git work was committed and remote-verified;
- live/package QA happened or has a real non-web reason;
- at least one negative/failure signal exists for a strong verdict;
- claimed totals do not exceed computed evidence.

## Next compounding move

Wire this into the morning dashboard generator so every monster-session lane gets scored automatically before the HTML report is written. If the report claims more than the scorer computes, mark that lane yellow/red instead of flattering it.
