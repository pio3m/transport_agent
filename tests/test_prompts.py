import os
import json
import pytest
from deepdiff import DeepDiff
from agents.llm_agent import LLMAgent

test_input = "Potrzebuję transportu z Warszawy do Sierpca. Towar: 10 palet, waga 500kg, wymiary 120x80x150cm. Termin: jutro. dowóz następnego dnia"

@pytest.mark.parametrize("prompt_file", [
    "prompts/p_v1.txt",
    # "prompts/p_v2.txt"
])
def test_prompt_snapshot(prompt_file):
    agent = LLMAgent(provider="openai")
    result = agent.parse_transport_request(
        prompt=test_input,
        system_prompt_path=prompt_file
    )

    # Zapisz wynik do pliku JSON
    version_name = os.path.splitext(os.path.basename(prompt_file))[0]
    snapshot_path = f"snapshots/{version_name}.json"

    if not os.path.exists("snapshots"):
        os.makedirs("snapshots")

    if not os.path.exists(snapshot_path):
        # Pierwsze uruchomienie – utwórz snapshot
        with open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        pytest.skip(f"Snapshot created for {version_name}")
    else:
        # Porównaj z istniejącym snapshotem
        with open(snapshot_path, "r", encoding="utf-8") as f:
            snapshot = json.load(f)

        diff = DeepDiff(snapshot, result, significant_digits=4)

        if diff:
            print(f"\n❗️Różnice dla {version_name}:\n{diff}")
        assert not diff, f"Zmiana odpowiedzi względem snapshotu dla {version_name}"
