import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Electroweb
from pokemon import Pokemon


class ElectrowebTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = Electroweb()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Electroweb")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 55)
        self.assertEqual(self.move.accuracy, 95)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_successful_hit_lowers_target_speed(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 10)
        self.assertEqual(self.defender.stat_modifiers["speed"], -1)
        self.assertEqual(result["effect"]["stages"], -1)
        self.assertTrue(result["effect"]["applied"])

    def test_speed_drop_respects_negative_six_limit(self):
        self.defender.stat_modifiers["speed"] = -6

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["stages"], 0)
        self.assertEqual(self.defender.stat_modifiers["speed"], -6)

    def test_miss_does_not_lower_target_speed(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.defender.stat_modifiers["speed"], 0)


if __name__ == "__main__":
    unittest.main()