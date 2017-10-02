import random
from creatures import Miner,Saboteur,Wizard
from mine import Mine
from items import Treasure, Map

class MineGenerator():

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def build_mine(self, screen):

        m = Mine(screen, self.width, self.height)
        for i in range(random.randint(1, 200)):
            miner = Miner(random.randint(0, m.width - 1), 0)
            m.add_creature(miner)

        for i in range(random.randint(4, 10)):
            hole_size = random.randint(4, 8)
            m.create_cave(random.randint(0, m.width - 1), random.randint(0, m.height - 1), hole_size)

        for i in range(random.randint(1, 3)):
            saboteur = Saboteur(random.randint(0, m.width - 1), int(m.height / 2))
            m.add_creature(saboteur)

        for i in range(random.randint(1, 5)):
            wizard = Wizard(random.randint(0, m.width - 1), random.randint(int(m.height / 2), m.height - 1))
            m.add_creature(wizard)

        for i in range(random.randint(1, 10)):
            treasure = Treasure(random.randint(0, m.width - 1), random.randint(10, m.height - 1))
            m.add_item(treasure)

        for i in range(random.randint(1, 10)):
            map_item = Map(random.randint(0, m.width - 1), random.randint(5, m.height - 1))
            m.add_item(map_item)
        return m