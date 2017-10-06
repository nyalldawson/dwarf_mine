import math
import curses

class Utils:
    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.ceil(math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1)))

    @staticmethod
    def exact_distance(x1, y1, x2, y2):
        return math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))

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


class Rect():

    def __init__(self,x1,y1,x2,y2):
        self.x1 = min(x1,x2)
        self.y1 = min(y1,y2)
        self.x2 = max(x1,x2)
        self.y2 = max(y1,y2)

    def center(self):
        return (math.floor((self.x1+self.x2)/2), math.floor((self.y1+self.y2)/2))

    def get_cells(self):
        cells = []
        for x in range(self.x1,self.x2+1):
            for y in range(self.y1, self.y2+1):
                cells.append((x,y))
        return cells

    def remove_invalid(self, mine):
        self.x1 = max(self.x1, 0)
        self.x2 = min(self.x2, mine.width -1 )
        self.y1 = max( self.y1, 0)
        self.y2 = min(self.y2,mine.height -1 )

    @staticmethod
    def from_center(x,y,width,height):
        return Rect(x-math.ceil(width / 2),y-math.floor(height/2), x+math.floor(width/2), y+math.ceil(height/2))

