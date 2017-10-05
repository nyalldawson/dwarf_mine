import math
import random
from traits import Determined
from materials import Fire
from actions import SleepAction

class Enchantment:
    def __init__(self):
        self.creature = None
        self.time = None

    def place_on_creature(self, creature):
        self.creature = creature

    def remove_from_creature(self, creature):
        creature.remove_enchantment(self)

    def action(self):
        if self.time is not None:
            self.time -= 1
            if self.time < 0:
                self.remove_from_creature(self.creature)

    def alter_char(self, char):
        return char

    def alter_color(self):
        return None

    def affect_visibility(self, visible):
        return visible

    def affect_move_to(self, x, y):
        # return None to block movement
        return (x,y)

class Tricked(Enchantment):
    def __init__(self):
        Enchantment.__init__(self)
        self.time = 100

    def alter_color(self):
        return (135,3)

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        self.time = 1000


class SaboteurSpell(Tricked):
    def __init__(self):
        Tricked.__init__(self)
        self.time = math.inf

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)


class DeterminationSpell(Enchantment):
    def __init__(self):
        Enchantment.__init__(self)
        self.trait = None

    def alter_color(self):
        return (230,1)

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        if not creature.has_trait(Determined):
            self.trait = Determined()
            creature.add_trait(self.trait)
            self.time = 300

    def remove_from_creature(self, creature):
        Enchantment.remove_from_creature(self, creature)
        creature.remove_trait(self.trait)


class Firestarter(Enchantment):

    def __init__(self):
        Enchantment.__init__(self)
        self.countdown = 9*20 #multiple of 9
        self.trait = None

    def alter_color(self):
        return (197,10)

    def alter_char(self, char):
        return str(self.countdown / 20)

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)
        if not creature.has_trait(Determined):
            self.trait = Determined()
            creature.add_trait(self.trait)

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


class Invisibility(Enchantment):

    def __init__(self):
        Enchantment.__init__(self)

    def alter_color(self):
        return (237,9)

    def affect_visibility(self, visible):
        return False


class Frozen(Enchantment):

    def __init__(self):
        super().__init__()
        self.time = 150

    def alter_color(self):
        return (527,9)

    def affect_move_to(self, x, y):
        return None


class SleepSpell(Enchantment):

    def __init__(self):
        super().__init__()
        self.sleep_action = None

    def alter_color(self):
        return (42,9)

    def place_on_creature(self, creature):
        super().place_on_creature(creature)
        self.sleep_action=SleepAction()
        self.creature.push_action(self.sleep_action)
        self.time=self.sleep_action.duration


