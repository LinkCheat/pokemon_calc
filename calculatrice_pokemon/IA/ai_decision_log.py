from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).with_name("ai_decisions.log")


def clear_log():
    """Clear the decision log when a new battle starts."""
    LOG_FILE.write_text("", encoding="utf-8")


def _describe_action(battle_field, side, action_index):
    """Return a readable move or switch description for an action index."""
    team = (
        battle_field.player_team
        if side == "player"
        else battle_field.opponent_team
    )
    active_pokemon = (
        battle_field.player_active_pokemon
        if side == "player"
        else battle_field.opponent_active_pokemon
    )

    if 0 <= action_index < 4:
        selected_move = (
            active_pokemon.locked_move
            or active_pokemon.charging_move
            or active_pokemon.recharging_move
            or active_pokemon.moves[action_index]
        )
        return f"attaque {selected_move.name} (index {action_index})"

    team_index = action_index - battle_field.SWITCH_INDEX_OFFSET
    return f"switch vers {team[team_index].name} (index {action_index})"


def write_decision_log(
    battle_field,
    analysis,
    predicted_player_action,
    selected_opponent_action,
    predicted_score,
):
    """Append opponent action scores and the selected action to the log."""
    predicted_candidate = next(
        candidate
        for candidate in analysis
        if candidate["player_action"] == predicted_player_action
    )
    lines = [
        f"Tour {battle_field.turn_number + 1} "
        f"({datetime.now().astimezone().isoformat(timespec='seconds')})"
    ]

    for response in predicted_candidate["opponent_responses"]:
        lines.append(
            f"{_describe_action(battle_field, 'opponent', response['action_index'])}"
            f" : {response['score']:+.3f}"
        )

    lines.extend((
        f"Joueur prévu : "
        f"{_describe_action(battle_field, 'player', predicted_player_action)}",
        f"Choisie : "
        f"{_describe_action(battle_field, 'opponent', selected_opponent_action)} "
        f"({predicted_score:+.3f})",
        "",
    ))

    with LOG_FILE.open("a", encoding="utf-8") as log_file:
        log_file.write("\n".join(lines))
