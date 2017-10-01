import random
import curses
import sys
import math


class Material:
    def __init__(self):
        self.char = None
        self.color = 17
        self.x = None
        self.y = None
        self.mine = None
        self.toughness = None

    def action(self):
        pass


class Space(Material):
    def __init__(self):
        Material.__init__(self)
        self.char = '█'
        self.toughness = 0


class Dirt(Material):
    def __init__(self):
        Material.__init__(self)
        self.char = '░'
        dirt_colors = [95]
        self.color = dirt_colors[random.randint(0, len(dirt_colors) - 1)]
        self.toughness = 1


class Rock(Material):
    def __init__(self):
        Material.__init__(self)
        self.char = 'O'
        self.color = 60
        self.toughness = 10


class Lava(Material):
    def __init__(self):
        Material.__init__(self)
        self.char = '#'
        lava_color = [10, 161, 125]
        self.color = lava_color[random.randint(0, len(lava_color) - 1)]
        self.temperature = random.randint(2000, 100000)

    def action(self):
        # check adjacent cells
        x_neighbors = []
        if self.x > 0:
            x_neighbors.append(self.x - 1)
        x_neighbors.append(self.x)
        if self.x < self.mine.width - 1:
            x_neighbors.append(self.x + 1)
        y_neighbors = []
        if self.y > 0:
            y_neighbors.append(self.y - 1)
        y_neighbors.append(self.y)
        if self.y < self.mine.height - 1:
            y_neighbors.append(self.y + 1)

        for y in y_neighbors:
            for x in x_neighbors:
                if x == self.x and y == self.y:
                    continue
                if x != self.x and y != self.y:
                    # no diagonals
                    continue
                if self.temperature < 100:
                    break

                if self.mine.is_empty(x, y):
                    lava = Lava()
                    self.temperature *= 0.9
                    lava.temperature = self.temperature
                    self.mine.set_material(x, y, lava)
                material = self.mine.material(x, y)
                if isinstance(material, Lava):
                    t = self.temperature * 0.9999 + material.temperature * 0.0001
                    material.temperature = self.temperature * 0.0001 + material.temperature * 0.9999
                    self.temperature = t

                item = self.mine.get_creature(x, y)
                if isinstance(item, Creature):
                    item.die()

        self.temperature -= 1
        if self.temperature < 100:
            self.mine.set_material(self.x, self.y, Rock())


class Utils:
    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.ceil(math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)))

    @staticmethod
    def line_between(x1, y1, x2, y2):
        dx = x2 - x1
        dy = y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        if dist == 0:
            return []
        step_dx = dx / dist
        step_dy = dy / dist
        steps = int(math.ceil(dist))
        return [(x1 + round(step_dx * i), y1 + round(step_dy * i)) for i in range(1, steps)]


