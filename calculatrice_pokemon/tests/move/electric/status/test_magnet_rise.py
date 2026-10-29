import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import MagnetRise
from pokemon import Pokemon


class MagnetRiseTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = MagnetRise()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Magnet Rise")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_use_makes_user_ungrounded_for_five_turns(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(self.attacker.magnet_rise_turns_remaining, 5)
        self.assertFalse(self.battle_field._is_grounded(self.attacker))

    def test_magnet_rise_expires_after_five_turn_ticks(self):
        self.move.effect(self.attacker, self.defender)

        for _ in range(self.move.DURATION):
            self.battle_field._apply_magnet_rise()

        self.assertEqual(self.attacker.magnet_rise_turns_remaining, 0)
        self.assertTrue(self.battle_field._is_grounded(self.attacker))

    def test_gravity_prevents_magnet_rise(self):
        self.battle_field.gravity_active = True

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["failed"])
        self.assertEqual(result["effect"]["reason"], "gravity_active")
        self.assertEqual(self.attacker.magnet_rise_turns_remaining, 0)

    def test_ingrain_prevents_magnet_rise(self):
        self.attacker.ingrain_active = True

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertTrue(result["failed"])
        self.assertEqual(result["effect"]["reason"], "ingrain_active")
        self.assertEqual(self.attacker.magnet_rise_turns_remaining, 0)

    def test_switching_out_ends_magnet_rise(self):
        reserve = Pokemon("Raichu")
        self.battle_field.add_pokemon(reserve, "player")
        self.move.effect(self.attacker, self.defender)

        self.battle_field.switch_pokemon("player", 1)

        self.assertEqual(self.attacker.magnet_rise_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()