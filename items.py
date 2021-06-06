import random
from item import Item
from enchantments import DeterminationSpell, Invisibility
from actions import SearchAction
from creatures import Miner
from utils import Rect
import math


class Treasure(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = '☼'
        self.color = 12
        if random.randint(1, 5) == 1:
            treasures = ['magic ring', 'magic hat', 'magic glove']
            self.type = treasures[random.randint(0, len(treasures) - 1)]
            spells = [DeterminationSpell, Invisibility]
            self.spell = spells[random.randint(0, len(spells) - 1)]()
        else:
            treasures = ['crown', 'gold nugget', 'diamond', 'shiny ring', 'gold ring', 'silver ring', 'treasure chest',
                         'gold coin', 'ruby', 'shiny necklace', 'precious cup']
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

    def found_by(self, creature: 'Creature'):
        if self.spell is not None:
            creature.enchant(self.spell)
        creature.mine.push_message(f'{creature.get_identifier()} found a {self.type}!')


class Map(Item):
    def __init__(self, x, y, target: Item):
        super().__init__(x, y)
        self.char = 'M'
        self.color = 181
        self.type = 'map'
        self.target: Item = target
        self.search_area = None

    def add_to_mine(self, mine):
        super().add_to_mine(mine)
        hole_size = random.randint(4, 8)
        mine.create_cave(self.x, self.y, hole_size)
        mine.set_visibility(self.x, self.y, True)
        self.search_area = Rect.from_center(self.target.x, self.target.y, math.ceil(self.mine.width / 6),
                                            math.ceil(self.mine.height / 6))

    def is_attractive_to(self, creature: 'Creature'):
        if isinstance(creature, Miner):
            return True

        return False

    def found_by(self, creature: 'Creature'):
        if self.target in self.mine.items:
            # target item still exists
            self.mine.push_message(f'{creature.get_identifier()} found a map for a {self.target.type}!')
            creature.push_action(SearchAction(self.target, self.search_area))
