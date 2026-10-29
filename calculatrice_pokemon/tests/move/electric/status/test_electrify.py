import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Electrify, Tackle
from pokemon import Pokemon


class ElectrifyTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = Electrify()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Electrify")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 20)
        self.assertFalse(self.move.contact)

    def test_electrify_changes_target_move_type(self):
        result = self.move.effect(self.attacker, self.defender)
        normal_effectiveness = self.battle_field.calculate_move_effectiveness(
            Tackle(), self.attacker, self.defender
        )
        electrified_effectiveness = self.battle_field.calculate_move_effectiveness(
            Tackle(), Pokemon("Geodude"), self.defender
        )

        self.assertTrue(result["applied"])
        self.assertTrue(self.defender.electrified)
        self.assertEqual(normal_effectiveness, 0.5)
        self.assertEqual(electrified_effectiveness, 0.0)

    def test_electrify_does_not_affect_a_target_that_already_acted(self):
        self.defender.has_acted_this_turn = True

        result = self.move.effect(self.attacker, self.defender)

        self.assertFalse(result["applied"])
        self.assertEqual(result["reason"], "target_already_acted")
        self.assertFalse(self.defender.electrified)

    def test_electrify_expires_after_target_uses_its_move(self):
        self.move.effect(self.attacker, self.defender)

        self.battle_field.resolve_move("opponent", Tackle())

        self.assertFalse(self.defender.electrified)


if __name__ == "__main__":
    unittest.main()