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


class ThunderFang(Moves):
    PARALYSIS_CHANCE = 0.1
    FLINCH_CHANCE = 0.1

    def __init__(self):
        """Create the Electric-type physical contact move Thunder Fang."""
        super().__init__(
            name="Thunder Fang",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=65,
            accuracy=95,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Independently try to paralyze and flinch the target."""
        result = {
            "name": self.name,
            "status": None,
            "applied": False,
            "flinched": False,
        }

        if Type.ELECTRIC in target.type:
            result["reason"] = "type_immune"
        elif target.status_condition is not None:
            result["reason"] = "already_statused"
        elif random.random() < self.PARALYSIS_CHANCE:
            target.status_condition = STATUS_CONDITION.PARALYSIS
            result["status"] = STATUS_CONDITION.PARALYSIS
            result["applied"] = True
        else:
            result["reason"] = "chance_failed"

        if target.has_acted_this_turn:
            result["flinch_reason"] = "target_already_acted"
        elif random.random() < self.FLINCH_CHANCE:
            target.flinched = True
            result["flinched"] = True
        else:
            result["flinch_reason"] = "chance_failed"

        return result