import curses
from generator import MineGenerator


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

        g = MineGenerator(width - 1, height - 1)
        m = g.build_mine(screen)

        while True:
            m.action()


if __name__ == '__main__':
    curses.wrapper(main)
