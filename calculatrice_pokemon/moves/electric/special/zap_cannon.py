try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ZapCannon(Moves):
    def __init__(self):
        """Create the Electric-type special move Zap Cannon."""
        super().__init__(
            name="Zap Cannon",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=120,
            accuracy=50,
            max_pp=5,
            contact=False,
        )

    def effect(self, user, target):
        """Paralyze the target if its type and status allow it."""
        if Type.ELECTRIC in target.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        return self.inflict_paralysis(target)