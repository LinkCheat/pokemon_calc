try:
    from enums.move_category import MoveCategory
    from enums.type import Type
    from moves.move import Moves
except ModuleNotFoundError:
    from calculatrice_pokemon.enums.move_category import MoveCategory
    from calculatrice_pokemon.enums.type import Type
    from calculatrice_pokemon.moves.move import Moves


class MagnetRise(Moves):
    DURATION = 5

    def __init__(self):
        """Create the Electric-type status move Magnet Rise."""
        super().__init__(
            name="Magnet Rise",
            move_type=Type.ELECTRIC,
            category=MoveCategory.STATUS,
            accuracy=101,
            max_pp=10,
            contact=False,
        )

    def targets_user(self):
        return True

    def fails_before_damage(self, user, target, field):
        """Fail early if Magnet Rise is already active on the user."""
        return user.magnet_rise_turns_remaining > 0

    def effect(self, user, target):
        """Grant the user temporary immunity to Ground-type targeting."""
        if user.magnet_rise_turns_remaining > 0:
            return {
                "name": self.name,
                "condition": "magnet_rise",
                "applied": False,
                "reason": "already_active",
            }

        user.magnet_rise_turns_remaining = self.DURATION
        return {
            "name": self.name,
            "condition": "magnet_rise",
            "applied": True,
            "turns": self.DURATION,
        }

    def apply_effect_with_field(self, user, target, damage_dealt, field):
        """Reject Magnet Rise when Gravity or Ingrain keeps the user grounded."""
        if field.gravity_active:
            return {
                "name": self.name,
                "condition": "magnet_rise",
                "applied": False,
                "reason": "gravity_active",
                "failed": True,
            }
        if user.ingrain_active:
            return {
                "name": self.name,
                "condition": "magnet_rise",
                "applied": False,
                "reason": "ingrain_active",
                "failed": True,
            }
        return self.effect(user, target)