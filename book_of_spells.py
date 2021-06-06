import random
from item import Item
from creatures import Miner
from enchantments import SleepSpell, Frozen, Firestarter


class BookOfSpells(Item):
    def  __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = 'B'
        self.color = 948
        self.type = 'Book of Spells'
        spells = [SleepSpell, Frozen, Firestarter]
        self.spell = spells[random.randint(0, len(spells) - 1)]()

    def add_to_mine(self, mine):
        Item.add_to_mine(self, mine)
        mine.set_visibility(self.x, self.y, True)
        hole_size = random.randint(2, 4)
        mine.create_cave(self.x, self.y, hole_size)

    def is_attractive_to(self, creature):
        if isinstance(creature, Miner):
            return True

        return False

    def found_by(self, creature: 'Creature'):
        if self.spell is not None:
            creature.learn(self.spell)
        creature.mine.push_message(f'{creature.get_identifier()} found a {self.type} and learnt the {self.spell.type} spell!')
