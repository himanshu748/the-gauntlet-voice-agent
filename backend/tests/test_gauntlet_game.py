from src.improv_game import ImprovGame


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


def test_cannot_validate_before_pitch() -> None:
    game = ImprovGame()

    try:
        game.end_round("Looks investable.")
    except RuntimeError as exc:
        assert str(exc) == "Cannot validate a pitch before a scenario is assigned."
    else:
        raise AssertionError("Expected validation before a scenario to fail")
