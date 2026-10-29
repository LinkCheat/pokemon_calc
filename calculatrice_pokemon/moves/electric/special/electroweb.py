try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Electroweb(Moves):
    def __init__(self):
        """Create the Electric-type special contact move Electroweb."""
        super().__init__(
            name="Electroweb",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=55,
            accuracy=95,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Lower the target's Speed by one stage, down to -6."""
        current_stage = target.stat_modifiers["speed"]
        if current_stage <= -6:
            return {
                "name": self.name,
                "stat": "speed",
                "stages": 0,
                "applied": False,
                "recipient": "target",
            }

        target.stat_modifiers["speed"] = current_stage - 1
        return {
            "name": self.name,
            "stat": "speed",
            "stages": -1,
            "applied": True,
            "recipient": "target",
        }