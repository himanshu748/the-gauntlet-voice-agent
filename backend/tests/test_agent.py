import logging

from src import agent


def test_missing_provider_env_lists_required_keys(monkeypatch) -> None:
    for name in agent.REQUIRED_PROVIDER_ENV:
        monkeypatch.delenv(name, raising=False)

    assert agent.missing_provider_env() == [
        "DEEPGRAM_API_KEY",
        "GOOGLE_API_KEY",
        "MURF_API_KEY",
    ]


def test_missing_provider_env_ignores_present_keys(monkeypatch) -> None:
    monkeypatch.setenv("DEEPGRAM_API_KEY", "present")
    monkeypatch.setenv("GOOGLE_API_KEY", "present")
    monkeypatch.delenv("MURF_API_KEY", raising=False)

    assert agent.missing_provider_env() == ["MURF_API_KEY"]


def test_missing_runtime_env_includes_livekit_and_provider_keys(monkeypatch) -> None:
    for name in agent.REQUIRED_RUNTIME_ENV:
        monkeypatch.delenv(name, raising=False)

    monkeypatch.setenv("LIVEKIT_URL", "present")
    monkeypatch.setenv("LIVEKIT_API_KEY", "present")
    monkeypatch.setenv("LIVEKIT_API_SECRET", "present")

    assert agent.missing_runtime_env() == [
        "DEEPGRAM_API_KEY",
        "GOOGLE_API_KEY",
        "MURF_API_KEY",
    ]


def test_provider_prewarm_failure_summary_omits_raw_exception_detail() -> None:
    exc = RuntimeError("provider failed with sk-live-secret and /private/local/path")

    summary = agent.provider_prewarm_failure_summary(exc)

    assert summary == "RuntimeError; provider details omitted"
    assert "sk-live-secret" not in summary
    assert "/private/local/path" not in summary


def test_prewarm_fails_before_provider_init_when_env_missing(monkeypatch, caplog) -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.userdata = {}

    for name in agent.REQUIRED_RUNTIME_ENV:
        monkeypatch.delenv(name, raising=False)

    with caplog.at_level(logging.ERROR, logger="startup-validator"):
        try:
            agent.prewarm(FakeProcess())
        except agent.MissingRuntimeEnvError as exc:
            assert exc.missing == list(agent.REQUIRED_RUNTIME_ENV)
        else:
            raise AssertionError("Expected missing runtime env to fail prewarm")

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "Missing runtime environment variables" in messages
    assert "LIVEKIT_API_SECRET" in messages


def test_prewarm_logs_sanitized_provider_exception(monkeypatch, caplog) -> None:
    class FakeProcess:
        def __init__(self) -> None:
            self.userdata = {}

    def fail_load():
        raise RuntimeError(
            "provider failed with sk-live-secret and /private/local/path"
        )

    for name in agent.REQUIRED_RUNTIME_ENV:
        monkeypatch.setenv(name, "present")
    monkeypatch.setattr(agent.silero.VAD, "load", fail_load)

    with caplog.at_level(logging.ERROR, logger="startup-validator"):
        try:
            agent.prewarm(FakeProcess())
        except RuntimeError:
            pass
        else:
            raise AssertionError("Expected prewarm to raise the provider failure")

    messages = "\n".join(record.getMessage() for record in caplog.records)
    assert "RuntimeError; provider details omitted" in messages
    assert "sk-live-secret" not in messages
    assert "/private/local/path" not in messages
