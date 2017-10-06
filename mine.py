import random
import sys
import curses

from message_box import MessageBox
from materials import Lava, Dirt, Space, Water
from utils import Utils
from items import Treasure
from creatures import Miner, Saboteur


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
        self.creatures = []
        self.items = []
        self.dark = True
        self.build_mine()

    def push_feedback(self, line):
        self.screen.addstr(self.feedback_line, 0, line + (' ' * (self.width - len(line))))
        self.feedback_timer = 40

    def clear_feedback(self):
        self.screen.addstr(self.feedback_line, 0, ' ' * self.width)

    def push_message(self, message):
        MessageBox(self.screen, message)

    def build_mine(self):
        self.mine = [Dirt()] * (self.width*self.height)
        self.visibility = [False] * (self.width * self.height)

        for l in range(random.randint(1, 5)):
            lava_size = random.randint(5, 20)
            lava_start = random.randint(1, self.width - lava_size - 1)

            lava_y_start = random.randint(self.height - 5, self.height - 1)
            lava_y_end = self.height

            for y in range(lava_y_start, lava_y_end):
                for i in range(lava_start, lava_start + lava_size):
                    self.set_material(i, y, Lava())

        for l in range(random.randint(1, 5)):
            water_size = random.randint(5, 20)
            water_start = random.randint(1, self.width - water_size - 1)

            water_y_start = random.randint(5, self.height - 1)
            water_y_end = min(self.height - 1, water_y_start + random.randint(1, 10))

            for y in range(water_y_start, water_y_end):
                for i in range(water_start, water_start + water_size):
                    self.set_material(i, y, Water())

    def set_material(self, x, y, material):
        self.mine[y * self.width + x] = material
        material.placed_in_mine(self, x,y)

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
        return isinstance(self.mine[y * self.width + x], Space)

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
            return self.mine[y * self.width + x]
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
        for cell in self.mine:
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
        current_state = [s.get_char() for s in self.mine]
        current_colors = [s.color for s in self.mine]

        for m in self.creatures:
            current_state[m.y * self.width + m.x] = m.get_char()
            current_colors[m.y * self.width + m.x] = m.get_color()

        for i in self.items:
            current_state[i.y * self.width + i.x] = i.char
            current_colors[i.y * self.width + i.x] = i.color

        for y in range(self.height):
            for x in range(self.width):
                if not self.dark or self.visibility[self.width * y + x]:
                    self.screen.addstr(y, x, current_state[y * self.width + x], curses.color_pair(current_colors[y * self.width + x]))
                else:
                    self.screen.addstr(y, x, '█', curses.color_pair(235))

        self.feedback_timer -= 1
        if self.feedback_timer == 0:
            self.clear_feedback()
        self.screen.refresh()