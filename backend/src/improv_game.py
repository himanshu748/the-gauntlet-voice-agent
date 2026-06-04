import random
from dataclasses import dataclass, field
from typing import Optional

DEFAULT_SCENARIOS = [
    "Pitch a startup that sells bottled air to fish.",
    "Explain why your 'Uber for Dog Walking' needs blockchain.",
    "Pitch a dating app for ghosts.",
    "Sell me a subscription service for socks that don't match.",
    "Pitch a VR headset for cats.",
    "Explain your AI that generates random excuses for being late.",
    "Pitch a social network for plants.",
    "Sell me a smart water bottle that judges your hydration habits.",
]


@dataclass
class ImprovState:
    player_name: Optional[str] = None
    current_round: int = 0
    max_rounds: int = 3
    rounds: list[dict[str, str]] = field(default_factory=list)
    phase: str = "intro"  # "intro", "pitching", "validating", "done"


class ImprovGame:
    def __init__(self) -> None:
        self.state = ImprovState()
        self.scenarios = list(DEFAULT_SCENARIOS)
        self.used_scenarios: set[str] = set()
        self.current_scenario: Optional[str] = None

    def start_game(self, player_name: str) -> None:
        normalized_name = player_name.strip() or "Founder"
        self.state.player_name = normalized_name
        self.state.current_round = 0
        self.state.rounds = []
        self.state.phase = "intro"
        self.used_scenarios = set()
        self.current_scenario = None

    def get_next_scenario(self) -> Optional[str]:
        if self.state.current_round >= self.state.max_rounds:
            self.state.phase = "done"
            return None

        self.state.current_round += 1
        self.state.phase = "pitching"
        self.current_scenario = self._choose_unused_scenario()
        self.used_scenarios.add(self.current_scenario)
        return self.current_scenario

    def end_round(self, host_reaction: str) -> None:
        if self.current_scenario is None:
            raise RuntimeError("Cannot validate a pitch before a scenario is assigned.")

        self.state.rounds.append(
            {
                "scenario": self.current_scenario,
                "host_reaction": host_reaction.strip(),
            }
        )
        self.state.phase = "validating"

    def get_game_summary(self) -> str:
        return f"Alright {self.state.player_name}, we've reviewed your deck. You survived {self.state.max_rounds} rounds of due diligence. We'll be in touch... maybe."

    def _choose_unused_scenario(self) -> str:
        unused_scenarios = [
            scenario
            for scenario in self.scenarios
            if scenario not in self.used_scenarios
        ]
        return random.choice(unused_scenarios or self.scenarios)
