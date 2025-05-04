import pytest
from fastapi.testclient import TestClient
from main import app  # lub inny punkt wejścia

client = TestClient(app)

# @pytest.mark.parametrize("prompt,expected_ldm,expected_warning_part", [
#     (
#         "Mam ładunek na solówkę odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne",
#         7.3,
#         None  # brak ostrzeżenia, bo idealnie pasuje
#     ),
#     (
#         "Mam ładunek na solówkę 2 x 2 x 9 metrów odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne",
#         None,
#         "przekracza maksymalną dla solówka"
#     ),
#     (
#         "Mam ładunek na solówkę 2 x 2 x 7metrów o wadze 15 ton odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne",
#         None,
#         "waga ładunku.*przekracza maksymalną"
#     ),
#     (
#         "Mam ładunek na solówkę 2 x 2 x 4 metry odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne",
#         4.0,
#         "Zajmujesz mniej niż 80% przestrzeni pojazdu"
#     )
# ])
# def test_prompt_ldm_warnings(prompt, expected_ldm, expected_warning_part):
#     response = client.post("/api/v1/parse", json={"prompt": prompt})
#     assert response.status_code == 200
#     data = response.json()["parsed_data"]
#     analysis = data.get("cargo_analysis", {})

#     if expected_ldm is not None:
#         assert round(analysis["ldm"], 1) == expected_ldm

#     if expected_warning_part:
#         warnings = " ".join(analysis.get("warnings", []))
#         assert expected_warning_part.lower() in warnings.lower()


@pytest.mark.parametrize("prompt,expected_ldm", [
    (
        "chcę przewieźć 3 palety 100x80 cm o wysokości 2 metry odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne",
        1.0
    ),
    (
        "chcę przewieźć 4 palety 100x80 cm o wysokości 2 metry odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne ",
        1.6
    ),
])
def test_ldm_values_only(prompt, expected_ldm):
    response = client.post("/api/v1/parse", json={"prompt": prompt})
    assert response.status_code == 200
    data = response.json()["parsed_data"]
    analysis = data.get("cargo_analysis", {})

    assert round(analysis["ldm"], 1) == expected_ldm