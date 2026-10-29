try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Nuzzle(Moves):
    def __init__(self):
        """Create the Electric-type physical contact move Nuzzle."""
        super().__init__(
            name="Nuzzle",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=20,
            accuracy=100,
            max_pp=20,
            contact=True,
        )

    def effect(self, user, target):
        """Paralyze the target if its type allows it and it has no status."""
        if Type.ELECTRIC in target.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        return self.inflict_paralysis(target)