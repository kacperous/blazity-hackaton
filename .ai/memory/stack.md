# Stack

Web app: React frontend + FastAPI proxy backend. Application code not yet
scaffolded.

## Chosen

- **Frontend:** Vite + React + TypeScript (SPA). No secrets in the client.
- **Backend:** FastAPI (Python) — proxy holding all API keys.
- **AI text:** Claude (Anthropic) via the Python `anthropic` SDK. Use the
  latest, most capable Claude models.
- **AI video:** fal.ai via `fal-client` (Python). Async render; poll for clip URL.
- **Publish:** Facebook Graph API via `httpx`.
- **Version control:** Git.

## Hard rules

- API keys (`ANTHROPIC_API_KEY`, `FAL_KEY`, `FB_PAGE_ID`,
  `FB_PAGE_ACCESS_TOKEN`) live only in backend `.env`, never in the Vite client.
- `.env` is git-ignored; commit a `.env.example` with empty placeholders.

## Tooling notes

- Atlas (`@blazity-atlas/core`) manages the AI workspace; health check:
  `npx --yes @blazity-atlas/core@latest doctor`.

## Expected commands (confirm once scaffolded)

- Frontend: `npm install`, `npm run dev`, `npm run build`
- Backend: `uvicorn app.main:app --reload` (or via a runner); deps in
  `requirements.txt` / `pyproject.toml`

## Unknowns (fill once scaffolded)

- Frontend libs (router, state, styling)
- Test frameworks (Vitest frontend, pytest backend are natural fits)
- fal.ai model id + render params
