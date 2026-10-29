try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class ElectroBall(Moves):
    def __init__(self):
        """Create the Electric-type special move Electro Ball."""
        super().__init__(
            name="Electro Ball",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=0,
            accuracy=100,
            max_pp=10,
            contact=False,
        )

    def get_power(self, user, target, field=None):
        """Return power according to the user's Speed relative to the target."""
        user_speed = user.stats["speed"]
        target_speed = target.stats["speed"]

        if user_speed >= target_speed * 4:
            return 150
        if user_speed >= target_speed * 3:
            return 120
        if user_speed >= target_speed * 2:
            return 80
        if user_speed >= target_speed:
            return 60
        return 40

    def effect(self, user, target):
        """Electro Ball has no secondary effect."""
        return None