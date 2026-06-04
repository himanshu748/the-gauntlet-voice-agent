const SECRET_PATTERNS = [
  /\bsk-[A-Za-z0-9_-]{8,}\b/g,
  /\bgh[pousr]_[A-Za-z0-9_]{8,}\b/g,
  /\bAIza[A-Za-z0-9_-]{8,}\b/g,
  /\bhf_[A-Za-z0-9]{8,}\b/g,
  /\b[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b/g,
];

const LOCAL_PATH_PATTERNS = [/\/(?:Users|private|var|tmp)\/[^\s)"']+/g, /[A-Za-z]:\\[^\s)"']+/g];

export function redactSensitiveText(value: string): string {
  return [...SECRET_PATTERNS, ...LOCAL_PATH_PATTERNS].reduce(
    (message, pattern) => message.replace(pattern, '[redacted]'),
    value
  );
}

export function safeErrorDescription(error: unknown, fallback: string): string {
  if (error instanceof Error && error.message.trim()) {
    return redactSensitiveText(`${error.name}: ${error.message.trim()}`);
  }
  return fallback;
}

export function safeLogDetails(error: unknown) {
  return {
    name: error instanceof Error ? error.name : typeof error,
  };
}

export type ConnectionDetailsErrorBody = {
  error?: unknown;
  code?: unknown;
  missing?: unknown;
};

export function connectionDetailsMessage(body: ConnectionDetailsErrorBody | null): string {
  if (body?.code === 'missing_livekit_env') {
    return 'LiveKit connection is not configured on the server.';
  }
  if (body?.code === 'invalid_request') {
    return typeof body.error === 'string'
      ? redactSensitiveText(body.error)
      : 'Connection request is invalid.';
  }
  return 'Unable to create a LiveKit session. Please try again.';
}
