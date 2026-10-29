import random

try:
    from enums.move_category import MoveCategory
    from enums.status_condition import STATUS_CONDITION
    from enums.type import Type
    from enums.weather import Weather
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.status_condition import STATUS_CONDITION
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.enums.weather import Weather
    from calculatrice_pokemon.moves.move import Moves


class Thunder(Moves):
    PARALYSIS_CHANCE = 0.3

    def __init__(self):
        """Create the Electric-type special move Thunder."""
        super().__init__(
            name="Thunder",
            move_type=Type.ELECTRIC,
            category=MoveCategory.SPECIAL,
            power=110,
            accuracy=70,
            max_pp=10,
            contact=False,
        )

    def get_accuracy(self, user, target, field=None):
        """Adjust accuracy for rain and sun when a field is available."""
        if field is None:
            return self.accuracy
        if field.weather in (Weather.RAINY, Weather.PRIMORDIAL_SEA):
            return 100
        if field.weather in (Weather.SUNNY, Weather.DESOLATE_LAND):
            return 50
        return self.accuracy

    def effect(self, user, target):
        """Try to paralyze the target with a 30% chance."""
        if Type.ELECTRIC in target.type:
            return {
                "name": self.name,
                "status": None,
                "applied": False,
                "reason": "type_immune",
            }
        if target.status_condition is not None:
            return self.inflict_paralysis(target)
        if random.random() < self.PARALYSIS_CHANCE:
            return self.inflict_paralysis(target)
        return {
            "name": self.name,
            "status": None,
            "applied": False,
            "reason": "chance_failed",
        }