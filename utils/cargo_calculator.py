from typing import List, Dict
from math import floor
from enum import Enum

class VehicleType(Enum):
    BUS = "bus"
    SOLO = "solówka"
    NACZEPA = "naczepa"

VEHICLES = {
    VehicleType.BUS: {
        "length_cm": 450,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 4.4,
        "max_weight": 1500
    },
    VehicleType.SOLO: {
        "length_cm": 730,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 7.7,
        "max_weight": 9000
    },
    VehicleType.NACZEPA: {
        "length_cm": 1360,
        "width_cm": 240,
        "height_cm": 260,
        "max_ldm": 13.6,
        "max_weight": 24000
    }
}

def get_max_ldm(vehicle_type: str | VehicleType) -> float:
    if isinstance(vehicle_type, str):
        try:
            vehicle_type = VehicleType(vehicle_type)
        except ValueError:
            vehicle_type = VehicleType.NACZEPA
    if vehicle_type not in VEHICLES:
        return VEHICLES[VehicleType.NACZEPA]["max_ldm"]
    return VEHICLES[vehicle_type]["max_ldm"]


class CargoCalculator:
    def __init__(self, vehicle_type: str | VehicleType = VehicleType.NACZEPA):
        if isinstance(vehicle_type, str):
            try:
                vehicle_type = VehicleType(vehicle_type)
            except ValueError:
                vehicle_type = VehicleType.NACZEPA
        self.vehicle_type = vehicle_type if vehicle_type in VEHICLES else VehicleType.NACZEPA
        self.vehicle = VEHICLES[self.vehicle_type]

    def check_ldm(self, ldm):
        #spr czy dla danego typu nie przekracza ldm
        return ldm > self.vehicle["max_ldm"]
         



    def get_max_ldm(self) -> float:
        return self.vehicle["max_ldm"]
    
    def calculateLDM(self, cargo_items: List[Dict]) -> Dict:
       

        total_ldm = 0.0
        total_weight = 0
        warnings = []
        fit_in_vehicle = True

        for item in cargo_items:
            l = item["length"] * 100
            w = item["width"] * 100
            h = item["height"] * 100
            qty = item["quantity"]
            weight_per_piece = item.get("weight", 0)

            if h > self.vehicle["height_cm"]:
                warnings.append(f"Ładunek o wysokości {h} cm przekracza wysokość pojazdu ({self.vehicle['height_cm']} cm).")
                fit_in_vehicle = False

            orientations = [(l, w), (w, l)]
            best_ldm = None

            for orient_l, orient_w in orientations:
                pieces_per_row = floor(self.vehicle["width_cm"] / orient_w)
                if pieces_per_row == 0:
                    continue

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

            total_ldm += best_ldm
            total_weight += weight_per_piece * qty

        if total_ldm > self.vehicle["max_ldm"]:
            warnings.append(f"Łączna długość LDM ({round(total_ldm, 2)}) przekracza maksymalną dla {self.vehicle_type} ({self.vehicle['max_ldm']}).")
            fit_in_vehicle = False

        if total_weight > self.vehicle["max_weight"]:
            warnings.append(f"Łączna waga ładunku ({total_weight} kg) przekracza maksymalną dla {self.vehicle_type} ({self.vehicle['max_weight']} kg).")
            fit_in_vehicle = False

        if 0 < total_ldm < (0.8 * self.vehicle["max_ldm"]):
            warnings.append("Zajmujesz mniej niż 80% przestrzeni pojazdu – rozważ wybór opcji 'dowolny typ pojazdu'.")

        total_ldm = round(total_ldm, 2)

        return {
            "ldm": total_ldm,
            "fit_in_vehicle": fit_in_vehicle,
            "warnings": warnings,
            "total_weight": total_weight,
            "vehicle_used": self.vehicle_type.value,
            "vehicle_suggestion": self.vehicle_type.value if fit_in_vehicle else VehicleType.NACZEPA.value
        }

    @staticmethod
    def suggest_optimal_vehicle(cargo_items: List[Dict]) -> Dict:
        candidates = []
        for vehicle_type in [VehicleType.BUS, VehicleType.SOLO, VehicleType.NACZEPA]:
            calc = CargoCalculator(vehicle_type)
            result = calc.calculateLDM(cargo_items)
            if result["fit_in_vehicle"]:
                candidates.append((vehicle_type, result["ldm"]))

        if not candidates:
            return {"vehicle": "brak", "reason": "Żaden pojazd nie mieści ładunku"}

        best = min(candidates, key=lambda x: x[1])
        return {"vehicle": best[0].value}
