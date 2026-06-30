# Design: AI Content Tool (brief → on-brand post + video → FB publish)

Date: 2026-06-30
Status: Approved (brainstorming)

## Problem

Creating social content that stays consistent with an account's existing voice
and format is slow manual work: rewriting, matching tone, producing matching
visuals, then copy-pasting to publish. AI can do the rewriting and visual
generation; an API removes the last copy-paste step.

Blazity "AI for Content" hackathon. Judged on quality of thinking, not volume:
one thing done well, demoable and explainable.

## Core flow

1. User provides a brief plus a few of their existing posts (and optionally
   reference images) so the AI can learn their style.
2. Claude generates a post matched to that voice/length/format and runs a
   brand-voice consistency check.
3. "Generate video" button — Claude builds a video prompt; fal.ai renders the
   clip (async); the app polls until a clip URL is ready.
4. One-click publish to a Facebook Page via a server-side proxy.

## Architecture

```
[Vite + React + TS]  --fetch-->  [FastAPI proxy]  -->  Claude (anthropic SDK)
   browser                        holds keys in    -->  fal.ai (fal-client)
   no keys                        .env              -->  FB Graph API (httpx)
```

- **Frontend:** Vite + React + TypeScript SPA. No secrets in the client.
- **Backend:** FastAPI (Python). Holds all API keys, calls Claude / fal.ai / FB.
- The Anthropic, fal, and FB keys never reach the browser.

## Backend endpoints

- `POST /api/generate` — input: brief, example posts, optional image refs.
  Output: generated post text + brand-voice check result (Claude).
- `POST /api/video` — input: approved post/brief. Claude builds a fal.ai video
  prompt; submit to fal.ai; return `job_id`.
- `GET /api/video/{job_id}` — poll fal.ai status; return clip URL when ready.
- `POST /api/publish` — input: clip URL + post text. Calls FB Graph
  `POST /{page-id}/videos` (file_url = fal URL, description = post text). Returns
  the published post link.

## Data flow

1. Form → `/api/generate` → post + brand-voice check rendered in UI.
2. "Generate video" → `/api/video` → `job_id`; frontend polls
   `/api/video/{job_id}` until a clip URL returns.
3. "Publish" → `/api/publish` with URL + text → FB → link to the published post.

## Secrets (.env, server-side only)

`ANTHROPIC_API_KEY`, `FAL_KEY`, `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`.
Never bundled into the Vite client. `.env` is git-ignored; ship `.env.example`.

## Error handling

- fal.ai render failure/timeout → user-facing message + retry option.
- FB publish failure → surface the Graph API error message.
- Missing/invalid key → backend returns 500 with a clear message.
- fal poll: cap attempts/time; show progress while pending.

## Out of scope (YAGNI)

- No database — state lives in frontend session.
- No auth / multi-user — demo uses one Page.
- No reading FB post history — brand voice comes from pasted examples
  (LinkedIn/FB post-history read needs partner permissions not available to a
  hackathon app).
- No publish scheduling.
- Single platform: Facebook Page only. Instagram out of scope for the demo
  (heavier setup: account conversion + Page link + two-step publish).

## Key constraints / decisions

- Use the latest, most capable Claude models for generation.
- fal.ai chosen over Creatomate: real generative video. Accept the tradeoff that
  generative output is slower and less predictable; mitigate with clear loading
  states and retry.
- FB Page chosen over Instagram: simpler setup, single-request video publish
  (`file_url`), no account-type conversion.

## Open questions (resolve during build)

- Brand-voice check: hard pass/fail gate vs. advisory suggestions? (lean advisory)
- Target user: solo creator vs. brand/marketing team?
- Which fal.ai video model + default duration/aspect ratio?
