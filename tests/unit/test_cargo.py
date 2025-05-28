import unittest
from utils.cargo_calculator import CargoCalculator, get_max_ldm, VehicleType

class TestCargoCalculator(unittest.TestCase):

    def test_get_max_ldm(self):
        self.assertEqual(get_max_ldm(VehicleType.BUS), 4.5)
        self.assertEqual(get_max_ldm(VehicleType.SOLO), 7.3)
        self.assertEqual(get_max_ldm(VehicleType.NACZEPA), 13.6)
        self.assertEqual(get_max_ldm("nieznany"), 13.6)  # default fallback

    def test_no_cargo_returns_max_ldm(self):
        calc = CargoCalculator(VehicleType.BUS)
        result = calc.calculateLDM([])
        self.assertEqual(result["max_ldm"], 4.5)
        self.assertIn("Brak danych o ładunku", result["warnings"][0])

    def test_fit_simple_cargo_bus(self):
        cargo = [{"length": 0.8, "width": 1.0, "height": 2.0, "quantity": 3, "weight": 200}]
        calc = CargoCalculator(VehicleType.BUS)
        result = calc.calculateLDM(cargo)
        self.assertTrue(result["fit_in_vehicle"])
        self.assertAlmostEqual(result["ldm"], 1.0)

    def test_exceeds_height(self):
        cargo = [{"length": 0.8, "width": 1.0, "height": 3.0, "quantity": 1, "weight": 100}]
        calc = CargoCalculator(VehicleType.SOLO)
        result = calc.calculateLDM(cargo)
        self.assertFalse(result["fit_in_vehicle"])
        self.assertIn("przekracza wysokość pojazdu", result["warnings"][0])

    def test_exceeds_ldm(self):
        cargo = [{"length": 3.0, "width": 1.2, "height": 2.0, "quantity": 3, "weight": 200}]
        calc = CargoCalculator(VehicleType.BUS)
        result = calc.calculateLDM(cargo)
        self.assertFalse(result["fit_in_vehicle"])
        self.assertIn("przekracza maksymalną", " ".join(result["warnings"]))


    def test_exceeds_weight(self):
        cargo = [{"length": 1.0, "width": 1.0, "height": 2.0, "quantity": 1, "weight": 16000}]
        calc = CargoCalculator(VehicleType.SOLO)
        result = calc.calculateLDM(cargo)
        self.assertFalse(result["fit_in_vehicle"])
        self.assertIn("przekracza maksymalną dla VehicleType.SOLO", " ".join(result["warnings"]))

    def test_ldm_optimization_warning(self):
        cargo = [{"length": 0.8, "width": 1.0, "height": 2.0, "quantity": 1, "weight": 200}]
        calc = CargoCalculator(VehicleType.NACZEPA)
        result = calc.calculateLDM(cargo)
        self.assertIn("Zajmujesz mniej niż 80% przestrzeni pojazdu", " ".join(result["warnings"]))

    def test_vehicle_suggestion(self):
        cargo = [{"length": 0.8, "width": 1.0, "height": 2.0, "quantity": 4, "weight": 200}]
        result = CargoCalculator.suggest_optimal_vehicle(cargo)
        self.assertEqual(result["vehicle"], VehicleType.BUS.value)

    def test_no_vehicle_fits(self):
        cargo = [{"length": 5.0, "width": 3.0, "height": 3.0, "quantity": 1, "weight": 50000}]
        result = CargoCalculator.suggest_optimal_vehicle(cargo)
        self.assertEqual(result["vehicle"], "brak")

if __name__ == '__main__':
    unittest.main()
