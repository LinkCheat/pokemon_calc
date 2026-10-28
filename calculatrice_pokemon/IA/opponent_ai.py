import copy
import random

try:
    from enums.type import Type
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.type import Type

try:
    from . import ai_decision_log
except ImportError:
    from calculatrice_pokemon.IA import ai_decision_log


def evaluate_state(current_field, simulated_field):
    """Score the simulated state's benefits to the opponent over the current state."""
    score = 0.0
    score += _evaluate_team(current_field.player_team, simulated_field.player_team, -1)
    score += _evaluate_team(current_field.opponent_team, simulated_field.opponent_team, 1)
    if current_field.terrain is not simulated_field.terrain:
        score += 1
    if current_field.weather is not simulated_field.weather:
        score += 1
    return score


def _evaluate_team(current_team, simulated_team, side_multiplier):
    """Score changes to a team's Pokémon, positive from the opponent's perspective."""
    score = 0.0
    for current_pokemon, simulated_pokemon in zip(current_team, simulated_team):
        max_hp = current_pokemon.max_hp
        hp_change = simulated_pokemon.current_hp - current_pokemon.current_hp
        score += side_multiplier * 2 * hp_change / max_hp

        if current_pokemon.current_hp > 0 and simulated_pokemon.current_hp <= 0:
            score -= side_multiplier * 3

        if current_pokemon.status_condition is not simulated_pokemon.status_condition:
            if simulated_pokemon.status_condition is None:
                status_change = 1
            elif current_pokemon.status_condition is None:
                status_change = -1
            else:
                status_change = 0
            score += side_multiplier * status_change

        for stat_name, current_stage in current_pokemon.stat_modifiers.items():
            simulated_stage = simulated_pokemon.stat_modifiers[stat_name]
            score += side_multiplier * 0.5 * (simulated_stage - current_stage)

        for attribute, is_beneficial in _MINOR_STATUS_EFFECTS:
            was_active = _is_minor_status_active(current_pokemon, attribute)
            is_active = _is_minor_status_active(simulated_pokemon, attribute)
            if was_active != is_active:
                effect_value = 0.5 if is_beneficial else -0.5
                score += side_multiplier * effect_value * (1 if is_active else -1)

    return score


_MINOR_STATUS_EFFECTS = (
    ("confusion_turns_remaining", False),
    ("leech_seeded", False),
    ("ingrain_active", True),
    ("snap_trap_turns_remaining", False),
    ("fire_spin_turns_remaining", False),
    ("magma_storm_turns_remaining", False),
    ("syrupy_turns_remaining", False),
)


def _is_minor_status_active(pokemon, attribute):
    """Treat counters as active/inactive instead of scoring every remaining turn."""
    value = getattr(pokemon, attribute)
    if attribute.endswith("_turns_remaining"):
        return value > 0
    return value


def _available_action_indexes(battle_field, side):
    """Return legal move and switch indexes for one side."""
    active_pokemon = (
        battle_field.player_active_pokemon
        if side == "player"
        else battle_field.opponent_active_pokemon
    )
    if active_pokemon is None:
        raise ValueError(f"L'équipe {side} ne contient aucun Pokémon actif.")

    action_indexes = []
    if active_pokemon.current_hp > 0:
        forced_move = (
            active_pokemon.locked_move
            or active_pokemon.charging_move
            or active_pokemon.recharging_move
        )
        if forced_move is not None:
            try:
                action_indexes.append(active_pokemon.moves.index(forced_move))
            except ValueError as error:
                raise ValueError(
                    f"L'attaque forcée du Pokémon {side} ne fait pas partie de ses attaques."
                ) from error
        else:
            for move_index, selected_move in enumerate(
                active_pokemon.moves[:active_pokemon.MAX_MOVES]
            ):
                if selected_move.pp > 0:
                    action_indexes.append(move_index)

    can_switch = active_pokemon.current_hp <= 0 or (
        active_pokemon.locked_move is None
        and not (
            active_pokemon.ingrain_active
            and Type.GHOST not in active_pokemon.type
        )
        and not (
            active_pokemon.snap_trap_turns_remaining > 0
            or active_pokemon.fire_spin_turns_remaining > 0
            or active_pokemon.magma_storm_turns_remaining > 0
        )
    )
    if can_switch:
        team = (
            battle_field.player_team
            if side == "player"
            else battle_field.opponent_team
        )
        for team_index, teammate in enumerate(team):
            if (
                teammate is not active_pokemon
                and teammate.current_hp > 0
            ):
                action_indexes.append(
                    battle_field.SWITCH_INDEX_OFFSET + team_index
                )

    if not action_indexes:
        raise ValueError(f"Aucune action légale n'est disponible pour {side}.")
    return action_indexes


def _best_opponent_response(
    battle_field,
    player_action_index,
    evaluation_function,
    random_state,
):
    """Return the opponent's best response and its score for one player action."""
    best_action_index = None
    best_score = None
    responses = []
    for action_index in _available_action_indexes(battle_field, "opponent"):
        random.setstate(random_state)
        simulated_field = copy.deepcopy(battle_field)
        simulated_field.resolve_turn(player_action_index, action_index)
        score = evaluation_function(battle_field, simulated_field)
        responses.append({"action_index": action_index, "score": score})
        if best_score is None or score > best_score:
            best_action_index = action_index
            best_score = score
    return best_action_index, best_score, responses


def _predict_player_action_and_response(battle_field, evaluation_function):
    """Predict the player's minimax action and the opponent's response to it."""
    random_state = random.getstate()
    best_player_action = None
    best_opponent_action = None
    best_opponent_score = None
    analysis = []

    try:
        for player_action in _available_action_indexes(battle_field, "player"):
            opponent_action, opponent_score, responses = _best_opponent_response(
                battle_field,
                player_action,
                evaluation_function,
                random_state,
            )
            analysis.append({
                "player_action": player_action,
                "opponent_responses": responses,
                "best_opponent_action": opponent_action,
                "best_opponent_score": opponent_score,
            })
            if (
                best_opponent_score is None
                or opponent_score < best_opponent_score
            ):
                best_player_action = player_action
                best_opponent_action = opponent_action
                best_opponent_score = opponent_score
    finally:
        random.setstate(random_state)

    ai_decision_log.write_decision_log(
        battle_field,
        analysis,
        best_player_action,
        best_opponent_action,
        best_opponent_score,
    )
    return best_player_action, best_opponent_action


def predict_player_action(battle_field, evaluation_function=None):
    """Predict the player's action that minimizes the opponent's best score."""
    if evaluation_function is None:
        evaluation_function = evaluate_state

    player_action, _ = _predict_player_action_and_response(
        battle_field,
        evaluation_function,
    )
    return player_action


def choose_action(battle_field, evaluation_function=None):
    """Choose the best opponent response to the predicted player action."""
    if evaluation_function is None:
        evaluation_function = evaluate_state

    _, opponent_action = _predict_player_action_and_response(
        battle_field,
        evaluation_function,
    )
    return opponent_action
