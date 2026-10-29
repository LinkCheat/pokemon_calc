import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from moves import ElectroBall
from pokemon import Pokemon


class ElectroBallTests(unittest.TestCase):
    def setUp(self):
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ElectroBall()

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Electro Ball")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 0)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_power_scales_with_speed_ratio(self):
        self.defender.stats["speed"] = 100

        for user_speed, expected_power in (
            (400, 150),
            (300, 120),
            (200, 80),
            (100, 60),
            (99, 40),
        ):
            with self.subTest(user_speed=user_speed):
                self.attacker.stats["speed"] = user_speed
                self.assertEqual(
                    self.move.get_power(self.attacker, self.defender),
                    expected_power,
                )

    def test_move_has_no_secondary_effect(self):
        self.assertIsNone(self.move.effect(self.attacker, self.defender))


if __name__ == "__main__":
    unittest.main()