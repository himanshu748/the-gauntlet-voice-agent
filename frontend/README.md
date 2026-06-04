# The Gauntlet Frontend

Next.js LiveKit session UI for **The Gauntlet**, a voice game where founders pitch absurd startups to a skeptical VC agent.

## What This UI Does

- Creates a LiveKit participant token through `app/api/connection-details/route.ts`
- Starts a voice session with the `startup-validator` backend agent
- Shows the branded welcome screen, transcript, audio controls, and chat input
- Keeps LiveKit credentials on the server side only

## Setup

```bash
pnpm install
cp .env.example .env.local
```

Fill in `frontend/.env.local`:

```text
LIVEKIT_API_KEY=
LIVEKIT_API_SECRET=
LIVEKIT_URL=
NEXT_PUBLIC_SITE_URL=http://localhost:3000
```

Use the same LiveKit project or local server configured for the backend.

## Run

```bash
pnpm dev
```

Open `http://localhost:3000`.

## Verify

```bash
pnpm build
pnpm format:check
```

## Key Files

- `app-config.ts` - Gauntlet branding, feature toggles, and LiveKit agent name
- `components/app/welcome-view.tsx` - first screen and start button
- `app/api/connection-details/route.ts` - server-side token minting
- `components/app/session-view.tsx` - transcript, controls, and active call layout
