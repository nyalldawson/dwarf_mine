import math
import random
from traits import Determined
from materials import Fire

class Enchantment:
    def __init__(self):
        self.creature = None

    def place_on_creature(self, creature):
        self.creature = creature

    def remove_from_creature(self, creature):
        creature.remove_enchantment(self)

    def action(self):
        pass

    def alter_char(self, char):
        return char


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


class Firestarter(Enchantment):

    def __init__(self):
        Enchantment.__init__(self)
        self.countdown = 9*20 #multiple of 9
        self.trait = None

    def alter_char(self, char):
        return str(self.countdown / 20)

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        if not creature.has_trait(Determined):
            self.trait = Determined()
            creature.add_trait(self.trait)
        creature.color = 197

    def action(self):
        Enchantment.action(self)
        self.countdown -= 1
        if self.countdown < 0:
            self.creature.mine.create_cave(self.creature.x, self.creature.y, random.randint(3,5))
            self.creature.look()
            self.creature.mine.set_material(self.creature.x,self.creature.y,Fire())


    def remove_from_creature(self, creature):
        Enchantment.remove_from_creature(self, creature)
        creature.remove_trait(self.trait)