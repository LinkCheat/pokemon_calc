import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import Nuzzle
from pokemon import Pokemon


class NuzzleTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = Nuzzle()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Nuzzle")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 20)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 20)
        self.assertTrue(self.move.contact)

    def test_successful_hit_always_paralyzes_target(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=5):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 5)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertEqual(self.move.pp, 19)

    def test_electric_type_target_is_immune_to_paralysis(self):
        electric_target = Pokemon("Pikachu")

        result = self.move.effect(self.attacker, electric_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(electric_target.status_condition)

    def test_existing_status_is_not_replaced(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)

    def test_miss_does_not_paralyze_target(self):
        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)


if __name__ == "__main__":
    unittest.main()