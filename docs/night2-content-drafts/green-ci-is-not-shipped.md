# Approval-gated draft: green CI is not shipped

Status: draft only — do not post without Pras approval.  
Source: Night 1 Claw production-pain framing + Night 2 deploy/live QA sweep.  
Angle: CI is necessary but incomplete; agents should verify the runtime surface, not just the build log.

## Draft

Green CI is not shipped.

This sounds obvious until you watch agents — and humans — treat a green check as the finish line.

A build can pass while the product is still broken.

Wrong env var.
Missing runtime secret.
Bad relative path.
Static asset not deployed.
Health check hitting the wrong URL.
Demo page built locally but never reachable.
Package works in tests but fails in the actual CLI path.

In last night’s agent run, one of the most useful moments was not a new feature.

It was catching a boring deploy gap:

the repo was clean,
the tests passed,
but the sample build script had a bad relative path.

The fix was tiny.

The lesson is not.

For agent-built software, I want a separate “shipped” gate:

1. tests pass
2. artifact builds
3. commit exists
4. remote SHA matches
5. deploy/demo/package surface is checked
6. live QA output is recorded

Only then do we say shipped.

CI tells you the code satisfied the machine you configured.

Live QA tells you whether the thing a human will touch actually exists.

Agents are very good at producing green-looking logs.

So the eval needs to ask the rude question:

where is the URL, package, CLI command, or file I can actually use?

## Shorter variant

Green CI is not shipped.

For agent-built software, I’m adding a separate shipped gate:

- tests pass
- artifact builds
- commit exists
- remote SHA matches
- live/demo/package surface is checked
- QA output is recorded

A green check proves your configured test path passed.

It does not prove a human can use the thing.

Agents love green-looking logs. Make them produce a usable surface.

## Anti-slop notes

- This is strongest when paired with md2deck: tests + pushed repo + GitHub Pages + curl QA.
- Avoid making it sound like CI is bad. CI is table stakes; it is not the whole shipping proof.
- Do not include private/work anecdotes. Keep examples generic or from public-safe Night2 artifacts.
