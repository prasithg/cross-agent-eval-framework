# Launch positioning: md2deck-hermes-lab

Status: approval-gated launch packet. Repo/demo already public; no social posting happened.

## Strongest artifact of Night 2

`md2deck-hermes-lab` is the cleanest launch candidate because it has the full chain:

- runnable CLI: `node md2deck.mjs input.md output.html`
- tests: `npm test`
- build command: `npm run build:sample`
- pushed public repo: `https://github.com/prasithg/md2deck-hermes-lab`
- live demo: `https://prasithg.github.io/md2deck-hermes-lab/sample-deck.html`
- live QA: HTTP 200, 4616 bytes, 5 slide nodes, no external HTTP dependencies

## Positioning

A tiny dependency-free Markdown-to-offline-slide-deck converter, built as a cross-agent work-session artifact.

The point is not that Markdown-to-slides is novel.

The point is the operating pattern:

same build-off prompt,
independent agent implementation,
runnable output,
tests,
commit/push,
live QA,
and a scorecard that punishes vibes.

## README opening replacement candidate

```md
# md2deck-hermes-lab

A tiny dependency-free Markdown-to-offline-HTML deck converter built during a HermesPras × PrasClaw overnight build-off.

It turns a Markdown file into a self-contained slide deck:

```bash
node md2deck.mjs sample.md sample-deck.html
```

Why this exists:

- to make a small useful tool;
- to test whether agent teams can ship runnable artifacts instead of just producing plans;
- to pair code output with objective eval signals: tests, commit SHA, live demo QA, and cross-agent review.

Live demo: https://prasithg.github.io/md2deck-hermes-lab/sample-deck.html
```

## Launch post skeleton

I ran an overnight two-agent build-off and forced the output through a shipping scorecard.

The small artifact: a dependency-free Markdown → offline HTML slide deck converter.

The more interesting artifact: the eval harness around it.

For a session to count as “shipped,” I wanted:

- runnable command
- tests
- commit + pushed SHA
- live/demo QA
- external critique from another agent
- at least one real failure caught along the way

The converter is intentionally tiny. That’s the point.

Small surface area makes it easier to see the operating pattern:

agents should not just produce plausible work;
they should produce artifacts another process can verify.

Repo: https://github.com/prasithg/md2deck-hermes-lab
Demo: https://prasithg.github.io/md2deck-hermes-lab/sample-deck.html

## Next polish before posting

1. Add screenshot/GIF to README.
2. Add a short “How this was evaluated” table with command/output snippets.
3. Ask PrasClaw for anti-slop review: does this sound like a real operator story or AI toy-launch fluff?
4. Optional: add `npx`/package install path later; not needed for the first story.
