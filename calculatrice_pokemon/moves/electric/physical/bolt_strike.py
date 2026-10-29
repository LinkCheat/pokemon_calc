import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class BoltStrike(Moves):
    PARALYSIS_CHANCE = 0.2

    def __init__(self):
        """Create the Electric-type physical contact move Bolt Strike."""
        super().__init__(
            name="Bolt Strike",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=130,
            accuracy=85,
            max_pp=5,
            contact=True,
        )

    def effect(self, user, target):
        """Try to paralyze the target with a 20% chance."""
        if target.status_condition is not None:
            return self.inflict_paralysis(target)
        if random.random() >= self.PARALYSIS_CHANCE:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "chance_failed",
            }
        return self.inflict_paralysis(target)