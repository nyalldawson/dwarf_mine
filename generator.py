import random
import math
from creatures import Miner, Saboteur, Wizard, Snake, DwarfKing
from mine import Mine
from tribe import TRIBE_CLASSES, Tribe
from items import Treasure, Map
from actions import ExploreAction
from traits import Contagious

COLORS = [(206, 0), (209, 0), (154, 0), (142, 0), (221, 0), (249, 0)]
KING_COLORS = [(212, 0), (216, 0), (124, 0), (184, 0), (222, 0), (253, 0)]
NAMES = ['Pink', 'Orange', 'Blue', 'Purple', 'Yellow', 'White']


class MineGenerator():

    def __init__(self, width, height, args):
        self.width = width
        self.height = height
        self.args = args

    def build_mine(self, screen, pad):

        m = Mine(screen, pad, self.width, self.height)

        tribe_population = self.args.miners or random.randint(1, 30)

        tribe_width = int(m.width / (self.args.tribes * 2 - 1))
        for t in range(self.args.tribes):
            new_tribe = random.choice(TRIBE_CLASSES)(t)

            new_tribe.min_x = tribe_width * new_tribe.id * 2
            new_tribe.max_x = tribe_width * (new_tribe.id * 2 + 1) - 1
            new_tribe.color = COLORS[t]
            new_tribe.leader_color = KING_COLORS[t]
            new_tribe.name = (NAMES[t] + ' ' + new_tribe.name).strip()
            m.tribes.append(new_tribe)

            creatures = new_tribe.populate(tribe_population)
            for c in creatures:
                m.add_creature(c)

        #for i in range(miner_count):
        #    tribe = random.choice(m.tribes)
        #    x = random.randint(tribe.min_x, tribe.max_x)

        #    creature = tribe.create_creature(x=x, y=0, tribe=tribe)
        #    m.add_creature(creature)

        for i in range(random.randint(4, 10)):
            hole_size = random.randint(4, 8)
            m.create_cave(random.randint(0, m.width - 1), random.randint(0, m.height - 1), hole_size)

        outcast_tribe = Tribe(-1)
        outcast_tribe.name = 'Outcast'
        saboteur_count = self.args.saboteurs or random.randint(1, 3)
        for i in range(saboteur_count):
            saboteur = Saboteur(random.randint(0, m.width - 1), int(m.height / 2), tribe=outcast_tribe)
            m.add_creature(saboteur)

        wizard_count = self.args.wizards or random.randint(1, 5)
        for i in range(wizard_count):
            wizard = Wizard(random.randint(0, m.width - 1), random.randint(math.ceil(m.height / 3), m.height - 1))
            m.add_creature(wizard)

     #   def make_explore_action():
     #       return ExploreAction()

      #snake_count = self.args.snakes or random.randint(1, 5)
      #for i in range(snake_count):
      #    tribe = random.choice([t for t in m.tribes if Snake in t.creatures])
      #    x = random.randint(tribe.min_x, tribe.max_x)
      #    snake = Snake(x, 0, tribe=tribe)

      #    snake.default_action = make_explore_action
      #    snake.push_action(ExploreAction())
      #    if snake.has_trait(Contagious):
      #        snake.color = KING_COLORS[tribe.id]
      #    else:
      #        snake.color = tribe.color

#     #     snake = Snake(random.randint(0, m.width - 1), random.randint(math.ceil(m.height / 5), m.height - 1))
      #    m.add_creature(snake)

        treasure_count = self.args.treasures or random.randint(1, 10)
        for i in range(treasure_count):
            treasure = Treasure(random.randint(0, m.width - 1), random.randint(10, m.height - 1))
            m.add_item(treasure)
            map_item = Map(random.randint(0, m.width - 1), random.randint(5, m.height - 1), treasure)
            m.add_item(map_item)

      #  for t in m.tribes:
      #      king_count = int(self.args.kings) if self.args.kings is not None else 1
      #      for i in range(king_count):
      #          x = random.randint(t.min_x, t.max_x)
#
      #          king = DwarfKing(x, 0, t)
      #          king.color = KING_COLORS[t.id]
      #          m.add_creature(king)
#
        return m
