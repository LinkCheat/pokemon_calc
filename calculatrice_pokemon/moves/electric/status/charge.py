try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class Charge(Moves):
    def __init__(self):
        """Create the Electric-type status move Charge."""
        super().__init__(
            name="Charge",
            move_type=Type.ELECTRIC,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=20,
            contact=False,
        )

    def targets_user(self):
        return True

    def effect(self, user, target):
        """Charge the next Electric move and raise Special Defense by one."""
        user.electric_charge_active = True
        current_stage = user.stat_modifiers["sp_def"]
        if current_stage >= 6:
            return {
                "name": self.name,
                "stat": "sp_def",
                "stages": 0,
                "applied": False,
                "reason": "stat_limit",
                "recipient": "user",
                "charge_active": True,
            }

        user.stat_modifiers["sp_def"] = current_stage + 1
        return {
            "name": self.name,
            "stat": "sp_def",
            "stages": 1,
            "applied": True,
            "recipient": "user",
            "charge_active": True,
        }