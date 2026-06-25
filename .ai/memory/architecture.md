# Architecture

No application architecture exists yet. The repository contains only project
metadata (README, LICENSE) and the Atlas AI workspace under `.ai/`.

## Current layout

- `.ai/` — Atlas AI workspace (config, memory, vocabulary, plans, research,
  decisions, results, skills). `.ai/config.json` is the source of truth for
  artifact locations.
- `AGENTS.md` / `CLAUDE.md` — agent instructions. `CLAUDE.md` imports `AGENTS.md`.
- `.agents/`, `.claude/`, `.cursor/` — generated agent surfaces.

## Unknowns (fill once code lands)

- Runtime and deployment model
- Service/module boundaries
- Architectural invariants and constraints
