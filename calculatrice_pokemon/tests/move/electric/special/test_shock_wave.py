import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import ShockWave
from pokemon import Pokemon


class ShockWaveTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ShockWave()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Shock Wave")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 60)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_move_always_hits(self):
        self.attacker.stat_modifiers["accuracy"] = -6
        self.defender.stat_modifiers["evasion"] = 6

        with patch("field.random.random") as roll:
            self.assertTrue(
                self.battle_field.attack_hits(self.attacker, self.defender, self.move)
            )

        roll.assert_not_called()

    def test_move_has_no_secondary_effect(self):
        self.assertIsNone(self.move.effect(self.attacker, self.defender))


if __name__ == "__main__":
    unittest.main()