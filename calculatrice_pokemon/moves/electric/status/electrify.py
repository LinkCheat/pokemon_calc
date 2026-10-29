try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Electrify(Moves):
    def __init__(self):
        """Create the Electric-type status move Electrify."""
        super().__init__(
            name="Electrify",
            move_type=Type.ELECTRIC,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=20,
            contact=False,
        )

    def effect(self, user, target):
        """Make the target's next move Electric if it has not acted yet."""
        if target.has_acted_this_turn:
            return {
                "name": self.name,
                "applied": False,
                "reason": "target_already_acted",
            }

        target.electrified = True
        return {
            "name": self.name,
            "applied": True,
            "type": Type.ELECTRIC,
            "recipient": "target",
        }