# The Gauntlet Backend

LiveKit Agents backend for **The Gauntlet**, a voice-first startup pitch validator. The agent persona is **The Partner**, a skeptical VC who assigns absurd startup ideas, critiques each pitch, and closes with a term-sheet-style decision.

## Runtime Stack

- LiveKit Agents Python worker
- Deepgram Nova 3 speech-to-text
- Google Gemini 2.5 Flash reasoning
- Murf Falcon text-to-speech
- Silero VAD and LiveKit multilingual turn detection

## Setup

```bash
uv sync
cp .env.example .env.local
```

Fill in `backend/.env.local` or `backend/.env`. If both exist, `.env.local`
overrides `.env`.

```text
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
GOOGLE_API_KEY=
MURF_API_KEY=
DEEPGRAM_API_KEY=
```

Download local model assets before the first run:

```bash
uv run python -m src.agent download-files
```

## Run

```bash
uv run python -m src.agent dev
```

For a terminal-only smoke run:

```bash
uv run python -m src.agent console
```

## Verify

```bash
uv run pytest -q
uv run ruff check src tests
```

The test suite is deterministic and validates the local Gauntlet game state. It should not require live provider credentials.

## Key Files

- `src/agent.py` - The Partner persona, LiveKit session setup, and tool definitions
- `src/improv_game.py` - round state, scenario selection, pitch validation, and summary logic
- `tests/test_gauntlet_game.py` - deterministic game-flow coverage
