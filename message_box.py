import math
import curses

class MessageBox:
    def __init__(self, screen, message):
        self.screen = screen
        lines = message.split('\n')

        message_width = max([len(l) for l in lines])
        message_height = len(lines)

        screen_height, screen_width = screen.getmaxyx()

        left = math.floor((screen_width - message_width) / 2)
        top = math.floor((screen_height - message_height) / 2)
        self.draw_box(left, top, message_width, message_height)

        self.draw_message(left, top, message_width, lines)

        self.screen.refresh()
        screen.getch()

    def draw_box(self, left, top, width, height):
        self.screen.addstr(top - 1, left - 1, '+' + ('-' * (width + 2)) + '+', curses.color_pair(215))
        for y in range(top, top + height + 2):
            self.screen.addstr(y, left - 1, '|' + (' ' * (width + 2)) + '|', curses.color_pair(215))
        self.screen.addstr(top + height + 2, left - 1, '+' + ('-' * (width + 2)) + '+', curses.color_pair(215))

    def draw_message(self, left, top, width, lines):
        for y, l in enumerate(lines):
            line_length = len(l)
            line_offset = math.floor((width - line_length) / 2)
            self.screen.addstr(top + 1 + y, left + 1 + line_offset, l, curses.color_pair(221))
