import random
from enchantments import DeterminationSpell, Invisibility
from creatures import Miner

class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = 'X'
        self.color = 1
        self.mine = None
        self.type = 'thing'

    def add_to_mine(self, mine):
        self.mine = mine

    def is_attractive_to(self, creature):
        return False

    def found_by(self, creature):
        pass

    def alter_color(self):
        return None


class Treasure(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = '☼'
        self.color = 12
        if random.randint(1, 5) == 1:
            treasures = ['magic ring', 'magic hat', 'magic glove']
            self.type = treasures[random.randint(0, len(treasures) - 1)]
            spells = [DeterminationSpell,Invisibility]
            self.spell = spells[random.randint(0, len(spells) - 1)]()
        else:
            treasures = ['crown', 'gold nugget', 'diamond', 'shiny ring', 'gold ring', 'silver ring', 'treasure chest',
                         'gold coin', 'ruby', 'shiny necklace','precious cup']
            self.type = treasures[random.randint(0, len(treasures) - 1)]
            self.spell = None

    def add_to_mine(self, mine):
        Item.add_to_mine(self, mine)
        mine.set_visibility(self.x, self.y, True)
        hole_size = random.randint(2, 4)
        mine.create_cave(self.x, self.y, hole_size)

    def is_attractive_to(self, creature):
        if isinstance(creature, Miner):
            return True

        return False

    def found_by(self, creature):
        if self.spell is not None:
            creature.enchant(self.spell)
        creature.mine.push_message('{} found a {}!'.format(creature.type, self.type))


class Map(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = 'M'
        self.color = 181
        self.type = 'map'

    def add_to_mine(self, mine):
        Item.add_to_mine(self, mine)
        hole_size = random.randint(4, 8)
        mine.create_cave(self.x, self.y, hole_size)
        mine.set_visibility(self.x, self.y, True)

    def is_attractive_to(self, creature):
        if isinstance(creature, Miner):
            return True

        return False

