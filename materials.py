import random

class Material:
    """
    Base class for mine construction materials
    """
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
    """
    An empty space!
    """
    def __init__(self):
        Material.__init__(self)
        self.char = '█'
        self.toughness = 0


class Dirt(Material):
    """
    Dirt. Easy to break through.
    """
    def __init__(self):
        Material.__init__(self)
        self.char = '█'
        dirt_colors = [95]
        self.color = dirt_colors[random.randint(0, len(dirt_colors) - 1)]
        self.toughness = 1


class Rock(Material):
    """
    Rock (or boulders). Hard to break through.
    """
    def __init__(self):
        Material.__init__(self)
        self.char = 'O'
        self.color = 60
        self.toughness = 10


class Lava(Material):
    """
    Lava. Nice and hot, and likes to flow around and fill
    empty space.
    """
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

                creature = self.mine.get_creature(x, y)
                if creature is not None:
                    creature.die()

        self.temperature -= 1
        if self.temperature < 100:
            self.mine.set_material(self.x, self.y, Rock())