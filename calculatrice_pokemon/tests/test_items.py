import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from enums.item import Item
from enums.move_category import MoveCategory
from enums.type import Type
from field import Field
from moves import Incinerate, SunnyDay, Tackle
from moves.move import Moves
from pokemon import Pokemon
from main import input_player_action


class FixedDamageMove(Moves):
    def __init__(self):
        super().__init__(
            name="Fixed Damage",
            move_type=Type.NORMAL,
            category=MoveCategory.SPECIAL,
        )

    def effect(self, user, target):
        return None

    def uses_damage_formula(self):
        return False

    def calculate_damage(self, user, target, standard_damage):
        return 25


class ItemTests(unittest.TestCase):
    def test_pokemon_starts_with_no_held_item(self):
        self.assertIs(Pokemon("Eevee").item, Item.NONE)

    def test_sitrus_berry_is_marked_as_a_berry(self):
        self.assertTrue(Item.SITRUS_BERRY.is_berry)
        self.assertFalse(Item.LIFE_ORB.is_berry)

    def test_charizardite_x_is_protected_as_a_mega_stone(self):
        self.assertEqual(Item.CHARIZARDITE_X.value, "Charizardite X")
        self.assertTrue(Item.CHARIZARDITE_X.is_mega_stone)
        self.assertTrue(Item.CHARIZARDITE_X.is_immune_to_item_negation)
        self.assertFalse(Item.CHARIZARDITE_X.can_be_manipulated)

    def test_mega_stones_map_to_their_compatible_pokemon_and_forms(self):
        expected = {
            Item.VENUSAURITE: ("Venusaur", "Mega Venusaur"),
            Item.BLASTOISINITE: ("Blastoise", "Mega Blastoise"),
            Item.CHARIZARDITE_X: ("Charizard", "Mega Charizard X"),
            Item.CHARIZARDITE_Y: ("Charizard", "Mega Charizard Y"),
        }

        for item, mega_evolution in expected.items():
            with self.subTest(item=item):
                self.assertTrue(item.is_mega_stone)
                self.assertTrue(item.is_immune_to_item_negation)
                self.assertFalse(item.can_be_manipulated)
                self.assertEqual(item.mega_evolution, mega_evolution)

    def test_each_mega_stone_evolves_its_matching_pokemon(self):
        expected = (
            (Item.VENUSAURITE, "Venusaur", "Mega Venusaur"),
            (Item.BLASTOISINITE, "Blastoise", "Mega Blastoise"),
            (Item.CHARIZARDITE_X, "Charizard", "Mega Charizard X"),
            (Item.CHARIZARDITE_Y, "Charizard", "Mega Charizard Y"),
        )

        for item, pokemon_name, mega_form in expected:
            with self.subTest(item=item):
                battle_field = Field()
                pokemon = Pokemon(pokemon_name)
                opponent = Pokemon("Eevee")
                pokemon.item = item
                pokemon.add_move(Tackle())
                opponent.add_move(Tackle())
                battle_field.add_pokemon(pokemon, "player")
                battle_field.add_pokemon(opponent, "opponent")
                battle_field.initialize_battle()

                self.assertTrue(battle_field.can_mega_evolve("player"))
                battle_field.mega_evolve("player")

                self.assertEqual(pokemon.form, mega_form)
                self.assertTrue(pokemon.mega_evolved)

    def test_mega_stone_cannot_evolve_the_wrong_pokemon(self):
        battle_field = Field()
        venusaur = Pokemon("Venusaur")
        opponent = Pokemon("Eevee")
        venusaur.item = Item.CHARIZARDITE_X
        battle_field.add_pokemon(venusaur, "player")
        battle_field.add_pokemon(opponent, "opponent")

        self.assertFalse(battle_field.can_mega_evolve("player"))

    def _create_mega_battle(self, opposing_pokemon=None):
        battle_field = Field()
        charizard = Pokemon("Charizard")
        charizard.item = Item.CHARIZARDITE_X
        charizard.add_move(Tackle())
        opponent = opposing_pokemon or Pokemon("Eevee")
        opponent.add_move(Tackle())
        battle_field.add_pokemon(charizard, "player")
        battle_field.add_pokemon(opponent, "opponent")
        battle_field.initialize_battle()
        return battle_field, charizard, opponent

    def test_mega_evolution_is_resolved_with_the_selected_attack(self):
        battle_field, charizard, opponent = self._create_mega_battle()

        battle_field.resolve_turn(
            battle_field.MEGA_ACTION_OFFSET,
            0,
        )

        self.assertEqual(charizard.form, "Mega Charizard X")
        self.assertEqual(charizard.type, [Type.FIRE, Type.DRAGON])
        self.assertTrue(charizard.mega_evolved)
        self.assertTrue(battle_field.player_mega_evolved)
        self.assertFalse(battle_field.can_mega_evolve("player"))
        self.assertEqual(charizard.moves[0].pp, charizard.moves[0].max_pp - 1)

    def test_each_team_can_mega_evolve_once_in_the_same_battle(self):
        opponent = Pokemon("Charizard")
        opponent.item = Item.CHARIZARDITE_X
        battle_field, charizard, _ = self._create_mega_battle(opponent)

        battle_field.resolve_turn(
            battle_field.MEGA_ACTION_OFFSET,
            battle_field.MEGA_ACTION_OFFSET,
        )

        self.assertEqual(charizard.form, "Mega Charizard X")
        self.assertEqual(opponent.form, "Mega Charizard X")
        self.assertTrue(battle_field.player_mega_evolved)
        self.assertTrue(battle_field.opponent_mega_evolved)

    def test_mega_evolution_is_restored_when_a_new_battle_starts(self):
        battle_field, charizard, _ = self._create_mega_battle()
        battle_field.resolve_turn(battle_field.MEGA_ACTION_OFFSET, 0)

        battle_field.initialize_battle()

        self.assertEqual(charizard.form, "")
        self.assertEqual(charizard.type, [Type.FIRE, Type.FLYING])
        self.assertFalse(charizard.mega_evolved)
        self.assertFalse(battle_field.player_mega_evolved)
        self.assertTrue(battle_field.can_mega_evolve("player"))

    def test_player_mega_option_then_prompts_only_for_an_attack(self):
        battle_field, _, _ = self._create_mega_battle()

        with patch("builtins.input", side_effect=["11", "0"]):
            action_index = input_player_action(battle_field)

        self.assertEqual(action_index, battle_field.MEGA_ACTION_OFFSET)

    def setUp(self):
        self.battle_field = Field()
        self.attacker = Pokemon("Eevee")
        self.defender = Pokemon("Bulbasaur")
        self.attacker.item = Item.LIFE_ORB
        self.attacker.add_move(Tackle())
        self.attacker.add_move(FixedDamageMove())
        self.attacker.add_move(SunnyDay())
        self.battle_field.add_pokemon(self.attacker, "player")
        self.battle_field.add_pokemon(self.defender, "opponent")

    def test_adds_life_orb_boost_to_damage_modifiers(self):
        move = self.attacker.moves[0]
        with patch.object(
            self.battle_field,
            "calculate_critical_hit_multiplier",
            return_value=1,
        ):
            self.attacker.item = Item.NONE
            regular_modifiers = self.battle_field.calculate_damage_modifiers(
                self.attacker,
                self.defender,
                move,
            )
            self.attacker.item = Item.LIFE_ORB
            boosted_modifiers = self.battle_field.calculate_damage_modifiers(
                self.attacker,
                self.defender,
                move,
            )

        self.assertAlmostEqual(boosted_modifiers, regular_modifiers * 1.3)

    def test_takes_ten_percent_max_hp_recoil_after_damaging_move(self):
        starting_hp = self.attacker.current_hp
        move = self.attacker.moves[0]

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=20),
        ):
            result = self.battle_field.resolve_move("player", move)

        expected_recoil = self.attacker.max_hp // 10
        self.assertEqual(result["item_recoil"], expected_recoil)
        self.assertEqual(self.attacker.current_hp, starting_hp - expected_recoil)

    def test_fixed_damage_move_is_not_boosted_but_still_causes_recoil(self):
        starting_hp = self.attacker.current_hp
        move = self.attacker.moves[1]

        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", move)

        self.assertEqual(result["damage"], 25)
        self.assertEqual(
            result["item_recoil"],
            self.attacker.max_hp // 10,
        )
        self.assertEqual(self.defender.current_hp, self.defender.max_hp - 25)
        self.assertEqual(self.attacker.current_hp, starting_hp - self.attacker.max_hp // 10)

    def test_status_move_does_not_cause_life_orb_recoil(self):
        move = self.attacker.moves[2]
        with patch.object(self.battle_field, "attack_hits", return_value=True):
            result = self.battle_field.resolve_move("player", move)

        self.assertNotIn("item_recoil", result)

    def test_sitrus_berry_activates_below_half_hp_and_heals_quarter(self):
        self.defender.item = Item.SITRUS_BERRY
        self.defender.current_hp = self.defender.max_hp // 2 + 10
        starting_hp = self.defender.current_hp

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=11),
        ):
            result = self.battle_field.resolve_move(
                "player",
                self.attacker.moves[0],
            )

        healing = self.defender.max_hp // 4
        self.assertEqual(self.defender.current_hp, starting_hp - 11 + healing)
        self.assertIs(self.defender.item, Item.NONE)
        self.assertEqual(result["item_healing"][0]["healed"], healing)

    def test_sitrus_berry_does_not_activate_at_exactly_half_hp(self):
        self.defender.item = Item.SITRUS_BERRY
        self.defender.current_hp = self.defender.max_hp // 2 + 1

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=1),
        ):
            result = self.battle_field.resolve_move(
                "player",
                self.attacker.moves[0],
            )

        self.assertEqual(self.defender.current_hp, self.defender.max_hp // 2)
        self.assertIs(self.defender.item, Item.SITRUS_BERRY)
        self.assertNotIn("item_healing", result)

    def test_incinerate_removes_sitrus_berry_before_it_can_activate(self):
        self.defender.item = Item.SITRUS_BERRY
        self.defender.current_hp = self.defender.max_hp // 2 + 10
        incinerate = Incinerate()

        with (
            patch.object(self.battle_field, "attack_hits", return_value=True),
            patch.object(self.battle_field, "calculate_damage", return_value=11),
        ):
            result = self.battle_field.resolve_move("player", incinerate)

        self.assertIs(self.defender.item, Item.NONE)
        self.assertNotIn("item_healing", result)
        self.assertEqual(
            result["effect"]["item_destroyed"],
            Item.SITRUS_BERRY,
        )

    def test_confusion_self_damage_does_not_cause_life_orb_recoil(self):
        self.attacker.confusion_turns_remaining = 2
        starting_hp = self.attacker.current_hp
        with patch("field.random.random", return_value=0):
            result = self.battle_field.resolve_move(
                "player",
                self.attacker.moves[0],
            )

        self.assertTrue(result["confusion_self_hit"])
        self.assertNotIn("item_recoil", result)
        self.assertLess(self.attacker.current_hp, starting_hp)


if __name__ == "__main__":
    unittest.main()
