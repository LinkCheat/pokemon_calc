import copy
import random
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from field import Field
from enums.status_condition import STATUS_CONDITION
from enums.terrain import Terrain
from enums.weather import Weather
from moves import Tackle
from IA.opponent_ai import choose_action, evaluate_state, predict_player_action
from pokemon import Pokemon
from IA import ai_decision_log


class OpponentAITests(unittest.TestCase):
    def setUp(self):
        log_directory = tempfile.TemporaryDirectory()
        self.addCleanup(log_directory.cleanup)
        log_patch = patch.object(
            ai_decision_log,
            "LOG_FILE",
            Path(log_directory.name) / "ai_decisions.log",
        )
        log_patch.start()
        self.addCleanup(log_patch.stop)

        self.battle_field = Field()
        self.player = Pokemon("Bulbasaur")
        self.opponent = Pokemon("Eevee")
        self.opponent_bench = Pokemon("Pikachu")
        self.player.add_move(Tackle())
        self.player.add_move(Tackle())
        self.opponent.add_move(Tackle())
        self.opponent_bench.add_move(Tackle())
        self.battle_field.add_pokemon(self.player, "player")
        self.battle_field.add_pokemon(self.opponent, "opponent")
        self.battle_field.add_pokemon(self.opponent_bench, "opponent")
        self.battle_field.initialize_battle()

    def test_clear_log_empties_existing_battle_history(self):
        ai_decision_log.LOG_FILE.write_text("Ancien combat\n", encoding="utf-8")

        ai_decision_log.clear_log()

        self.assertEqual(
            ai_decision_log.LOG_FILE.read_text(encoding="utf-8"),
            "",
        )

    def test_simulates_legal_actions_without_changing_battle_state(self):
        evaluations = []
        random_state = random.getstate()

        def evaluate(current_field, simulated_field):
            evaluations.append((current_field, simulated_field))
            return 0.0

        action_index = choose_action(
            self.battle_field,
            evaluation_function=evaluate,
        )

        self.assertEqual(action_index, 0)
        self.assertEqual(len(evaluations), 4)
        self.assertTrue(
            all(simulated.turn_number == 1 for _, simulated in evaluations)
        )
        self.assertEqual(self.battle_field.turn_number, 0)
        self.assertEqual(self.battle_field.opponent_active_pokemon, self.opponent)
        self.assertGreater(self.opponent.current_hp, 0)
        self.assertEqual(random.getstate(), random_state)

    def test_selects_action_with_highest_evaluation(self):
        def prefer_switch(current_field, simulated_field):
            return int(simulated_field.opponent_active_pokemon.name == "Pikachu")

        action_index = choose_action(
            self.battle_field,
            evaluation_function=prefer_switch,
        )

        self.assertEqual(
            action_index,
            self.battle_field.SWITCH_INDEX_OFFSET + 1,
        )

    def test_predicts_player_action_with_minimax_and_uses_its_response(self):
        scores = {
            (0, 0): 2,
            (0, 6): 5,
            (1, 0): -1,
            (1, 6): 4,
        }

        def evaluate(current_field, simulated_field):
            return scores[
                (
                    simulated_field.player_action_index,
                    simulated_field.opponent_action_index,
                )
            ]

        self.assertEqual(
            predict_player_action(self.battle_field, evaluate),
            1,
        )
        self.assertEqual(
            choose_action(self.battle_field, evaluate),
            self.battle_field.SWITCH_INDEX_OFFSET + 1,
        )

    def test_writes_minimax_choices_and_scores_to_a_separate_log(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "ai_decisions.log"
            with patch.object(ai_decision_log, "LOG_FILE", log_file):
                choose_action(
                    self.battle_field,
                    lambda current, simulated: float(
                        simulated.player_action_index
                    ),
                )

            log = log_file.read_text(encoding="utf-8")
            self.assertIn("Tour 1", log)
            self.assertIn("attaque Charge (index 0) : ", log)
            self.assertIn("switch vers Pikachu (index 6) : ", log)
            self.assertIn("Choisie : ", log)
            self.assertIn("Joueur prévu : attaque Charge (index 0)", log)
            self.assertNotIn("Action envisagée du joueur", log)
            self.assertNotIn("Prédiction du joueur", log)

    def test_scores_damage_and_healing_by_percentage_of_max_hp(self):
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.current_hp -= self.player.max_hp // 4
        simulated_field.opponent_active_pokemon.current_hp += self.opponent.max_hp // 4

        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field),
            2 * (self.player.max_hp // 4) / self.player.max_hp
            + 2 * (self.opponent.max_hp // 4) / self.opponent.max_hp,
        )

    def test_scores_knockout_in_addition_to_damage(self):
        simulated_field = copy.deepcopy(self.battle_field)
        self.player.current_hp = 1
        simulated_field.player_team[0].current_hp = 0

        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field),
            3 + 2 / self.player.max_hp,
        )

    def test_scores_standard_statuses_against_the_affected_side(self):
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.status_condition = (
            STATUS_CONDITION.BURN
        )
        self.assertEqual(evaluate_state(self.battle_field, simulated_field), 1)

        simulated_field.opponent_active_pokemon.status_condition = (
            STATUS_CONDITION.PARALYSIS
        )
        self.assertEqual(evaluate_state(self.battle_field, simulated_field), 0)

    def test_scores_stat_stages_and_minor_statuses(self):
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.stat_modifiers["attack"] += 2
        simulated_field.player_active_pokemon.confusion_turns_remaining = 2
        simulated_field.opponent_active_pokemon.ingrain_active = True
        simulated_field.opponent_active_pokemon.leech_seeded = True

        self.assertEqual(evaluate_state(self.battle_field, simulated_field), -0.5)

        self.opponent.confusion_turns_remaining = 3
        simulated_field.opponent_active_pokemon.confusion_turns_remaining = 2
        self.assertEqual(
            evaluate_state(self.battle_field, simulated_field),
            -0.5,
        )

    def test_scores_terrain_and_weather_changes(self):
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.terrain = Terrain.GRASSY
        simulated_field.weather = Weather.SUNNY

        self.assertEqual(evaluate_state(self.battle_field, simulated_field), 2)

        simulated_field.terrain = self.battle_field.terrain
        self.assertEqual(evaluate_state(self.battle_field, simulated_field), 1)

    def test_scores_terrain_and_weather_expiration_as_changes(self):
        self.battle_field.terrain = Terrain.GRASSY
        self.battle_field.weather = Weather.SUNNY
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.terrain = None
        simulated_field.weather = None

        self.assertEqual(evaluate_state(self.battle_field, simulated_field), 2)


    def test_scores_electric_minor_statuses(self):
        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.electric_charge_active = True
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), -0.5
        )

        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.electrified = True
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), 0.5
        )

        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.player_active_pokemon.magnet_rise_turns_remaining = 2
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), -0.5
        )

        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.opponent_active_pokemon.electric_charge_active = True
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), 0.5
        )

        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.opponent_active_pokemon.electrified = True
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), -0.5
        )

        simulated_field = copy.deepcopy(self.battle_field)
        simulated_field.opponent_active_pokemon.magnet_rise_turns_remaining = 2
        self.assertAlmostEqual(
            evaluate_state(self.battle_field, simulated_field), 0.5
        )


if __name__ == "__main__":
    unittest.main()
