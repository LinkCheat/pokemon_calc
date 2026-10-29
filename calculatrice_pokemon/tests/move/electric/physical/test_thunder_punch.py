import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import ThunderPunch
from pokemon import Pokemon


class ThunderPunchTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ThunderPunch()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Thunder Punch")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 75)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_successful_hit_can_paralyze_target(self):
        with (
            patch.object(self.battle_field, "calculate_damage", return_value=20),
            patch(
                "moves.electric.physical.thunder_punch.random.random",
                return_value=0.099999,
            ),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertEqual(self.move.pp, 14)

    def test_paralysis_chance_failure_does_not_affect_target(self):
        with patch(
            "moves.electric.physical.thunder_punch.random.random",
            return_value=0.1,
        ):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertIsNone(self.defender.status_condition)

    def test_electric_type_target_is_immune_to_paralysis(self):
        electric_target = Pokemon("Pikachu")

        with patch(
            "moves.electric.physical.thunder_punch.random.random"
        ) as roll:
            result = self.move.effect(self.attacker, electric_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(electric_target.status_condition)
        roll.assert_not_called()

    def test_existing_status_is_not_replaced(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        with patch(
            "moves.electric.physical.thunder_punch.random.random"
        ) as roll:
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)
        roll.assert_not_called()

    def test_miss_does_not_attempt_to_paralyze(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.electric.physical.thunder_punch.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()