# Product

Hackathon project for the Blazity "AI for Content" challenge (2026-06-30):
an AI tool that turns a content brief into an on-brand post (with a generated
video) and publishes it to a Facebook Page in one click.

## The problem

Creating social content that stays consistent with an account's existing voice
and format is manual, slow work: rewriting, matching tone, producing matching
visuals, then copy-pasting to publish. AI does the rewriting and visual
generation; an API removes the last copy-paste step.

## Core flow

1. User provides a brief plus a few existing posts (and optionally reference
   images) so the AI can learn their style.
2. Claude generates a post matched to that voice/length/format + brand-voice check.
3. "Generate video" → Claude builds a prompt → fal.ai renders (async, polled) → clip URL.
4. One-click publish to a Facebook Page via a server-side proxy.

## Scope decisions

- Publish target: **Facebook Page only** for the demo. Instagram/LinkedIn out of scope.
- Video: **fal.ai** (generative). Creatomate considered and dropped.
- Style learning: user **pastes their own example posts**; the app does NOT read
  post history from any platform API (needs partner permissions).
- No DB, no auth, no scheduling (see design spec).

## Judging criteria (from the brief)

- Quality of thinking over volume shipped.
- One thing done well, demoable and explainable, beats a sprawling build.
- Show the AI was aimed at the right problem and its output was checked.

## Reference

Full design: `.ai/research/2026-06-30-content-tool-design.md`.

## Unknowns (resolve during build)

- Brand-voice check: pass/fail gate vs. advisory (lean advisory)
- Target user: solo creator vs. brand/marketing team
- fal.ai model + default duration/aspect ratio
