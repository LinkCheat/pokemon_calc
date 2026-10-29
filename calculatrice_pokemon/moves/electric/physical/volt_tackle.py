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


class VoltTackle(Moves):
    PARALYSIS_CHANCE = 0.1

    def __init__(self):
        """Create the Electric-type physical contact move Volt Tackle."""
        super().__init__(
            name="Volt Tackle",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=120,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Volt Tackle's recoil and paralysis are applied after damage."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Apply one-third recoil and a 10% chance to paralyze the target."""
        recoil = min(damage_dealt // 3, user.current_hp)
        user.current_hp -= recoil

        result = {
            "name": self.name,
            "recoil": recoil,
            "status": None,
            "applied": False,
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

        return result