class Mine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.mine = []
        self.visibility = []
        self.colors = []
        self.build_mine()
        self.creatures = []
        self.items = []
        self.dark = True

    def build_mine(self):
        for l in range(self.height):
            self.mine.append([None] * self.width)

        self.visibility = [False] * (self.width * self.height)

        for y in range(self.height):
            for x in range(self.width):
                self.set_material(x, y, Dirt())

        for l in range(random.randint(1, 5)):
            lava_size = random.randint(5, 20)
            lava_start = random.randint(1, self.width - lava_size - 1)

            lava_y_start = random.randint(self.height - 5, self.height - 1)
            lava_y_end = self.height

            for y in range(lava_y_start, lava_y_end):
                for i in range(lava_start, lava_start + lava_size):
                    self.set_material(i, y, Lava())

    def set_material(self, x, y, material):
        self.mine[y][x] = material
        material.x = x
        material.y = y
        material.mine = self

    def add_creature(self, creature):
        self.creatures.append(creature)
        creature.place_in_mine(self)
        self.set_material(creature.x, creature.y, Space())

    def remove_creature(self, creature):
        self.creatures.remove(creature)

    def add_item(self, item):
        self.items.append(item)
        item.add_to_mine(self)
        self.set_material(item.x, item.y, Space())

    def set_visibility(self, x, y, visibility):
        self.visibility[y * self.width + x] = visibility

    def is_empty(self, x, y):
        return isinstance(self.mine[y][x], Space)

    def is_valid_location(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def is_visible_from(self, x1, y1, x2, y2):
        line = Utils.line_between(x1, y1, x2, y2)
        for pt in line:
            if not self.is_empty(pt[0], pt[1]):
                return False

            for m in self.creatures:
                if m.x == pt[0] and m.y == pt[1]:
                    return False

        return True

    def get_visible_cells(self, x, y, max_dist):
        cells = []

        for cx in range(x - max_dist, x + max_dist + 1):
            if cx < 0 or cx >= self.width:
                continue
            for cy in range(y - max_dist, y + max_dist + 1):
                if cy < 0 or cy >= self.height:
                    continue
                elif Utils.distance(x, y, cx, cy) > max_dist:
                    continue
                elif not self.is_visible_from(x, y, cx, cy):
                    continue
                else:
                    cells.append((cx, cy))

        return cells

    def get_creature(self, x, y):
        for m in self.creatures:
            if m.x == x and m.y == y:
                return m
        return None

    def get_item(self, x, y):
        for m in self.items:
            if m.x == x and m.y == y:
                return m
        return None

    def material(self, x, y):
        try:
            return self.mine[y][x]
        except:
            assert False, str(x) + ',' + str(y)

    def create_cave(self, center_x, center_y, hole_size):
        for x in range(center_x - hole_size, center_x + hole_size + 1):
            if x < 0 or x >= self.width:
                continue
            for y in range(center_y - hole_size, center_y + hole_size + 1):
                if y < 0 or y >= self.height:
                    continue
                if Utils.distance(center_x, center_y, x, y) <= hole_size:
                    self.set_material(x, y, Space())

    def action(self):
        for level in self.mine:
            for cell in level:
                cell.action()

        for m in self.creatures:
            m.move()
            for i in self.items:
                if m.x == i.x and m.y == i.y:
                    self.items.remove(i)
                    m.add_item(i)

        self.print_current_level()

        if len([i for i in self.items if isinstance(i, Treasure)]) == 0:
            for i in range(2):
                print('Dwarves won!!')
            sys.exit()

    def print_current_level(self):
        current_state = []
        current_colors = []
        for l in self.mine:
            current_state.append([s.char for s in l])
            current_colors.append([s.color for s in l])

        for m in self.creatures:
            current_state[m.y][m.x] = m.char
            current_colors[m.y][m.x] = m.color

        for i in self.items:
            current_state[i.y][i.x] = i.char
            current_colors[i.y][i.x] = i.color

        for y in range(self.height):
            for x in range(self.width):
                if not self.dark or self.visibility[self.width * y + x]:
                    stdscr.addstr(y, x, current_state[y][x], curses.color_pair(current_colors[y][x]))
                else:
                    stdscr.addstr(y, x, ' ')

        stdscr.refresh()


class Enchantment:
    def __init__(self):
        self.creature = None

    def place_on_creature(self, creature):
        self.creature = creature

    def remove_from_creature(self, creature):
        pass

    def action(self):
        pass


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

    def remove_from_creature(self, creature):
        creature.color = creature.original_color
        creature.remove_enchantment(self)


class SaboteurSpell(Tricked):
    def __init__(self):
        Tricked.__init__(self)
        self.time = math.inf

    def place_on_creature(self, creature):
        Enchantment.place_on_creature(self, creature)


class Action:
    def __init__(self):
        self.creature = None

    def added_to_creature(self, creature):
        self.creature = creature

    def do(self):
        pass


class SleepAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.duration = random.randint(100, 300)
        self.original_char = None

    def added_to_creature(self, creature):
        Action.added_to_creature(self, creature)
        self.original_char = creature.char
        creature.char = 'Z'

    def do(self):
        self.duration -= 1
        if self.duration == 0:
            self.creature.char = self.original_char
            self.creature.remove_action(self)


class GoToAction(Action):
    def __init__(self, x, y):
        Action.__init__(self)
        self.x = x
        self.y = y

    def do(self):
        if self.creature.x == self.x and self.creature.y == self.y:
            self.creature.remove_action(self)

        new_x = self.creature.x
        new_y = self.creature.y
        if self.creature.x < self.x:
            new_x += 1
        elif self.creature.x > self.x:
            new_x -= 1

        def try_to_move_to(x, y):
            if not self.creature.mine.is_valid_location(x, y):
                return False
            elif not self.creature.can_move(x, y):
                return False
            elif self.creature.mine.is_empty(x, y):
                self.creature.move_to(x, y)
                return True
            elif self.creature.decided_to_dig(x, y):
                self.creature.move_to(x, y)
                self.creature.mine.set_material(x, y, Space())
                return True
            else:
                return False

        if not new_x == self.creature.x:
            if try_to_move_to(new_x, new_y):
                return
            else:
                new_x = self.creature.x

        if self.creature.y < self.y:
            new_y += 1
        elif self.creature.y > self.y:
            new_y -= 1

        if not new_y == self.creature.y:
            if try_to_move_to(new_x, new_y):
                return

        return


class ExploreAction(Action):
    def __init__(self):
        Action.__init__(self)
        self.x_dir = 0
        self.xx_dir = 1
        self.y_dir = 1
        self.yy_dir = 1
        self.frustration = 0

    def think_about_changing_vertical_direction(self):
        if self.creature.y == 0:
            self.yy_dir = 1
            self.y_dir = 1
            return
        if self.creature.y == self.creature.mine.height - 1:
            self.yy_dir = -1
            self.y_dir = -1
            return

        if random.randint(1, 1000) < self.frustration:
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
        if self.creature.x == 0:
            self.xx_dir = 1
            self.x_dir = 1
            return
        if self.creature.x == self.creature.mine.width - 1:
            self.xx_dir = -1
            self.x_dir = -1
            return

        if random.randint(1, 1000) < self.frustration:
            self.xx_dir *= -1
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir, 1), -1)
            self.frustration *= 0.5
            return

        if random.randint(1, 1000) == 1:
            self.x_dir += self.xx_dir
            self.x_dir = max(min(self.x_dir, 1), -1)

        # 'general' direction trend is hard to change
        if random.randint(1, 10000) == 1:
            self.xx_dir *= -1

    def do(self):
        new_x = self.creature.x
        new_y = self.creature.y

        self.think_about_changing_vertical_direction()
        self.think_about_changing_horizontal_direction()

        changed_level = False
        if not changed_level and random.randint(1, 2) == 1:
            new_x += self.x_dir
            changed_level = True

        if not changed_level and random.randint(1, 2) == 1:
            new_y += self.y_dir

        if new_x == self.creature.x and new_y == self.creature.y:
            return

        if not self.creature.mine.is_valid_location(new_x, new_y):
            self.frustration += 1
            return

        if not self.creature.can_move(new_x, new_y):
            self.frustration += 1
            return

        if self.creature.mine.is_empty(new_x, new_y):
            self.creature.move_to(new_x, new_y)
            self.frustration = 0

        else:
            # reluctant to dig
            if self.creature.decided_to_dig(new_x, new_y):
                self.creature.move_to(new_x, new_y)
                self.creature.mine.set_material(new_x, new_y, Space())
                self.frustration = 0
            else:
                self.frustration += 1


