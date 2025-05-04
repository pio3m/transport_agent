import pytest
from fastapi.testclient import TestClient
from main import app 

client = TestClient(app)


@pytest.mark.parametrize("prompt,min_km,max_km", [
    (
        "chcę przewieźć 4 palety 100x80 cm o wysokości 2 metry odbiór Warszawa Aleje Jerozolimskie 200 dostawa Sierpc Browar odbiór za 3 dni dowóz następnego dnia.",
        124,
        145  
    ),
    (
        "chcę przewieźć 4 palety 100x80 cm o wysokości 2 metry odbiór 22-405 Zamość dostawa 86-302 Grudziądz odbiór za 3 dni dowóz następnego dnia.",
        500,
        580  # oczekiwano 500–570 km
    ),
    (
        "chcę przewieźć 3 palety 100x80 cm o wysokości 2 metry odbiór 42-445 Szczekociny dostawa 34-442 Łapsze Niżne odbiór dziś dowóz następnego dnia.",
        180,
        230
    )
])
def test_distance_km_estimation(prompt, min_km, max_km):
    response = client.post("/api/v1/parse", json={"prompt": prompt})
    assert response.status_code == 200

    parsed_data = response.json().get("parsed_data", {})
    distance = parsed_data.get("distance_km", None)

    assert distance is not None, "Brak distance_km w odpowiedzi"
    assert isinstance(distance, (float, int)), f"distance_km ma nieprawidłowy typ: {type(distance)}"
    assert min_km <= distance <= max_km, f"Oczekiwano {min_km}–{max_km} km, otrzymano {distance:.1f} km"
