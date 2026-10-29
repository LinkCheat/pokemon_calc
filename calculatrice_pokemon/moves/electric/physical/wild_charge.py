try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class WildCharge(Moves):
    def __init__(self):
        """Create the Electric-type physical contact move Wild Charge."""
        super().__init__(
            name="Wild Charge",
            move_type=Type.ELECTRIC,
            category=MoveCategory.PHYSICAL,
            power=90,
            accuracy=100,
            max_pp=15,
            contact=True,
        )

    def effect(self, user, target):
        """Wild Charge has no effect before damage is calculated."""
        return None

    def apply_effect(self, user, target, damage_dealt):
        """Inflict recoil equal to one quarter of the damage actually dealt."""
        recoil = min(damage_dealt // 4, user.current_hp)
        user.current_hp -= recoil
        return {
            "name": self.name,
            "recoil": recoil,
        }