import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import ZapCannon
from pokemon import Pokemon


class ZapCannonTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ZapCannon()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Zap Cannon")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 50)
        self.assertEqual(self.move.max_pp, 5)
        self.assertFalse(self.move.contact)

    def test_successful_hit_always_paralyzes_target(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertEqual(self.move.pp, 4)

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