# Cross-Agent Eval Framework

A repo-ready, testable version of the Night2 `eval-framework-v0.2` packet. The goal is to stop flattering all-green summaries from passing as progress.

This scorer awards credit only when the scorecard includes evidence for:

- runnable commands;
- tests with assertions;
- committed and remotely verified git state;
- deploy/live/package QA;
- handoff lint signal;
- external review delta;
- failure signal / negative control.

## What changed from Night2 v0.2

Night2 was a useful rubric, but too easy to satisfy with narrative claims. This v0.3 repo makes the artifact stricter:

1. **Schema is explicit** about evidence objects, statuses, URLs, artifact paths, and verification fields.
2. **Scoring is computed, not trusted** from `objective_scores.total_points`.
3. **Remote/shipped evidence is stricter**: commit points require a repo, a HEAD SHA, a remote URL, and `remote_sha_verified: true`; shipped lanes are invalid without the same.
4. **Live/package QA needs concrete evidence**, not `not_applicable` hand-waving when a lane claims shipped/deployed.
5. **Negative fixtures are part of the test suite** so fake all-green progress cannot silently pass.

## Quick start

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m pytest -q
cross-agent-score examples/night2-partial-scorecard.json --strict
```

No production secrets are required. The scorer does not execute recorded session commands; those commands are evidence records only.

## CLI

```bash
cross-agent-score SCORECARD.json [SCORECARD2.json ...] --strict --json
```

For CI/cron jobs with network access, add live remote proof:

```bash
cross-agent-score SCORECARD.json --strict --verify-remote
```

`--verify-remote` runs `git ls-remote <remote_url> HEAD` for each lane that claims
`remote_sha_verified: true` and fails if the recorded `head_sha` is stale or not
the remote HEAD. Offline mode still validates the schema and evidence consistency
without touching the network.

Exit codes:

- `0`: every scorecard is valid under selected rules;
- `1`: one or more scorecards failed validation;
- `2`: CLI usage error.

## Repo layout

- `src/cross_agent_eval/` — scoring/validation library and CLI.
- `schemas/session_scorecard.schema.json` — v0.3 schema.
- `examples/` — Night2 imported examples.
- `fixtures/positive/` — passing minimal scorecards.
- `fixtures/negative/` — deliberately invalid/fake-progress cases.
- `tests/` — schema/scoring/regression tests.
- `reports/` — Night3 validation checkpoint.

## Guardrail

This project is safe for open-source packaging: it contains no secrets and only references local artifact paths from prior agent-work sessions. Content drafts stay approval-gated; do not post as Pras from this repo.
