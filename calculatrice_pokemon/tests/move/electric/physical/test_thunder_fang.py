import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import ThunderFang
from moves.normal.physical.tackle import Tackle
from pokemon import Pokemon


class ThunderFangTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Zekrom")
        self.defender = Pokemon("Eevee")
        self.attacker.add_move(ThunderFang())
        self.defender.add_move(Tackle())
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")
        self.move = self.attacker.moves[0]

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Thunder Fang")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 65)
        self.assertEqual(self.move.accuracy, 95)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_paralysis_and_flinch_can_happen_simultaneously(self):
        self.attacker.stats["speed"] = 200
        self.defender.stats["speed"] = 100

        with (
            patch.object(Pokemon, "calculateStats"),
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
            patch(
                "moves.electric.physical.thunder_fang.random.random",
                side_effect=(0.05, 0.05),
            ),
        ):
            results = self.battle_field.resolve_turn(0, 0)

        player_result = next(
            item["result"] for item in results if item["action"]["side"] == "player"
        )
        opponent_result = next(
            item["result"] for item in results if item["action"]["side"] == "opponent"
        )
        self.assertTrue(player_result["effect"]["applied"])
        self.assertTrue(player_result["effect"]["flinched"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertTrue(opponent_result["unable_to_act"])
        self.assertTrue(opponent_result["flinched"])
        self.assertEqual(self.move.pp, 14)

    def test_failed_paralysis_roll_does_not_prevent_flinch(self):
        with patch(
            "moves.electric.physical.thunder_fang.random.random",
            side_effect=(0.1, 0.05),
        ):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertTrue(result["flinched"])
        self.assertTrue(self.defender.flinched)
        self.assertIsNone(self.defender.status_condition)

    def test_flinch_is_not_applied_after_target_has_acted(self):
        self.defender.has_acted_this_turn = True

        with patch(
            "moves.electric.physical.thunder_fang.random.random",
            return_value=0.05,
        ) as roll:
            result = self.move.effect(self.attacker, self.defender)

        self.assertTrue(result["applied"])
        self.assertFalse(result["flinched"])
        self.assertEqual(result["flinch_reason"], "target_already_acted")
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        roll.assert_called_once()

    def test_electric_type_target_is_immune_to_paralysis_but_can_flinch(self):
        electric_target = Pokemon("Pikachu")

        with patch(
            "moves.electric.physical.thunder_fang.random.random",
            return_value=0.05,
        ) as roll:
            result = self.move.effect(self.attacker, electric_target)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "type_immune")
        self.assertTrue(result["flinched"])
        self.assertTrue(electric_target.flinched)
        self.assertIsNone(electric_target.status_condition)
        roll.assert_called_once()

    def test_existing_status_prevents_paralysis_without_preventing_flinch(self):
        self.defender.status_condition = STATUS_CONDITION.POISON

        with patch(
            "moves.electric.physical.thunder_fang.random.random",
            return_value=0.05,
        ) as roll:
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "already_statused")
        self.assertTrue(result["flinched"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.POISON)
        roll.assert_called_once()

    def test_miss_does_not_attempt_either_secondary_effect(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.electric.physical.thunder_fang.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)
        self.assertFalse(self.defender.flinched)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()