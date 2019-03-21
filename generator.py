import random
import math
from creatures import Miner,Saboteur,Wizard,Snake,DwarfKing
from mine import Mine
from tribe import Tribe
from items import Treasure, Map

class MineGenerator():

    def __init__(self, width, height, args):
        self.width = width
        self.height = height
        self.args = args

    def build_mine(self, screen):

        m = Mine(screen, self.width, self.height)

        tribes = []
        tribe_width = m.width / (self.args.tribes * 2 - 1)
        for t in range(self.args.tribes):
            new_tribe = Tribe(id=t)
            new_tribe.min_x = tribe_width * new_tribe.id * 2
            new_tribe.max_x = tribe_width * (new_tribe.id*2+1)-1
            tribes.append(new_tribe)

        miner_count = int(self.args.miners) if self.args.miners is not None else random.randint(1, 200)
        for i in range(miner_count):
            tribe = random.choice(tribes)

            x = random.randint(tribe.min_x, tribe.max_x)

            miner = Miner(x, 0, tribe=tribe)
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

        snake_count = int(self.args.snakes) if self.args.snakes is not None else random.randint(1, 5)
        for i in range(snake_count):
            snake = Snake(random.randint(0, m.width - 1), random.randint(math.ceil(m.height/5), m.height - 1))
            m.add_creature(snake)

        for i in range(random.randint(1, 10)):
            treasure = Treasure(random.randint(0, m.width - 1), random.randint(10, m.height - 1))
            m.add_item(treasure)
            map_item = Map(random.randint(0, m.width - 1), random.randint(5, m.height - 1), treasure)
            m.add_item(map_item)

        for t in tribes:
            king_count = int(self.args.kings) if self.args.kings is not None else 1
            for i in range(king_count):
                x = random.randint(t.min_x, t.max_x)

                king = DwarfKing(x, 0, t)
                m.add_creature(king)

        return m