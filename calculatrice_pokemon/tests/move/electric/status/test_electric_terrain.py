import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from enums.move_category import MoveCategory
from enums.terrain import Terrain
from enums.type import Type
from field import Field
from moves import ElectricTerrain, Spore, Thunderbolt
from pokemon import Pokemon


class ElectricTerrainTests(unittest.TestCase):
    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Pikachu")
        self.defender = Pokemon("Eevee")
        self.move = ElectricTerrain()
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_move_metadata(self):
        self.assertEqual(self.move.name, "Electric Terrain")
        self.assertEqual(self.move.type, Type.ELECTRIC)
        self.assertEqual(self.move.category, MoveCategory.STATUS)
        self.assertEqual(self.move.accuracy, 101)
        self.assertEqual(self.move.max_pp, 10)
        self.assertFalse(self.move.contact)

    def test_successful_use_sets_electric_terrain_for_five_turns(self):
        result = self.battle_field.resolve_move("player", self.move)

        self.assertEqual(result["effect"]["condition"], "electric_terrain")
        self.assertEqual(self.battle_field.terrain, Terrain.ELECTRIC)
        self.assertEqual(self.battle_field.terrain_turns_remaining, 5)
        self.assertEqual(self.move.pp, 9)

    def test_electric_terrain_boosts_grounded_electric_damage(self):
        self.battle_field.terrain = Terrain.ELECTRIC
        move = Thunderbolt()

        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            terrain_modifier = self.battle_field.calculate_damage_modifiers(
                self.attacker, self.defender, move
            )
            self.battle_field.terrain = None
            baseline_modifier = self.battle_field.calculate_damage_modifiers(
                self.attacker, self.defender, move
            )

        self.assertAlmostEqual(terrain_modifier / baseline_modifier, 1.3)

    def test_electric_terrain_does_not_boost_flying_attacker(self):
        flying_attacker = Pokemon("Charizard")
        self.battle_field.terrain = Terrain.ELECTRIC
        move = Thunderbolt()

        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1.0,
        ):
            terrain_modifier = self.battle_field.calculate_damage_modifiers(
                flying_attacker, self.defender, move
            )
            self.battle_field.terrain = None
            baseline_modifier = self.battle_field.calculate_damage_modifiers(
                flying_attacker, self.defender, move
            )

        self.assertAlmostEqual(terrain_modifier, baseline_modifier)

    def test_electric_terrain_prevents_grounded_targets_from_falling_asleep(self):
        self.battle_field.terrain = Terrain.ELECTRIC
        move = Spore()

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("opponent", move)

        self.assertFalse(result["effect"]["applied"])
        self.assertEqual(result["effect"]["reason"], "electric_terrain")
        self.assertIsNone(self.attacker.status_condition)

    def test_electric_terrain_expires_after_its_last_turn(self):
        self.battle_field.terrain = Terrain.ELECTRIC
        self.battle_field.terrain_turns_remaining = 1

        self.battle_field._apply_grassy_terrain()

        self.assertIsNone(self.battle_field.terrain)
        self.assertEqual(self.battle_field.terrain_turns_remaining, 0)


if __name__ == "__main__":
    unittest.main()