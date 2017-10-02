import math
import curses

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

def show_colors(screen):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

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
