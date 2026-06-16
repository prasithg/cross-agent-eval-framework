# Approval-gated draft: agent teams need evals, not vibes

Status: draft only — do not post without Pras approval.  
Source: HermesPras × PrasClaw Night 1/2 monster sessions.  
Angle: make cross-agent collaboration measurable through artifacts, tests, commits, live QA, and failure signals.

## Draft

Agent teams need evals, not vibes.

The failure mode I keep seeing is not “the agents didn’t talk to each other.”

It’s worse:

they talk,
produce a wall of markdown,
congratulate each other,
and nobody can tell whether anything actually got better.

So I’m starting to score agent work sessions like build systems:

- What commands ran?
- What tests asserted something real?
- What changed because another agent disagreed?
- Is there a commit SHA?
- Is the remote actually updated?
- Is there a live/demo/package QA signal?
- Did we preserve at least one failing check, or is this fake all-green?

The last one matters more than people think.

If your multi-agent workflow never produces a red light, it probably isn’t evaluating anything. It’s just narrating progress.

A good second agent is not a cheerleader. It should kill assumptions.

In our overnight run, the useful deltas were boring and concrete:

- “your scheduler schema is wrong”
- “agent-doorbell is less valuable than handoff-lint”
- “green CI is not shipped”
- “run this against real historical handoffs, not the fixture you wrote for yourself”

That turned into tests, CLIs, live QA, a deployed demo, and a scorecard.

That’s the bar I want for agent teams:

not did they collaborate,
not did they write a strategy doc,
not did the transcript feel impressive.

Did the disagreement survive into an artifact you can run?

## Tighter variant

Multi-agent work needs a scoreboard.

Not sentiment. Not “great collaboration.” Not a 40-page transcript.

Score the boring things:

- runnable commands
- tests with assertions
- commit + remote SHA
- deploy/live QA
- linted handoffs
- external-review delta
- at least one failing/negative-control signal

If every check is green, I’m suspicious.

A useful agent teammate should break something before it helps you ship something.

## Anti-slop notes

- Keep the concrete examples. They are the only reason this avoids generic AI punditry.
- Do not say “AI agents are changing everything.” Too broad.
- Do not overclaim this as a universal framework yet; position as an operator pattern from real overnight runs.
- Best accompanying artifact: screenshot/table from `eval-framework-v0.2/examples/night2-partial-scorecard.json` plus md2deck live demo.