class Creature:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = '☺'
        self.mine = None
        self.color = 206
        self.original_color = 206
        self.enchantments = []
        self.view_distance = 0
        self.actions = []
        self.items = []

    def place_in_mine(self, mine):
        self.mine = mine
        self.look()

    def push_action(self, action):
        self.actions.insert(0, action)
        action.added_to_creature(self)

    def remove_action(self, action):
        self.actions.remove(action)

    def add_item(self, item):
        self.items.append(item)

    def die(self):
        self.mine.remove_creature(self)

    def has_enchantment(self, enchantment):
        for e in self.enchantments:
            if isinstance(e, enchantment):
                return True
        return False

    def enchant(self, enchantment):
        self.enchantments.append(enchantment)
        enchantment.place_on_creature(self)

    def remove_enchantment(self, enchantment):
        self.enchantments.remove(enchantment)

    def move(self):
        self.look()
        for e in self.enchantments:
            e.action()

        if len(self.actions) > 0:
            self.actions[0].do()

    def look_at(self, x, y):
        pass

    def look(self):
        visible_cells = self.mine.get_visible_cells(self.x, self.y, self.view_distance)
        for c in visible_cells:
            if self.x == c[0] and self.y == c[1]:
                continue
            self.look_at(c[0], c[1])


class Wizard(Creature):
    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.color = 11
        self.view_distance = 5

    def place_in_mine(self, mine):
        Creature.place_in_mine(self, mine)
        hole_size = random.randint(2, 6)
        mine.create_cave(self.x, self.y, hole_size)

    def look_at(self, x, y):
        creature = self.mine.get_creature(x, y)
        if isinstance(creature, Miner):
            # put a spell on him, if he doesn't have one already
            if not creature.has_enchantment(Tricked):
                creature.enchant(Tricked())


