try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ThunderWave(Moves):
    def __init__(self):
        """Create the Electric-type status move Thunder Wave."""
        super().__init__(
            name="Thunder Wave",
            move_type=Type.ELECTRIC,
            category=MoveCategory.STATUS,
            accuracy=90,
            max_pp=20,
            contact=False,
        )

    def effect(self, user, target):
        """Paralyze a target that is not immune to Electric status moves."""
        if Type.ELECTRIC in target.type or Type.GROUND in target.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        return self.inflict_paralysis(target)