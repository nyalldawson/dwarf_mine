import math
from traits import Determined

class Enchantment:
    def __init__(self):
        self.creature = None

    def place_on_creature(self, creature):
        self.creature = creature

    def remove_from_creature(self, creature):
        creature.remove_enchantment(self)

    def action(self):
        pass


class Tricked(Enchantment):
    def __init__(self):
        Enchantment.__init__(self)
        self.time = 100

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        creature.color = 135
        self.time = 1000

    def action(self):
        Enchantment.action(self)
        self.time -= 1
        if self.time < 0:
            self.remove_from_creature(self.creature)


class SaboteurSpell(Tricked):
    def __init__(self):
        Tricked.__init__(self)
        self.time = math.inf

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)


class DeterminationSpell(Enchantment):
    def __init__(self):
        Enchantment.__init__(self)
        self.time = 0
        self.trait = None

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        if not creature.has_trait(Determined):
            Enchantment.place_on_creature(self, creature)
            self.trait = Determined()
            creature.add_trait(self.trait)
            creature.color = 230
            self.time = 300

    def action(self):
        Enchantment.action(self)
        self.time -= 1
        if self.time < 0:
            self.remove_from_creature(self.creature)

    def remove_from_creature(self, creature):
        Enchantment.remove_from_creature(self, creature)
        creature.remove_trait(self.trait)