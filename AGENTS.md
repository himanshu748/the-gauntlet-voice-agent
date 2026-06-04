# Repository Guidelines

## Project Shape
- `backend/` contains the LiveKit Agents Python voice worker for The Partner persona and Gauntlet game state.
- `frontend/` contains the Next.js LiveKit session UI.
- `challenges/` keeps Murf challenge notes and should not drive runtime behavior.

## Local Commands
- Backend: `cd backend && uv run pytest -q`.
- Backend lint: `cd backend && uv run ruff check src tests`.
- Frontend: `cd frontend && pnpm install && pnpm build`.
- Full local run needs LiveKit credentials plus Murf, Gemini, and Deepgram keys configured in local env files.

## Safety Notes
- Keep provider and LiveKit secrets server-side in ignored `.env.local` files.
- Do not commit `.venv`, `node_modules`, `.next`, local logs, screenshots, or challenge scratch output.
- Prefer deterministic tests for game flow; avoid tests that require live LLM/provider calls unless explicitly marked.
