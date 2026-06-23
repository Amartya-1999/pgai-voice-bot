import json
from pathlib import Path


SCENARIO_FILE = Path("data/scenarios.json")


def load_scenarios() -> list[dict]:
    with open(SCENARIO_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def get_scenario_by_id(scenario_id: str) -> dict:
    scenarios = load_scenarios()

    for scenario in scenarios:
        if scenario["id"] == scenario_id:
            return scenario

    raise ValueError(f"Scenario not found: {scenario_id}")