class Miner(Creature):
    def __init__(self, x, y):
        Creature.__init__(self, x, y)
        self.likes_to_go_vertical = random.randint(10, 20)
        self.likes_to_go_horizontal = random.randint(10, 20)
        self.view_distance = 5
        self.push_action(ExploreAction())

    def place_in_mine(self, mine):
        Creature.place_in_mine(self, mine)
        mine.set_visibility(self.x, self.y, True)

    def can_move(self, x, y):
        for m in self.mine.creatures:
            if m == self:
                continue
            if m.x == x and m.y == y:
                return False
        return True

    def decided_to_dig(self, x, y):
        if self.has_enchantment(Tricked):
            # he's motivated!
            return random.randint(1, 10) == 1

        toughness = self.mine.material(x, y).toughness
        if not toughness:
            return False

        return random.randint(1, toughness * (
            self.likes_to_go_horizontal * abs(self.x - x) + abs(self.y - y) * self.likes_to_go_vertical)) == 1

    def moved_from(self, x, y):
        if self.has_enchantment(Tricked):
            if random.randint(1, 5) == 1:
                self.mine.set_material(x, y, Rock())

    def move(self):
        if random.randint(1, 1000) == 1:
            self.push_action(SleepAction())

        Creature.move(self)

    def move_to(self, x, y):
        old_x = self.x
        old_y = self.y
        self.x = x
        self.y = y

        visible_cells = self.mine.get_visible_cells(x, y, self.view_distance)
        for c in visible_cells:
            self.mine.set_visibility(c[0], c[1], True)

        self.moved_from(old_x, old_y)

    def look_at(self, x, y):
        self.mine.set_visibility(x, y, True)

        item = self.mine.get_item(x, y)
        if item is not None:
            if item.is_attractive_to(self):
                self.push_action(GoToAction(x, y))


class Saboteur(Miner):
    def __init__(self, x, y):
        Miner.__init__(self, x, y)
        self.char = '☺'
        self.color = 2
        self.original_color = self.color
        self.enchant(SaboteurSpell())


class Item:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.char = 'X'
        self.color = 1
        self.mine = None

    def add_to_mine(self, mine):
        self.mine = mine

    def is_attractive_to(self, creature):
        return False


class Treasure(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = '☼'
        self.color = 12

    def add_to_mine(self, mine):
        Item.add_to_mine(self, mine)
        mine.set_visibility(self.x, self.y, True)
        hole_size = random.randint(2, 4)
        mine.create_cave(self.x, self.y, hole_size)

    def is_attractive_to(self, creature):
        if isinstance(creature, Miner):
            return True

        return False


class Map(Item):
    def __init__(self, x, y):
        Item.__init__(self, x, y)
        self.char = 'M'
        self.color = 181

    def add_to_mine(self, mine):
        Item.add_to_mine(self, mine)
        hole_size = random.randint(4, 8)
        mine.create_cave(self.x, self.y, hole_size)
        mine.set_visibility(self.x, self.y, True)

    def is_attractive_to(self, creature):
        if isinstance(creature, Miner):
            return True

        return False



if False:
    stdscr = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    x = 0
    y = 0
    for i in range(1000):
        x += 4
        if x > 180:
            y += 1
            x = 0
        stdscr.addstr(y, x, str(i), curses.color_pair(i))

    stdscr.refresh()
elif True:

    stdscr = curses.initscr()
    height, width = stdscr.getmaxyx()

    m = Mine(width-1, height-1)
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


    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    while True:
        m.action()
