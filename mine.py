import random
import curses
import sys

from materials import Lava, Dirt, Space
from items import Treasure, Map
from creatures import Miner, Saboteur, Wizard
from message_box import MessageBox
from utils import Utils


class Mine:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height - 1
        self.feedback_line = height - 1
        self.feedback_timer = 0
        self.mine = []
        self.visibility = []
        self.colors = []
        self.build_mine()
        self.creatures = []
        self.items = []
        self.dark = True

    def push_feedback(self, line):
        self.screen.addstr(self.feedback_line, 0, line + (' ' * (self.width - len(line))))
        self.feedback_timer = 40

    def clear_feedback(self):
        self.screen.addstr(self.feedback_line, 0, ' ' * self.width)

    def push_message(self, message):
        MessageBox(self.screen, message)

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
            self.push_message('Dwarves won!')
            sys.exit()

        if len([c for c in self.creatures if isinstance(c, Miner) and not isinstance(c, Saboteur)]) == 0:
            self.push_message('All dwarves died\n\nYou lose!')
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
                    self.screen.addstr(y, x, current_state[y][x], curses.color_pair(current_colors[y][x]))
                else:
                    self.screen.addstr(y, x, ' ')

        self.feedback_timer -= 1
        if self.feedback_timer == 0:
            self.clear_feedback()
        self.screen.refresh()


def main(screen):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    if False:

        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, 0, i)

        x = 0
        y = 0
        for i in range(1000):
            x += 4
            if x > 180:
                y += 1
                x = 0
            screen.addstr(y, x, str(i), curses.color_pair(i))

        screen.refresh()
        screen.getch()

    elif True:
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, 16)

        height, width = screen.getmaxyx()

        m = Mine(screen, width - 1, height - 1)
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

        while True:
            m.action()


if __name__ == '__main__':
    curses.wrapper(main)
