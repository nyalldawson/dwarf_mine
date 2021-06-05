import curses
import argparse
from generator import MineGenerator
from utils import show_colors


def main(screen, args):
    curses.start_color()
    curses.use_default_colors()
    curses.curs_set(0)

    screen.nodelay(1)

    height, width = screen.getmaxyx()
    width = args.width or width * 3
    height = args.depth or height * 2

    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, 16)
    pad = curses.newpad(height,width)
    g = MineGenerator(width - 1, height - 1, args)
    m = g.build_mine(screen, pad)

    if args.lights:
        m.dark = False

    while True:
        m.action()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--show-colors", help="shows a grid of available colors", action="store_true")
    parser.add_argument("-l", "--lights", help="shows all grid cells, not just explored ones", action="store_true")
    parser.add_argument("--miners", help="how many miners to add", type=int)
    parser.add_argument("--kings", help="how many dwarf kings to add", type=int, default=1)
    parser.add_argument("--wizards", help="how many wizards to add", type=int)
    parser.add_argument("--snakes", help="how many snakes to add", type=int)
    parser.add_argument("--tribes", help="how many opposing dwarf tribes", type=int, default=2)
    parser.add_argument("--saboteurs", help="how many saboteurs to add", type=int)
    parser.add_argument("--width", help="mine width", type=int)
    parser.add_argument("--depth", help="mine depth", type=int)
    args = parser.parse_args()
    if args.show_colors:
        curses.wrapper(show_colors)
    else:
        curses.wrapper(main, args)
