import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import ParabolicCharge
from pokemon import Pokemon


class ParabolicChargeTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ParabolicCharge()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Parabolic Charge")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 65)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_heals_half_the_damage_dealt(self):
        self.attacker.current_hp -= 30

        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 20)
        self.assertEqual(result["effect"]["healed"], 10)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 20)
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 20)

    def test_healing_uses_actual_damage_when_target_faints(self):
        self.attacker.current_hp -= 30
        self.defender.current_hp = 10

        with patch.object(self.battle_field, "calculate_damage", return_value=30):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 30)
        self.assertEqual(result["effect"]["healed"], 5)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 25)
        self.assertEqual(self.defender.current_hp, 0)

    def test_healing_does_not_exceed_maximum_hp(self):
        with patch.object(self.battle_field, "calculate_damage", return_value=20):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["healed"], 0)
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp)

    def test_miss_does_not_heal_user(self):
        self.attacker.current_hp -= 30

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertEqual(self.attacker.current_hp, self.attacker.max_hp - 30)


if __name__ == "__main__":
    unittest.main()