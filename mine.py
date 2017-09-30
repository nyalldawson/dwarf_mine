import random
import time
import curses
import sys
import copy
import math

stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()
for i in range(0, curses.COLORS):
    curses.init_pair(i + 1, i, -1)

class Material():

    def __init__(self):
        self.char = None
        self.color = curses.color_pair(17)
        self.x = None
        self.y = None
        self.mine = None
        self.toughness = None

    def action(self):
        pass

class Space(Material):

    def __init__(self):
        Material.__init__(self)
        self.char = ' '
        self.toughness = 0

class Dirt(Material):

    def __init__(self):
        Material.__init__(self)
        self.char = '.'
        dirt_colors=[curses.color_pair(60)]
        self.color = dirt_colors[random.randint(0,len(dirt_colors)-1)]
        self.toughness = 1


class Rock(Material):

    def __init__(self):
        Material.__init__(self)
        self.char = 'O'
        self.color = curses.color_pair(60)
        self.toughness = 10


class Lava(Material):

    def __init__(self):
        Material.__init__(self)
        self.char = '#'
        self.color = curses.color_pair(10)
        self.temperature = random.randint(2000,100000)


    def action(self):
        # check adjacent cells
        x_neighbors = []
        if self.x > 0:
            x_neighbors.append(self.x-1)
        x_neighbors.append(self.x)
        if self.x < self.mine.width-1:
            x_neighbors.append(self.x+1)
        y_neighbors = []
        if self.y > 0:
            y_neighbors.append(self.y-1)
        y_neighbors.append(self.y)
        if self.y < self.mine.height-1:
            y_neighbors.append(self.y+1)

        for y in y_neighbors:
            for x in x_neighbors:
                if x == self.x and y == self.y:
                    continue
                if self.temperature < 100:
                    break

                if self.mine.is_empty(x,y):
                    lava = Lava()
                    self.temperature *= 0.9
                    lava.temperature = self.temperature
                    self.mine.set_material(x,y,lava)
                material = self.mine.material(x,y)
                if isinstance(material,Lava):
                    t = self.temperature * 0.9999 + material.temperature * 0.0001
                    material.temperature = self.temperature * 0.0001 + material.temperature * 0.9999
                    self.temperature = t

                item = self.mine.item(x,y)
                if isinstance(item,Creature):
                    item.die()


        self.temperature -= 1
        if self.temperature < 100:
            self.mine.set_material(self.x,self.y,Rock())

class Utils():

    @staticmethod
    def distance(x1,y1,x2,y2):
        return math.ceil(math.sqrt((x2-x1)*(x2-x1) + (y2-y1)*(y2-y1)))


class Mine():

    def __init__(self):
        self.width = 210
        self.height = 51
        self.mine = []
        self.colors = []
        self.build_mine()
        self.creatures = []
        self.treasures = []

    def build_mine(self):
        for l in range(self.height):
            self.mine.append([None] * self.width)

        for y in range(self.height):
            for x in range(self.width):
                self.set_material(x,y,Dirt())

        for l in range(random.randint(1,5)):
            lava_size = random.randint(5, 20)
            lava_start = random.randint(1,self.width - lava_size-1)

            lava_y_start = random.randint(self.height-5,self.height-1)
            lava_y_end = self.height

            for y in range(lava_y_start,lava_y_end):
                for i in range(lava_start, lava_start+lava_size):
                    self.set_material(i,y,Lava())

    def set_material(self, x, y, material):
        self.mine[y][x] = material
        material.x = x
        material.y = y
        material.mine = self

    def add_creature(self, creature):
        self.creatures.append(creature)
        creature.place_in_mine(self)

    def remove_creature(self, creature):
        self.creatures.remove(creature)

    def add_treasure(self, treasure):
        self.treasures.append(treasure)

    def is_empty(self, x, y):
        return isinstance(self.mine[y][x], Space)

    def is_valid_location(self, x, y):
        return x >= 0 and x < self.width and y >=0 and y < self.height

    def item(self,x,y):
        for m in self.creatures:
            if m.x == x and m.y == y:
                return m
        return None

    def material(self,x,y):
        try:
            return self.mine[y][x]
        except:
            assert False, str(x)+','+str(y)

    def action(self):
        for level in self.mine:
            for cell in level:
                cell.action()

        for m in self.creatures:
            m.move()
            for t in self.treasures:
                if m.x == t.x and m.y == t.y:
                    self.treasures.remove(t)

        self.print_current_level()

        if len(self.treasures) == 0:
            for i in range(2):
                print('Dwarves won!!')
            sys.exit()


    def print_current_level(self):
        current_state = []
        current_colors = []
        for l in self.mine:
            current_state.append([s.char for s in l])
            current_colors.append([s.color for s in l])

        for t in self.treasures:
            current_state[t.y][t.x] = t.char
            current_colors[t.y][t.x] = t.color

        for m in self.creatures:
            current_state[m.y][m.x] = m.char
            current_colors[m.y][m.x] = m.color

        for y in range(self.height):
            for x in range(self.width):
                stdscr.addstr(y, x, current_state[y][x], current_colors[y][x])
        stdscr.refresh()

