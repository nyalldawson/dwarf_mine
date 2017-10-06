import random
import math
from creatures import Miner,Saboteur,Wizard
from mine import Mine
from items import Treasure, Map

class MineGenerator():

    def __init__(self, width, height, args):
        self.width = width
        self.height = height
        self.args = args

    def build_mine(self, screen):

        m = Mine(screen, self.width, self.height)

        miner_count = int(self.args.miners) if self.args.miners is not None else random.randint(1, 200)
        for i in range(miner_count):
            miner = Miner(random.randint(0, m.width - 1), 0)
            m.add_creature(miner)

        for i in range(random.randint(4, 10)):
            hole_size = random.randint(4, 8)
            m.create_cave(random.randint(0, m.width - 1), random.randint(0, m.height - 1), hole_size)

        for i in range(random.randint(1, 3)):
            saboteur = Saboteur(random.randint(0, m.width - 1), int(m.height / 2))
            m.add_creature(saboteur)

        wizard_count = int(self.args.wizards) if self.args.wizards is not None else random.randint(1, 5)
        for i in range(wizard_count):
            wizard = Wizard(random.randint(0, m.width - 1), random.randint(math.ceil(m.height/3), m.height - 1))
            m.add_creature(wizard)

        for i in range(random.randint(1, 10)):
            treasure = Treasure(random.randint(0, m.width - 1), random.randint(10, m.height - 1))
            m.add_item(treasure)
            map_item = Map(random.randint(0, m.width - 1), random.randint(5, m.height - 1), treasure)
            m.add_item(map_item)

        return m