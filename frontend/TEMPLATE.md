## The Gauntlet Frontend Template Notes

This frontend started from LiveKit's React agent starter, but the runtime surface is now customized for **The Gauntlet**.

Use this app with the backend `startup-validator` agent and keep deployment configuration in ignored `.env.local` files.

For sandbox or hosted deployments:

1. Configure `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, and `LIVEKIT_URL`.
2. Set `NEXT_PUBLIC_SITE_URL` to the hosted origin for Open Graph metadata.
3. Keep `app-config.ts` pointed at the `startup-validator` agent unless the backend agent name changes.
