# Self-critique / anti-AI-slop review notes

## What is strong

- The work is grounded in real Night2 artifacts: repos, tests, SHAs, live QA, failing handoffs, Claw critique.
- The two content drafts have operator details rather than generic “AI agents are the future” claims.
- The eval framework enforces objective scoring dimensions and preserves failure signals.
- The launch recommendation chooses the artifact with the cleanest verification chain, not the most grandiose story.

## What still smells like AI slop

- “Agent teams need evals, not vibes” is a strong line, but it risks becoming generic if not paired with a concrete table/screenshot.
- The md2deck artifact is intentionally small; if presented as a major product, it will feel inflated. Present it as a lab artifact / build-off demo / eval vehicle.
- The scorecard is lightweight and partially manual. Do not imply it is a mature benchmark suite yet.
- Night1 example is reconstructed from reports and should stay labeled partial.
- Claw-side token/API stats remain unavailable; do not invent them.

## Required honesty lines

Use these if posting or briefing:

- “This is an operator pattern from two overnight runs, not a universal benchmark yet.”
- “Night 1 is partially reconstructed; Night 2 has stronger push/live QA evidence.”
- “The scorecard validates artifact paths/git state but does not execute arbitrary recorded commands.”
- “Content drafts are approval-gated; nothing was posted automatically.”

## Better titles

- Agent teams need evals, not vibes.
- Green CI is not shipped.
- Make agents show the URL.
- Did the disagreement survive into code?
- All-green agent runs are suspicious.

## Kill list

Avoid:

- “revolutionary”
- “autonomous workforce”
- “10x productivity” without evidence
- “fully shipped” for internal CLI lanes without deploy/package QA
- “benchmark” unless we define fixture set and scoring stability

## Best morning approval item

Approve the md2deck launch packet after one quick human voice pass, because it has the strongest proof chain and lowest private-risk surface.
