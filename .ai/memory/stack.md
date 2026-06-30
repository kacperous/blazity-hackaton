# Stack

Frontend-first web app. Stack chosen; application code not yet scaffolded.

## Chosen

- **Language:** TypeScript
- **Frontend:** React via Vite (SPA, lightweight dev server + build)
- **AI provider:** Claude (Anthropic) — Anthropic SDK (`@anthropic-ai/sdk`).
  Default to the latest, most capable Claude models for product AI features.
- **Version control:** Git.

## Tooling notes

- Atlas (`@blazity-atlas/core`) manages the AI workspace; check health with
  `npx --yes @blazity-atlas/core@latest doctor`.
- The Anthropic API key must never be exposed to the browser. Calls to Claude
  must go through a server/proxy layer, not directly from the Vite client.

## Expected commands (confirm once `package.json` exists)

- Install: `npm install`
- Dev server: `npm run dev` (Vite default)
- Build: `npm run build`
- Preview build: `npm run preview`

## Unknowns (fill once scaffolded)

- Backend/proxy layer for Claude calls (serverless function, small Node server, etc.)
- Test framework (Vitest is the natural fit for Vite)
- Key libraries (router, state, styling)
