import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from field import Field
from moves import VoltTackle
from pokemon import Pokemon


class VoltTackleTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = VoltTackle()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Volt Tackle")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.PHYSICAL)
        self.assertEqual(self.move.power, 120)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertTrue(self.move.contact)

    def test_recoil_and_paralysis_are_applied_on_hit(self):
        with (
            patch.object(self.battle_field, "calculate_damage", return_value=30),
            patch(
                "moves.electric.physical.volt_tackle.random.random",
                return_value=0.05,
            ),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 10)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 10)

    def test_recoil_uses_actual_damage_when_target_faints(self):
        self.defender.current_hp = 10

        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 3)
        self.assertEqual(self.defender.current_hp, 0)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 3)

    def test_recoil_cannot_reduce_user_below_zero_hp(self):
        self.attacker.current_hp = 2

        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["recoil"], 2)
        self.assertEqual(self.attacker.current_hp, 0)

    def test_electric_type_target_is_immune_to_paralysis(self):
        electric_target = Pokemon("Pikachu")

        with patch(
            "moves.electric.physical.volt_tackle.random.random"
        ) as roll:
            result = self.move.apply_effect(self.attacker, electric_target, 30)

        self.assertEqual(result["recoil"], 10)
        self.assertEqual(result["reason"], "type_immune")
        self.assertIsNone(electric_target.status_condition)
        roll.assert_not_called()

    def test_miss_does_not_inflict_recoil_or_paralysis(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.electric.physical.volt_tackle.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(result["damage"], 0)
        self.assertIsNone(self.defender.status_condition)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()