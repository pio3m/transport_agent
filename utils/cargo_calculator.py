from typing import List, Dict, Tuple
from math import floor

VEHICLES = {
    "bus": {
        "length_cm": 450,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 4.5,
        "max_weight": 1500
    },
    "solówka": {
        "length_cm": 730,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 7.3,
        "max_weight": 9000
    },
    "naczepa": {
        "length_cm": 1360,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 13.6,
        "max_weight": 24000
    }
}


class CargoCalculator:
    def __init__(self, vehicle_type: str = "naczepa"):
        self.vehicle_type = vehicle_type if vehicle_type in VEHICLES else "naczepa"
        self.vehicle = VEHICLES[self.vehicle_type]

    def calculate(self, cargo_items: List[Dict]) -> Dict:
        total_ldm = 0.0
        total_weight = 0
        warnings = []
        fit_in_vehicle = True

        for item in cargo_items:
            l = item["length"] * 100  # m -> cm
            w = item["width"] * 100
            h = item["height"] * 100
            qty = item["quantity"]
            weight_per_piece = item.get("weight", 0)  # kg

            # Walidacja wysokości
            if h > self.vehicle["height_cm"]:
                warnings.append(f"Ładunek o wysokości {h} cm przekracza wysokość pojazdu ({self.vehicle['height_cm']} cm).")
                fit_in_vehicle = False

            # Sprawdzenie obu ułożeń (obrót): [l, w] oraz [w, l]
            orientations = [(l, w), (w, l)]
            best_ldm = None

            for orient_l, orient_w in orientations:
                pieces_per_row = floor(self.vehicle["width_cm"] / orient_w)
                if pieces_per_row == 0:
                    continue  # nie mieści się żaden w rzędzie

                full_rows = qty // pieces_per_row
                leftover = qty % pieces_per_row

                ldm_cm = (full_rows * orient_l) + (orient_l if leftover else 0)
                ldm_m = ldm_cm / 100

                if best_ldm is None or ldm_m < best_ldm:
                    best_ldm = ldm_m

            if best_ldm is None:
                warnings.append("Ładunek jest zbyt szeroki, by zmieścić się w pojeździe.")
                fit_in_vehicle = False
                continue

            total_ldm += round(best_ldm, 2)
            total_weight += weight_per_piece * qty

        # Walidacja LDM
        if total_ldm > self.vehicle["max_ldm"]:
            warnings.append(f"Łączna długość LDM ({total_ldm}) przekracza maksymalną dla {self.vehicle_type} ({self.vehicle['max_ldm']}).")
            fit_in_vehicle = False

        # Walidacja wagi
        if total_weight > self.vehicle["max_weight"]:
            warnings.append(f"Łączna waga ładunku ({total_weight} kg) przekracza maksymalną dla {self.vehicle_type} ({self.vehicle['max_weight']} kg).")
            fit_in_vehicle = False

        # Ostrzeżenie o nieoptymalnym LDM
        if 0 < total_ldm < (0.8 * self.vehicle["max_ldm"]):
            warnings.append("Zajmujesz mniej niż 80% przestrzeni pojazdu – rozważ wybór opcji 'dowolny typ pojazdu'.")

        return {
            "ldm": round(total_ldm, 2),
            "fit_in_vehicle": fit_in_vehicle,
            "warnings": warnings,
            "total_weight": total_weight,
            "vehicle_used": self.vehicle_type,
            "vehicle_suggestion": self.vehicle_type if fit_in_vehicle else "naczepa"
        }

    @staticmethod
    def suggest_optimal_vehicle(cargo_items: List[Dict]) -> Dict:
        candidates = []
        for vehicle_type in ["bus", "solówka", "naczepa"]:
            calc = CargoCalculator(vehicle_type)
            result = calc.calculate(cargo_items)
            if result["fit_in_vehicle"]:
                candidates.append((vehicle_type, result["ldm"]))

        if not candidates:
            return {"vehicle": "brak", "reason": "Żaden pojazd nie mieści ładunku"}

        # wybierz najmniejszy pojazd, który mieści ładunek
        best = min(candidates, key=lambda x: x[1])
        return {"vehicle": best[0]}