class Creature():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '☺'
        self.mine = None
        self.color = curses.color_pair(4)

    def place_in_mine(self, mine):
        self.mine = mine

    def die(self):
        self.mine.remove_creature(self)


class Wizard(Creature):

    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.color = curses.color_pair(11)

    def place_in_mine(self, mine):
        Creature.place_in_mine(self, mine)
        hole_size = random.randint(2,6)
        for x in range(self.x-hole_size,self.x+hole_size+1):
            if x < 0 or x >= self.mine.width:
                continue
            for y in range(self.y-hole_size,self.y+hole_size+1):
                if y < 0 or y >= self.mine.height:
                    continue
                if Utils.distance(self.x,self.y,x,y) <= hole_size:
                    self.mine.set_material(x,y,Space())

    def move(self):
        pass


class Miner(Creature):

    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.x_dir = 0
        self.xx_dir = 1
        self.y_dir = 1
        self.yy_dir = 1
        self.frustration = 0
        self.likes_to_go_vertical = random.randint(10,20)
        self.likes_to_go_horizontal = random.randint(10,20)

    def can_move(self,x ,y):
        for m in self.mine.creatures:
            if m == self:
                continue
            if m.x == x and m.y == y:
                return False
        return True

    def think_about_changing_vertical_direction(self):
        if self.y == 0:
            self.yy_dir = 1
            self.y_dir = 1
            return
        if self.y == self.mine.height-1:
            self.yy_dir = -1
            self.y_dir = -1
            return

        if random.randint(1,1000) < self.frustration :
            self.yy_dir *= -1
            self.y_dir += self.yy_dir
            self.y_dir = max(min(self.y_dir, 1), -1)
            self.frustration *= 0.5
            return

        if random.randint(1, 1000) == 1:
            self.y_dir += self.yy_dir
            self.y_dir = max(min(self.y_dir, 1), -1)

        # 'general' direction trend is hard to change
        if random.randint(1, 10000) == 1:
            self.yy_dir *= -1

    def think_about_changing_horizontal_direction(self):
        if self.x == 0:
            self.xx_dir = 1
            self.x_dir = 1
            return
        if self.x == self.mine.width-1:
            self.xx_dir = -1
            self.x_dir = -1
            return

        if random.randint(1,1000) < self.frustration:
            self.xx_dir *= -1
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir, 1), -1)
            self.frustration *= 0.5
            return

        if random.randint(1, 1000) == 1:
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir,1),-1)

        # 'general' direction trend is hard to change
        if random.randint(1,10000) == 1:
            self.xx_dir *= -1


    def decided_to_dig(self, x, y):
        toughness = self.mine.material(x, y).toughness
        if not toughness:
            return False
#        assert toughness==1, toughness
        return random.randint(1, toughness*(self.likes_to_go_horizontal*abs(self.x-x) + abs(self.y-y)*self.likes_to_go_vertical)) == 1

    def move(self):
        new_x = self.x
        new_y = self.y

        self.think_about_changing_vertical_direction()
        self.think_about_changing_horizontal_direction()


        if random.randint(1, 2) == 1:
            new_y = new_y + self.y_dir
            # after changing level, more likely to change horizontal direction
            for i in range(5):
                self.think_about_changing_horizontal_direction()

        if random.randint(1, 2) == 1:
            new_x += self.x_dir

        if new_x == self.x and new_y == self.y:
            return

        if not self.mine.is_valid_location(new_x, new_y):
            self.frustration += 1
            return

        if not self.can_move(new_x,new_y):
            self.frustration += 1
            return

        if self.mine.is_empty(new_x, new_y):
            self.x = new_x
            self.y = new_y
            self.frustration = 0

        else:
            # reluctant to dig
            if self.decided_to_dig(new_x,new_y):
                self.x = new_x
                self.y = new_y
                self.mine.mine[self.y][self.x] = Space()
                self.frustration = 0
            else:
                self.frustration += 1



class Saboteur(Miner):

    def __init__(self, x, y):
        Miner.__init__(self,x,y)
        self.char = '☹'
        self.color = curses.color_pair(2)

    def move(self):
        Miner.move(self)
        if random.randint(1,5) == 1:
            self.mine.mine[self.y][self.x] = Rock()

    def decided_to_dig(self, delta_x, delta_y):
        # he's motivated!
        return random.randint(1, 10) == 1


class Treasure():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '☼'
        self.color = curses.color_pair(12)


m = Mine()
for i in range(random.randint(1,20)):
    miner = Miner(random.randint(0,m.width-1),0)
    m.add_creature(miner)

for i in range(random.randint(1,3)):
    saboteur = Saboteur(random.randint(0,m.width-1),int(m.height/2))
    m.add_creature(saboteur)

for i in range(random.randint(1,3)):
    wizard = Wizard(random.randint(0,m.width-1),random.randint(int(m.height/2), m.height-1))
    m.add_creature(wizard)

for i in range(random.randint(1,10)):
    treasure = Treasure(random.randint(0,m.width-1),random.randint(10,m.height-1))
    m.add_treasure(treasure)

while True:
    m.action()
