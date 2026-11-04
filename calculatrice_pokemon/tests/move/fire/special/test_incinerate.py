import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.item import Item
from enums.type import Type
from field import Field
from moves import Incinerate
from pokemon import Pokemon


class IncinerateTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Charizard")
        self.defender = Pokemon("Eevee")
        self.move = Incinerate()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Incinerate")
        self.assertEqual(self.move.type, Type.FIRE)
        self.assertEqual(self.move.category, MoveCategory.SPECIAL)
        self.assertEqual(self.move.power, 60)
        self.assertEqual(self.move.accuracy, 100)
        self.assertEqual(self.move.max_pp, 15)
        self.assertFalse(self.move.contact)

    def test_successful_hit_destroys_held_berry(self):
        self.defender.item = Item.SITRUS_BERRY

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=12),
        ):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["damage"], 12)
        self.assertTrue(result["effect"]["applied"])
        self.assertEqual(result["effect"]["item_destroyed"], Item.SITRUS_BERRY)
        self.assertIs(self.defender.item, Item.NONE)
        self.assertEqual(self.move.pp, 14)

    def test_successful_hit_destroys_held_gem(self):
        self.defender.item = Item.FIRE_GEM

        result = self.move.effect(self.attacker, self.defender)

        self.assertTrue(result["applied"])
        self.assertEqual(result["item_destroyed"], Item.FIRE_GEM)
        self.assertIs(self.defender.item, Item.NONE)

    def test_does_not_destroy_held_mega_stone(self):
        self.defender.name = "Charizard"
        self.defender.item = Item.CHARIZARDITE_X

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertIsNone(result["item_destroyed"])
        self.assertIs(self.defender.item, Item.CHARIZARDITE_X)

    def test_other_held_items_are_not_destroyed(self):
        self.defender.item = Item.CHARCOAL

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertIsNone(result["item_destroyed"])
        self.assertIs(self.defender.item, Item.CHARCOAL)

    def test_no_item_is_reported_as_no_effect(self):
        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertIsNone(result["item_destroyed"])
        self.assertIs(self.defender.item, Item.NONE)

    def test_miss_does_not_destroy_item(self):
        self.defender.item = Item.SITRUS_BERRY

        with patch.object(self.battle_field, "attack_hits", return_value=False):
            result = self.battle_field.resolve_move("player", self.move)

        self.assertFalse(result["hit"])
        self.assertIs(self.defender.item, Item.SITRUS_BERRY)


if __name__ == "__main__":
    unittest.main()
