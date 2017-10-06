import random
import math


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

    def get_char(self):
        return self.char

    def touch_creature(self, creature):
        pass

    def placed_in_mine(self, mine, x, y):
        self.mine = mine
        self.x = x
        self.y = y
        creature = self.mine.get_creature(self.x, self.y)
        if creature is not None:
            self.touch_creature(creature)


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
    Rock. Hard to break through.
    """

    def __init__(self):
        Material.__init__(self)
        self.color = 60
        self.toughness = 5


class Boulder(Rock):
    """
    Boulders. Very hard to break through.
    """

    def __init__(self):
        Rock.__init__(self)
        self.char = 'O'
        self.toughness = 10


class IgneousRock(Rock):
    """
    Igneous rock. Volcanic byproduct with moderate strength.
    """

    def __init__(self):
        Rock.__init__(self)
        self.char = 'o'
        self.toughness = 5


class Fire(Material):
    """
    Fire. Ouch!
    """

    def __init__(self):
        Material.__init__(self)
        self.char = '*'
        fire_color = [10, 161, 125]
        self.color = fire_color[random.randint(0, len(fire_color) - 1)]
        self.temperature = random.randint(500, 1000)

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

                if isinstance(self.mine.material(x, y), (Water, Space)):
                    new = self.get_spread_material()
                    self.temperature *= 0.9
                    new.temperature = self.temperature
                    self.mine.set_material(x, y, new)
                material = self.mine.material(x, y)
                if isinstance(material, Lava):
                    t = self.temperature * 0.9999 + material.temperature * 0.0001
                    material.temperature = self.temperature * 0.0001 + material.temperature * 0.9999
                    self.temperature = t

        self.temperature -= 1
        if self.temperature < 100:
            self.mine.set_material(self.x, self.y, self.byproduct())

    def byproduct(self):
        return Space()

    def get_spread_material(self):
        return Fire()

    def touch_creature(self, creature):
        creature.die('was burnt by fire')


class Lava(Fire):

    """
    Lava. Nice and hot, and likes to flow around and fill
    empty space.
    """

    def __init__(self):
        Fire.__init__(self)
        self.char = '#'
        self.temperature = random.randint(2000, 100000)

    def byproduct(self):
        return IgneousRock()

    def get_spread_material(self):
        return Lava()

    def touch_creature(self, creature):
        creature.die('was burnt by lava')


class Water(Material):
    def __init__(self, capacity=100):
        Material.__init__(self)
        self.char = '█'
        self.color = 28
        self.capacity = capacity

    def get_char(self):
        # return self.char
        if self.capacity >= 99:
            return '█'
        elif self.capacity >= 87:
            return '▇'
        elif self.capacity >= 75:
            return '▆'
        elif self.capacity >= 62:
            return '▅'
        elif self.capacity >= 50:
            return '▄'
        elif self.capacity >= 37:
            return '▃'
        elif self.capacity >= 25:
            return '▂'
        else:
            return '▁'

    def action(self):
        # flow off bottom of mine
        if self.y == self.mine.height - 1:
            self.mine.set_material(self.x, self.y, Space())
            return

        # flow from cell above
        if self.y > 0 and isinstance(self.mine.material(self.x, self.y - 1), Water):
            other = self.mine.material(self.x, self.y - 1)
            if self.capacity < 100:
                new_capacity = self.capacity + other.capacity
                if new_capacity <= 100:
                    self.capacity = new_capacity
                    self.mine.set_material(self.x, self.y - 1, Space())
                else:
                    other.capacity = new_capacity - 100
                    self.capacity = 100

        # flow to cell below
        if self.y < self.mine.height - 1:
            other = self.mine.material(self.x, self.y + 1)
            if isinstance(other, Water):
                if other.capacity < 100:
                    new_capacity = other.capacity + self.capacity
                    if new_capacity <= 100:
                        other.capacity = new_capacity
                        self.mine.set_material(self.x, self.y, Space())
                        return
                    else:
                        self.capacity = new_capacity - 100
                        other.capacity = 100
            elif isinstance(other, Space):
                self.mine.set_material(self.x, self.y + 1, Water(self.capacity))
                self.mine.set_material(self.x, self.y, Space())
                return

        # diagonal flow
        if self.x > 0 and self.y < self.mine.height - 1:
            if self.mine.is_empty(self.x - 1, self.y + 1):
                self.mine.set_material(self.x - 1, self.y + 1, Water(self.capacity))
                self.mine.set_material(self.x, self.y, Space())
                return
            other = self.mine.material(self.x - 1, self.y + 1)
            if isinstance(other, Water) and other.capacity < 100:
                new_capacity = other.capacity + self.capacity
                if new_capacity <= 100:
                    other.capacity = new_capacity
                    self.mine.set_material(self.x, self.y, Space())
                else:
                    self.capacity = new_capacity - 100
                    other.capacity = 100
        if self.x < self.mine.width - 1 and self.y < self.mine.height - 1:
            if self.mine.is_empty(self.x + 1, self.y + 1):
                self.mine.set_material(self.x + 1, self.y + 1, Water(self.capacity))
                self.mine.set_material(self.x, self.y, Space())
                return
            other = self.mine.material(self.x + 1, self.y + 1)
            if isinstance(other, Water) and other.capacity < 100:
                new_capacity = other.capacity + self.capacity
                if new_capacity <= 100:
                    other.capacity = new_capacity
                    self.mine.set_material(self.x, self.y, Space())
                else:
                    self.capacity = new_capacity - 100
                    other.capacity = 100

        # flow to side
        if self.x > 0 and self.x < self.mine.width - 1:
            dir = -1 if random.randint(1, 2) == 1 else 1
            other = self.mine.material(self.x - dir, self.y)
            if isinstance(other, Water):
                if other.capacity < self.capacity:
                    other.capacity = math.floor((self.capacity + other.capacity) / 2.0)
                    self.capacity = other.capacity
            elif isinstance(other, Space):
                self.capacity = math.floor(self.capacity / 2)
                self.mine.set_material(self.x - dir, self.y, Water(self.capacity))

            other = self.mine.material(self.x + dir, self.y)
            if isinstance(other, Water) and other.capacity < self.capacity:
                other.capacity = math.floor((self.capacity + other.capacity) / 2.0)
                self.capacity = other.capacity
            elif isinstance(other, Space):
                self.capacity = math.floor(self.capacity / 2)
                self.mine.set_material(self.x + dir, self.y, Water(self.capacity))

        if self.capacity < 1:
            self.mine.set_material(self.x, self.y, Space())
            return

    def touch_creature(self, creature):
        if self.capacity > 70:
            creature.die('drowned')
