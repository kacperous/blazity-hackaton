# Project AI Instructions

## What this repo is

`blazity-hackaton` — a hackathon project for the Blazity "AI for Content"
challenge: a web app that uses AI to solve a content-management pain. Today it is
a scaffold (README, LICENSE, and the Atlas AI workspace under `.ai/`); no
application code yet. Stack is chosen — Vite + React (TypeScript) with Claude
(Anthropic) for AI. The concrete content problem is not yet decided. See
`.ai/memory/` for stable context.

## Structure

- `.ai/` — Atlas AI workspace. `.ai/config.json` is the source of truth for
  artifact locations (memory, vocabulary, plans, research, decisions, results).
- `AGENTS.md` / `CLAUDE.md` — agent instructions; `CLAUDE.md` imports this file.
- `.agents/`, `.claude/`, `.cursor/` — generated agent surfaces.

## Working rules

- Stack is Vite + React + TypeScript with the Anthropic SDK (Claude). The app
  is not scaffolded yet — confirm exact run/test/build commands once
  `package.json` exists; expected: `npm run dev` / `npm run build`.
- Never expose the Anthropic API key to the browser. Claude calls go through a
  server/proxy layer, not the Vite client.
- Beyond Atlas tooling (`npx --yes @blazity-atlas/core@latest doctor`), no
  project-specific safe commands are defined yet.
- The content problem is undecided — do not invent product scope; confirm first.
- Do not edit the `<!-- BEGIN/END ATLAS -->` managed block below by hand.
- Keep durable docs depersonalized (see Atlas Documentation Rules below).

<!-- BEGIN ATLAS: artifact-paths -->
## Atlas Artifact Paths

`.ai/config.json` is the source of truth for AI artifact locations in this repository.
Before writing plans, research, decisions, ADRs, results, memory, vocabulary, or skill outputs, resolve the destination through `artifactRoot`, `paths`, and `pathAliases`.
If an imported skill, template, or instruction mentions a different path, map it through `.ai/config.json` before reading or writing files.
Do not create new documentation roots unless `.ai/config.json` explicitly allows them.

## Atlas Documentation Rules

Durable documentation records needs, decisions, and reasons — never individuals or internal process.
Write "memory was needed to persist context across runs", not "<name> wanted memory".
Keep personal names, private schedules, internal-only references, and absolute local paths out of workspace artifacts.
<!-- END ATLAS: artifact-paths -->
