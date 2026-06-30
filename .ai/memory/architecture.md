# Architecture

No application code yet. The repository holds project metadata (README,
LICENSE) and the Atlas AI workspace under `.ai/`. The intended shape is below.

## Intended shape

- Vite + React (TypeScript) single-page app for the UI.
- A server/proxy layer for Anthropic API calls — the API key must stay
  server-side, never bundled into the browser client.

## Current layout

- `.ai/` — Atlas AI workspace (config, memory, vocabulary, plans, research,
  decisions, results, skills). `.ai/config.json` is the source of truth for
  artifact locations.
- `AGENTS.md` / `CLAUDE.md` — agent instructions. `CLAUDE.md` imports `AGENTS.md`.
- `.agents/`, `.claude/`, `.cursor/` — generated agent surfaces.

## Unknowns (fill once code lands)

- Proxy/backend choice (serverless function vs. small Node server)
- Service/module boundaries
- Deployment target
