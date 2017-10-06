import curses
import argparse
from generator import MineGenerator
from utils import show_colors


def main(screen, args):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)
    screen.nodelay(1)

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, 16)

    height, width = screen.getmaxyx()

    g = MineGenerator(width - 1, height - 1, args)
    m = g.build_mine(screen)

    if args.lights:
        m.dark = False

    while True:
        m.action()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--show-colors", help="shows a grid of available colors", action="store_true")
    parser.add_argument("-l", "--lights", help="shows all grid cells, not just explored ones", action="store_true")
    parser.add_argument("--miners", help="how many miners to add", type=int)
    parser.add_argument("--wizards", help="how many wizards to add", type=int)
    args = parser.parse_args()
    if args.show_colors:
        curses.wrapper(show_colors)
    else:
        curses.wrapper(main, args)
