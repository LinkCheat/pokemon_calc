try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ShockWave(Moves):
    def __init__(self):
        """Create the Electric-type special move Shock Wave."""
        super().__init__(
            name="Shock Wave",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=60,
            accuracy=101,
            max_pp=20,
            contact=False,
        )

    def effect(self, user, target):
        """Shock Wave has no secondary effect."""
        return None