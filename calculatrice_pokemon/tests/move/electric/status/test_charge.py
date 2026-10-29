import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Charge, Thunderbolt
from pokemon import Pokemon


class ChargeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = Charge()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Charge")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_use_raises_special_defense_and_arms_electric_boost(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(self.attacker.stat_modifiers["sp_def"], 1)
        self.assertTrue(self.attacker.electric_charge_active)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["stages"], 1)

    def test_charge_doubles_next_electric_damage_and_is_consumed(self):
        self.move.effect(self.attacker, self.defender)
        move = Thunderbolt()

        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            charged_modifier = self.battle_field.calculate_damage_modifiers(
                self.attacker, self.defender, move
            )
            self.attacker.electric_charge_active = False
            baseline_modifier = self.battle_field.calculate_damage_modifiers(
                self.attacker, self.defender, move
            )

        self.assertAlmostEqual(charged_modifier / baseline_modifier, 2)

        self.attacker.electric_charge_active = True
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=10),
        ):
            self.battle_field.resolve_move("player", move)

        self.assertFalse(self.attacker.electric_charge_active)

    def test_charge_stays_armed_at_special_defense_limit(self):
        self.attacker.stat_modifiers["sp_def"] = 6

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "stat_limit")
        self.assertTrue(self.attacker.electric_charge_active)

    def test_charge_targets_user_even_against_ground_type(self):
        ground_opponent = Pokemon("Geodude")
        field = Field()
        field.add_pokemon(self.attacker, "player")
        field.add_pokemon(ground_opponent, "opponent")

        result = field.resolve_move("player", self.move)

        self.assertTrue(result["hit"])
        self.assertTrue(self.attacker.electric_charge_active)


if __name__ == "__main__":
    unittest.main()