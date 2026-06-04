import { Button } from '@/components/livekit/button';

function WelcomeImage() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-fg0 mb-4 size-16"
    >
      <path
        d="M32 2C15.432 2 2 15.432 2 32C2 48.568 15.432 62 32 62C48.568 62 62 48.568 62 32C62 15.432 48.568 2 32 2ZM32 58C17.664 58 6 46.336 6 32C6 17.664 17.664 6 32 6C46.336 6 58 17.664 58 32C58 46.336 46.336 58 32 58Z"
        fill="currentColor"
      />
      <path
        d="M32 12C21.005 12 12 21.005 12 32C12 42.995 21.005 52 32 52C42.995 52 52 42.995 52 32C52 21.005 42.995 12 32 12ZM32 48C23.178 48 16 40.822 16 32C16 23.178 23.178 16 32 16C40.822 16 48 23.178 48 32C48 40.822 40.822 48 32 48Z"
        fill="currentColor"
      />
      <path
        d="M32 22C26.486 22 22 26.486 22 32C22 37.514 26.486 42 32 42C37.514 42 42 37.514 42 32C42 26.486 37.514 22 32 22ZM32 38C28.692 38 26 35.308 26 32C26 28.692 28.692 26 32 26C35.308 26 38 28.692 38 32C38 35.308 35.308 38 32 38Z"
        fill="currentColor"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center">
        <WelcomeImage />

        <h2 className="text-foreground text-2xl font-bold tracking-tight">The Gauntlet</h2>
        <p className="text-muted-foreground max-w-prose pt-2 leading-6 font-medium">
          Pitch your startup idea. Survive the validation.
        </p>

        <Button
          variant="primary"
          size="lg"
          onClick={onStartCall}
          className="mt-6 w-64 font-mono tracking-wider uppercase"
        >
          {startButtonText}
        </Button>
      </section>

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-pretty md:text-sm">
          Powered by LiveKit, Deepgram, Google Gemini, and Murf AI.
        </p>
      </div>
    </div>
  );
};
