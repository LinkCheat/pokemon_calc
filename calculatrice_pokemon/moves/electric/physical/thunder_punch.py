import random

try:
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ThunderPunch(Moves):
    PARALYSIS_CHANCE = 0.1

    def __init__(self):
        """Create the Electric-type physical contact punching move Thunder Punch."""
        super().__init__(
            name="Thunder Punch",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=75,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Try to paralyze the target with a 10% chance."""
        if Type.ELECTRIC in target.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        if target.status_condition is not None:
            return self.inflict_paralysis(target)
        if random.random() < self.PARALYSIS_CHANCE:
            return self.inflict_paralysis(target)
        return {
            "name": self.name,
            "status": None,
            "applied": False,
            "reason": "chance_failed",
        }