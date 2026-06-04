import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';
import { RoomConfiguration } from '@livekit/protocol';

type ConnectionDetails = {
  serverUrl: string;
  roomName: string;
  participantName: string;
  participantToken: string;
};

type LiveKitConfig = {
  livekitUrl: string;
  apiKey: string;
  apiSecret: string;
};

type ConnectionDetailsErrorCode =
  | 'missing_livekit_env'
  | 'invalid_request'
  | 'token_generation_failed';

class ConnectionDetailsError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly code: ConnectionDetailsErrorCode,
    readonly missing?: string[]
  ) {
    super(message);
  }
}

// don't cache the results
export const revalidate = 0;

export async function POST(req: Request) {
  try {
    const { livekitUrl, apiKey, apiSecret } = liveKitConfigFromEnv();

    // Parse agent configuration from request body
    const body = await req.json().catch(() => ({}));
    const agentName = parseAgentName(body);

    // Generate participant token
    const participantName = 'user';
    const participantIdentity = `voice_assistant_user_${randomId()}`;
    const roomName = `voice_assistant_room_${randomId()}`;

    const participantToken = await createParticipantToken(
      apiKey,
      apiSecret,
      { identity: participantIdentity, name: participantName },
      roomName,
      agentName
    );

    // Return connection details
    const data: ConnectionDetails = {
      serverUrl: livekitUrl,
      roomName,
      participantToken: participantToken,
      participantName,
    };
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    return NextResponse.json(data, { headers });
  } catch (error) {
    const sanitized = sanitizeConnectionError(error);
    console.error('Connection details request failed', sanitized.log);
    return NextResponse.json(sanitized.body, { status: sanitized.status });
  }
}

function requiredEnv(name: string): string {
  return process.env[name]?.trim() ?? '';
}

function liveKitConfigFromEnv(): LiveKitConfig {
  const livekitUrl = requiredEnv('LIVEKIT_URL');
  const apiKey = requiredEnv('LIVEKIT_API_KEY');
  const apiSecret = requiredEnv('LIVEKIT_API_SECRET');
  const missing = [
    ['LIVEKIT_URL', livekitUrl],
    ['LIVEKIT_API_KEY', apiKey],
    ['LIVEKIT_API_SECRET', apiSecret],
  ]
    .filter(([, value]) => !value)
    .map(([name]) => name);

  if (missing.length) {
    throw new ConnectionDetailsError(
      'LiveKit server configuration is incomplete.',
      500,
      'missing_livekit_env',
      missing
    );
  }

  return { livekitUrl, apiKey, apiSecret };
}

function parseAgentName(body: unknown): string | undefined {
  if (!body || typeof body !== 'object') return undefined;
  const roomConfig = (body as { room_config?: unknown }).room_config;
  if (!roomConfig || typeof roomConfig !== 'object') return undefined;
  const agents = (roomConfig as { agents?: unknown }).agents;
  if (!Array.isArray(agents)) return undefined;
  const firstAgent = agents[0];
  if (!firstAgent || typeof firstAgent !== 'object') return undefined;
  const agentName = (firstAgent as { agent_name?: unknown }).agent_name;
  if (typeof agentName !== 'string') {
    throw new ConnectionDetailsError(
      'Agent name must be a string when provided.',
      400,
      'invalid_request'
    );
  }
  const trimmed = agentName.trim();
  return trimmed || undefined;
}

async function createParticipantToken(
  apiKey: string,
  apiSecret: string,
  userInfo: AccessTokenOptions,
  roomName: string,
  agentName?: string
): Promise<string> {
  const at = new AccessToken(apiKey, apiSecret, {
    ...userInfo,
    ttl: '15m',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  if (agentName) {
    at.roomConfig = new RoomConfiguration({
      agents: [{ agentName }],
    });
  }

  try {
    return await at.toJwt();
  } catch {
    throw new ConnectionDetailsError(
      'Unable to create a LiveKit participant token.',
      502,
      'token_generation_failed'
    );
  }
}

function randomId(): string {
  return crypto.randomUUID().replaceAll('-', '').slice(0, 12);
}

function sanitizeConnectionError(error: unknown) {
  if (error instanceof ConnectionDetailsError) {
    return {
      status: error.status,
      body: {
        error: error.message,
        code: error.code,
        ...(error.missing ? { missing: error.missing } : {}),
      },
      log: {
        name: error.constructor.name,
        code: error.code,
        status: error.status,
        missing: error.missing,
      },
    };
  }

  return {
    status: 500,
    body: {
      error: 'Connection details unavailable.',
      code: 'token_generation_failed' satisfies ConnectionDetailsErrorCode,
    },
    log: {
      name: error instanceof Error ? error.constructor.name : typeof error,
      code: 'token_generation_failed' satisfies ConnectionDetailsErrorCode,
      status: 500,
    },
  };
}
