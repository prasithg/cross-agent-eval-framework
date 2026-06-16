# Cross-Agent Work-Session Eval Rubric v0.2

Purpose: score agent-team work by objective delivery signals, not vibes. This implements Claw's locked Lane D critique: every score must tie to a runnable command, test assertion, commit/push/deploy check, handoff lint signal, or explicit external-review delta.

## Scoring (100 pts)

| Dimension | Points | Full credit requires |
|---|---:|---|
| Runnable commands | 20 | Commands are recorded with paths and outputs; at least one core command can be rerun by another agent. |
| Tests with assertions | 20 | Tests are not only smoke text; assertion/subtest counts or equivalent checks are visible. |
| Commit/push evidence | 20 | Repo path, HEAD SHA, remote URL, and remote SHA verification are recorded when code changed. Dropbox-only artifacts get partial credit only if no code repo exists. |
| Deploy/live QA | 15 | For web/demo artifacts: HTTP 2xx or live artifact check. For CLIs/internal tools: dry-run or package-level QA is acceptable and labeled. |
| Handoff lint signal | 10 | Handoffs are linted against real/non-curated handoffs; failing signals are preserved rather than hidden. |
| External-review delta | 10 | Another agent's critique changed a concrete artifact, test, command, schema, or launch framing. |
| Failure signal present | 5 | At least one failing lane/check, known-bad fixture, or blocker is surfaced. All-green sessions without a designed negative control cap at `useful`. |

## Verdict bands

- `strong`: 85–100, with at least one failure/negative-control signal and no unacknowledged gated-action breach.
- `useful`: 70–84, or 85+ without a failure signal.
- `mixed`: 45–69, meaningful work but weak validation or unclear shipping state.
- `weak`: 1–44, mostly docs/plans without runnable evidence.
- `invalid`: 0 or guardrail breach / fabricated evidence.

## Anti-vibe rules

1. No subjective quality fields in the score. Quality commentary can exist in notes, but it cannot award points.
2. Green CI is not shipped unless a relevant deploy/live/package QA signal exists.
3. A repo link without a remote SHA check is only a pointer, not push evidence.
4. A handoff that only says “please review” without owner, path, sensitivity boundary, and next action is coordination debt.
5. A session with no failed check is suspicious; add a known-bad fixture or historical negative example.
6. Content drafts are approval-gated; writing a draft is valid output, posting it is not.

## Minimum scorecard fields

Use `session_scorecard.schema.json`. The script in `scripts/score_session.py` performs lightweight schema checks plus path/git evidence counting without external dependencies.
