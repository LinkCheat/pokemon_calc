from enum import Enum


class Item(Enum):
    NONE = ("", False, None)
    SITRUS_BERRY = ("Sitrus Berry", True, None)
    FIRE_GEM = ("Fire Gem", False, None)
    CHARCOAL = ("Charcoal", False, None)
    LIFE_ORB = ("Life Orb", False, None)
    VENUSAURITE = ("Venusaurite", False, ("Venusaur", "Mega Venusaur"))
    BLASTOISINITE = ("Blastoisinite", False, ("Blastoise", "Mega Blastoise"))
    CHARIZARDITE_X = ("Charizardite X", False, ("Charizard", "Mega Charizard X"))
    CHARIZARDITE_Y = ("Charizardite Y", False, ("Charizard", "Mega Charizard Y"))

    def __new__(cls, name, is_berry, mega_evolution):
        item = object.__new__(cls)
        item._value_ = name
        item._is_berry = is_berry
        item._mega_evolution = mega_evolution
        return item

    @property
    def is_berry(self):
        """Return whether this item belongs to the Berry category."""
        return self._is_berry

    @property
    def is_mega_stone(self):
        """Return whether this item is a Mega Stone."""
        return self._mega_evolution is not None

    @property
    def mega_evolution(self):
        """Return the compatible Pokémon name and Mega form, if applicable."""
        return self._mega_evolution

    @property
    def is_immune_to_item_negation(self):
        """Return whether item-negating effects leave this item unaffected."""
        return self.is_mega_stone

    @property
    def can_be_manipulated(self):
        """Return whether item-manipulating effects may give or remove this item."""
        return not self.is_mega_stone

    def __repr__(self):
        """Display the item's human-readable name."""
        return self.value
