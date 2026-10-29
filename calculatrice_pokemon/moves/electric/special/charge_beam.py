import random

try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ChargeBeam(Moves):
    SP_ATK_BOOST_CHANCE = 0.7

    def __init__(self):
        """Create the Electric-type special move Charge Beam."""
        super().__init__(
            name="Charge Beam",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=50,
            accuracy=90,
            max_pp=10,
            contact=False,
        )

    def effect(self, user, target):
        """Raise the user's Special Attack by one stage with 70% chance."""
        if random.random() >= self.SP_ATK_BOOST_CHANCE:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "reason": "chance_failed",
                "recipient": "user",
            }

        current_stage = user.stat_modifiers["sp_atk"]
        if current_stage >= 6:
            return {
                "name": self.name,
                "stat": "sp_atk",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
                "recipient": "user",
            }

        user.stat_modifiers["sp_atk"] = current_stage + 1
        return {
            "name": self.name,
            "stat": "sp_atk",
            "stages": 1,
            "applied": True,
            "recipient": "user",
        }