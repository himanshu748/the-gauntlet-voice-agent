import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    AutoSubscribe,
    JobContext,
    JobProcess,
    RoomInputOptions,
    WorkerOptions,
    cli,
    function_tool,
)
from livekit.plugins import deepgram, google, murf, noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from .improv_game import ImprovGame

ENV_DIR = Path(__file__).parent.parent
load_dotenv(dotenv_path=ENV_DIR / ".env")
load_dotenv(dotenv_path=ENV_DIR / ".env.local", override=True)

logger = logging.getLogger("startup-validator")

REQUIRED_LIVEKIT_ENV = ("LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET")
REQUIRED_PROVIDER_ENV = ("DEEPGRAM_API_KEY", "GOOGLE_API_KEY", "MURF_API_KEY")
REQUIRED_RUNTIME_ENV = (*REQUIRED_LIVEKIT_ENV, *REQUIRED_PROVIDER_ENV)


class MissingRuntimeEnvError(RuntimeError):
    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "Missing required runtime environment variables: " + ", ".join(missing)
        )


def missing_env_vars(names: tuple[str, ...] = REQUIRED_RUNTIME_ENV) -> list[str]:
    return [name for name in names if not os.getenv(name, "").strip()]


def missing_provider_env() -> list[str]:
    return missing_env_vars(REQUIRED_PROVIDER_ENV)


def missing_runtime_env() -> list[str]:
    return missing_env_vars(REQUIRED_RUNTIME_ENV)


def provider_prewarm_failure_summary(exc: BaseException) -> str:
    return f"{type(exc).__name__}; provider details omitted"


class StartupValidatorAgent(Agent):
    def __init__(self) -> None:
        self.game = ImprovGame()
        super().__init__(
            instructions=self._get_instructions(),
        )

    def _get_instructions(self) -> str:
        return """
        You are 'The Partner', a brutally honest, high-stakes Venture Capitalist and Startup Validator. You run 'The Gauntlet', a pitch validation session.

        **PERSONA:**
        - You are sharp, fast-talking, and business-focused.
        - You use VC jargon (burn rate, TAM, CAC, LTV, pivot, unicorn, decacorn).
        - You are skeptical but willing to be convinced.
        - You roast bad ideas mercilessly but praise true innovation (even if it's absurd).
        - Your voice should sound professional, authoritative, and slightly impatient.

        **GAME FLOW:**
        1.  **Intro:** When the user joins, welcome them to 'The Gauntlet'. Ask for their name and their "pre-seed valuation" (just for fun).
        2.  **Pitch Rounds (Validation):**
            - Use the `next_pitch` tool to get a startup idea.
            - Announce the idea they must pitch.
            - Tell them to "Sell me this!" or "Pitch it before I lose interest!".
            - Listen to their pitch.
            - When they finish, react to it.
            - Use `validate_pitch` to record your reaction.
        3.  **Validation Analysis (Reactions):**
            - Critique the business model, the market size, or the sheer absurdity.
            - Decide if you're "In" or "Out" for that round.
            - Example: "The TAM on bottled air is zero, but I like your hustle. I'm out." or "A dating app for ghosts? That's a blue ocean strategy! I'm listening."
        4.  **Term Sheet (End Game):**
            - After 3 rounds, summarize their performance.
            - Decide if you will fund them or pass.
            - Thank them and close the session.

        **TOOLS:**
        - `start_session(founder_name)`: Call this when the user provides their name.
        - `next_pitch()`: Call this to start a new pitch round.
        - `validate_pitch(reaction)`: Call this after you have reacted to the user's pitch.
        - `issue_term_sheet()`: Call this to end the game and summarize.

        **IMPORTANT:**
        - If the user says "stop" or "quit", confirm and end the call.
        - Keep it professional but entertaining.
        """

    @function_tool
    async def start_session(self, founder_name: str):
        """
        Start the validation session with the founder's name.
        """
        self.game.start_game(founder_name)
        return f"File opened for Founder {founder_name}. Let's see what you've got. Ready for the first pitch?"

    @function_tool
    async def next_pitch(self):
        """
        Get the next startup idea to pitch. Returns None if the session is over.
        """
        scenario = self.game.get_next_scenario()
        if scenario:
            return f"Here is your startup idea: {scenario}"
        else:
            return "Due diligence is complete. Let's look at the numbers."

    @function_tool
    async def validate_pitch(self, reaction: str):
        """
        Record the VC's reaction to the pitch.
        """
        self.game.end_round(reaction)
        return "Pitch validated. Moving to next item."

    @function_tool
    async def issue_term_sheet(self):
        """
        Ends the session and summarizes the results.
        """
        summary = self.game.get_game_summary()
        return f"Session closed. Here is our decision: {summary}. Don't call us, we'll call you."


def prewarm(proc: JobProcess):
    try:
        logger.info("Starting prewarm...")
        missing = missing_runtime_env()
        if missing:
            logger.error(
                "Missing runtime environment variables: %s", ", ".join(missing)
            )
            raise MissingRuntimeEnvError(missing)

        proc.userdata["vad"] = silero.VAD.load()
        # Deepgram Nova 3
        proc.userdata["stt"] = deepgram.STT(model="nova-3")
        # Google Gemini 2.5 Flash
        proc.userdata["llm"] = google.LLM(model="gemini-2.5-flash")
        # Murf Falcon
        proc.userdata["tts"] = murf.TTS(
            model="FALCON",
            voice="Matthew",  # Or another suitable professional voice
            style="Promo",
        )

        logger.info("Prewarm completed")
    except Exception as e:
        logger.error("Prewarm failed: %s", provider_prewarm_failure_summary(e))
        raise


async def entrypoint(ctx: JobContext):
    logger.info("Entrypoint started")
    ctx.log_context_fields = {"room": ctx.room.name}

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")

    agent = StartupValidatorAgent()

    session = AgentSession(
        stt=ctx.proc.userdata.get("stt") or deepgram.STT(model="nova-3"),
        llm=ctx.proc.userdata.get("llm") or google.LLM(model="gemini-2.5-flash"),
        tts=ctx.proc.userdata.get("tts")
        or murf.TTS(
            model="FALCON",
            voice="Matthew",
            style="Promo",
        ),
        turn_detection=ctx.proc.userdata.get("turn_detection") or MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        preemptive_generation=True,
    )

    await session.start(
        agent=agent,
        room=ctx.room,
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.say(
        "Welcome to The Gauntlet. I'm The Partner. State your name and let's see if you're unicorn material.",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            agent_name="startup-validator",
        ),
    )
