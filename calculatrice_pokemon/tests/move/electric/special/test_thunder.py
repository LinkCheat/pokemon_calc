import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.status_condition import STATUS_CONDITION
from enums.type import Type
from enums.weather import Weather
from field import Field
from moves import Thunder
from pokemon import Pokemon


class ThunderTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = Thunder()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Thunder")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 110)
        self.assertEqual(self.move.accuracy, 70)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_weather_changes_accuracy(self):
        self.assertEqual(
            self.move.get_accuracy(self.attacker, self.defender, self.battle_field),
            70,
        )

        self.battle_field.weather = Weather.RAINY
        self.assertEqual(
            self.move.get_accuracy(self.attacker, self.defender, self.battle_field),
            100,
        )

        self.battle_field.weather = Weather.SUNNY
        self.assertEqual(
            self.move.get_accuracy(self.attacker, self.defender, self.battle_field),
            50,
        )

    def test_field_accuracy_roll_uses_weather_adjusted_accuracy(self):
        self.battle_field.weather = Weather.RAINY
        with patch("field.random.random") as roll:
            self.assertTrue(
                self.battle_field.attack_hits(self.attacker, self.defender, self.move)
            )
        roll.assert_not_called()

        self.battle_field.weather = Weather.SUNNY
        with patch("field.random.random", return_value=0.6):
            self.assertFalse(
                self.battle_field.attack_hits(self.attacker, self.defender, self.move)
            )

    def test_successful_hit_can_paralyze_target(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
            patch("moves.electric.special.thunder.random.random", return_value=0.299999),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertTrue(result["effect"]["applied"])
        self.assertIs(self.defender.status_condition, STATUS_CONDITION.PARALYSIS)
        self.assertEqual(self.move.pp, 9)

    def test_paralysis_chance_failure_does_not_affect_target(self):
        with patch("moves.electric.special.thunder.random.random", return_value=0.3):
            result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "chance_failed")
        self.assertIsNone(self.defender.status_condition)

    def test_miss_does_not_attempt_to_paralyze(self):
        with (
            patch.object(self.battle_field, "attack_hits", return_value=False),
            patch("moves.electric.special.thunder.random.random") as roll,
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIsNone(self.defender.status_condition)
        roll.assert_not_called()


if __name__ == "__main__":
    unittest.main()