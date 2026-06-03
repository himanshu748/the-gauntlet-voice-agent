# The Gauntlet: Startup Validator Voice Agent

The Gauntlet is a voice-first startup pitch game where you step into a mock investor room and try to survive a brutally honest VC.

You pitch absurd startup ideas, the agent challenges your assumptions, and after three rounds it decides whether you are getting a term sheet or getting roasted out of the room.

## What It Does

- Runs a live voice conversation with a startup-validator persona called **The Partner**
- Gives the user three absurd startup ideas to pitch
- Tracks pitch rounds and reactions with backend game state
- Uses tool calls to start the session, generate pitch prompts, validate each round, and issue a final term-sheet-style summary
- Uses real-time speech input/output so the experience feels like a live pitch meeting

## Demo Flow

1. Join the voice session.
2. The Partner welcomes you to The Gauntlet.
3. Give your founder name.
4. Pitch the assigned startup idea.
5. Survive three rounds of VC-style critique.
6. Receive the final investment decision.

Example scenarios include:

- Bottled air for fish
- A dating app for ghosts
- A VR headset for cats
- A social network for plants

## Tech Stack

**Backend**

- LiveKit Agents for real-time voice sessions
- Deepgram Nova 3 for speech-to-text
- Google Gemini 2.5 Flash for the reasoning layer
- Murf Falcon TTS for voice output
- Silero VAD and LiveKit turn detection

**Frontend**

- Next.js
- React
- LiveKit Components
- Tailwind CSS

## Repository Structure

```text
the-gauntlet-voice-agent/
|-- backend/          # LiveKit voice agent backend
|   `-- src/
|       |-- agent.py        # The Partner voice agent
|       `-- improv_game.py  # Gauntlet round/game state
|-- frontend/         # Voice session UI
|-- challenges/       # Murf challenge task notes
|-- start_app.sh      # Starts local services
`-- README.md
```

## Local Setup

### Prerequisites

- Python 3.9+
- `uv`
- Node.js 18+
- `pnpm`
- LiveKit CLI or a local LiveKit server

### Backend

```bash
cd backend
uv sync
cp .env.example .env.local
```

Add the required credentials to `backend/.env.local`:

```text
LIVEKIT_URL=
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
MURF_API_KEY=
GOOGLE_API_KEY=
DEEPGRAM_API_KEY=
```

Download the required voice/turn-detection assets:

```bash
uv run python src/agent.py download-files
```

### Frontend

```bash
cd frontend
pnpm install
cp .env.example .env.local
```

Add the matching LiveKit credentials to `frontend/.env.local`.

## Run Locally

From the repo root:

```bash
chmod +x start_app.sh
./start_app.sh
```

This starts:

- Local LiveKit server
- Backend voice agent
- Frontend app at `http://localhost:3000`

You can also run services separately:

```bash
# Terminal 1
livekit-server --dev

# Terminal 2
cd backend
uv run python src/agent.py dev

# Terminal 3
cd frontend
pnpm dev
```

## Key Files

- `backend/src/agent.py` - Defines The Partner persona and LiveKit agent session
- `backend/src/improv_game.py` - Stores pitch rounds, startup prompts, and final session state
- `frontend/app-config.ts` - Frontend branding for The Gauntlet
- `frontend/components/app/welcome-view.tsx` - Start screen for the voice experience

## Status

The core voice-agent concept is implemented:

- Custom VC persona
- Startup pitch game loop
- Murf/Deepgram/Gemini/LiveKit voice pipeline
- Branded frontend entry screen

The project can be improved further with:

- A hosted demo link
- A short walkthrough video
- Stronger visual branding beyond the starter UI
- More pitch scenarios and scoring logic

## Credits

Built for the Murf AI Voice Agents Challenge.

This project started from the Murf AI / LiveKit voice-agent starter repository and was customized into The Gauntlet, a startup validator voice-agent game.

## License

MIT License. See `LICENSE` for details.
