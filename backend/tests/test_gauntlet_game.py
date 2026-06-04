from src.improv_game import (
    DEFAULT_HOST_REACTION,
    MAX_PLAYER_NAME_CHARS,
    MAX_REACTION_CHARS,
    ImprovGame,
)


def test_game_starts_with_clean_founder_state() -> None:
    game = ImprovGame()

    game.start_game("  Himanshu  ")

    assert game.state.player_name == "Himanshu"
    assert game.state.current_round == 0
    assert game.state.rounds == []
    assert game.state.phase == "intro"


def test_game_runs_exactly_three_pitch_rounds(monkeypatch) -> None:
    game = ImprovGame()
    game.start_game("Founder")
    monkeypatch.setattr("src.improv_game.random.choice", lambda scenarios: scenarios[0])

    scenarios = [game.get_next_scenario() for _ in range(3)]
    fourth = game.get_next_scenario()

    assert scenarios == game.scenarios[:3]
    assert fourth is None
    assert game.state.current_round == 3
    assert game.state.phase == "done"


def test_round_reaction_is_recorded_with_scenario(monkeypatch) -> None:
    game = ImprovGame()
    game.start_game("Founder")
    monkeypatch.setattr(
        "src.improv_game.random.choice", lambda scenarios: scenarios[-1]
    )

    scenario = game.get_next_scenario()
    game.end_round("Tiny TAM, excellent theater. I'm out.")

    assert game.state.phase == "validating"
    assert game.state.rounds == [
        {
            "scenario": scenario,
            "host_reaction": "Tiny TAM, excellent theater. I'm out.",
        }
    ]


def test_summary_names_founder_and_round_count() -> None:
    game = ImprovGame()
    game.start_game("Himanshu")

    summary = game.get_game_summary()

    assert "Himanshu" in summary
    assert "3 rounds" in summary


def test_blank_founder_name_falls_back_to_founder() -> None:
    game = ImprovGame()

    game.start_game("  ")

    assert game.state.player_name == "Founder"


def test_founder_name_is_normalized_and_bounded() -> None:
    game = ImprovGame()
    name = f"  {'A' * (MAX_PLAYER_NAME_CHARS + 20)} \n Founder  "

    game.start_game(name)

    assert game.state.player_name == "A" * MAX_PLAYER_NAME_CHARS
    assert len(game.state.player_name) == MAX_PLAYER_NAME_CHARS


def test_blank_round_reaction_uses_safe_default(monkeypatch) -> None:
    game = ImprovGame()
    game.start_game("Founder")
    monkeypatch.setattr("src.improv_game.random.choice", lambda scenarios: scenarios[0])

    game.get_next_scenario()
    game.end_round(" \n\t ")

    assert game.state.rounds[0]["host_reaction"] == DEFAULT_HOST_REACTION


def test_round_reaction_is_normalized_and_bounded(monkeypatch) -> None:
    game = ImprovGame()
    game.start_game("Founder")
    monkeypatch.setattr("src.improv_game.random.choice", lambda scenarios: scenarios[0])
    reaction = f"  {'Solid ' * 200}\ntraction  "

    game.get_next_scenario()
    game.end_round(reaction)

    recorded_reaction = game.state.rounds[0]["host_reaction"]
    assert "\n" not in recorded_reaction
    assert len(recorded_reaction) == MAX_REACTION_CHARS


def test_cannot_validate_before_pitch() -> None:
    game = ImprovGame()

    try:
        game.end_round("Looks investable.")
    except RuntimeError as exc:
        assert str(exc) == "Cannot validate a pitch before a scenario is assigned."
    else:
        raise AssertionError("Expected validation before a scenario to fail")
